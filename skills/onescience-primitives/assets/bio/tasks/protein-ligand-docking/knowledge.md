# 蛋白-配体分子对接 (protein-ligand-docking)

## 任务目标
预测小分子配体到蛋白靶点的三维结合姿势与模型置信度，服务基于结构的药物发现、虚拟筛选与先导优化。DiffDock/DiffDock-L 只输出 pose 与 confidence，不输出结合亲和力（ΔG、Kd）；亲和力必须与 GNINA、MM/GBSA 或 FEP/TI 联用。当前上游版本为 DiffDock v1.1.3，默认模型线在 `default_inference_args.yaml` 中指向 DiffDock-L。

## 适用范围 / 不适用场景
适用：100–1000 Da 类药小分子、<20 残基短肽、单链或多链蛋白；输入端可用 PDB 文件或氨基酸序列（走 ESMFold），配体端可用 SMILES、SDF、MOL2；覆盖单复合物对接、批量对接、集成对接与虚拟筛选。
不适用：蛋白-蛋白对接（改用 DiffDock-PP 或 AlphaFold-Multimer）、>20 残基大肽、共价对接、结合亲和力预测、膜蛋白（未专门训练，须谨慎使用）。

## 实体槽（Entity Slots）
- slot:protein_input:pdb 或 slot:protein_input:sequence（二选一，另一列在 CSV 中留空）
- slot:ligand_input:smiles / sdf / mol2（走 `--ligand_description`）
- slot:mode:single / batch / ensemble / screening
- slot:model:diffdock-l（默认）或 diffdock
- slot:samples_per_complex:10（默认）/ 20 / 40
- slot:device:cuda（强推，10–100× 加速）或 cpu

## 输入输出契约
输入：单对接传 `--protein_path` 或 `--protein_sequence` + `--ligand_description`；批量传 `--protein_ligand_csv`，CSV 必含列 `complex_name, protein_path, ligand_description, protein_sequence`。参数名坑：当前 `inference.py` 只注册 `--ligand_description`，部分旧 README 仍写 `--ligand`，除非本地 checkout 显式支持别名否则不要混用。
输出：`--out_dir/<complex_i>/rankN_confidence<x>.sdf`，默认 10 个采样姿势；`rank1.sdf` 是排名第一姿势的便捷副本。`analyze_results.py` 可再导出 summary CSV。首次运行会预计算 SO(2)/SO(3) 查找表（约 2–5 min），模型检查点约 500 MB 自动下载。

## 方法路线（可替换）
- 主路线：`python -m inference --config default_inference_args.yaml ...`，DiffDock-L 为默认。
- 大筛选（>100 化合物）：先 `python datasets/esm_embedding_preparation.py --protein_ligand_csv screening_input.csv --out_file protein_embeddings.pt`，再在推理时传 `--esm_embeddings_path`。
- 集成对接覆盖蛋白柔性：把多个构象 PDB 展开成 CSV（`conf1.pdb, conf2.pdb, conf3.pdb` 配同一配体），配合 `--samples_per_complex 20`。
- 亲和力重打分替代路线：DiffDock 产姿势 → 视觉检查 → GNINA `--score_only` 快扫 → AmberTools `MMPBSA.py` 或 `gmx_MMPBSA` 做 MM/GBSA（先能量最小化）→ OpenMM + OpenFE 或 GROMACS 做 FEP/TI（最准）。
- 参数预设：`assets/custom_inference_config.yaml` 内置 High Accuracy / Fast Screening / Flexible Ligands / Rigid Ligands 四套。

## 操作序列（Operations）
1. 环境自检：`python scripts/setup_check.py`（校验 Python 版本、PyTorch+CUDA、PyTorch Geometric、RDKit、ESM 等）。
2. 安装：`conda env create --file environment.yml; conda activate diffdock`，或 `docker pull rbgcsail/diffdock; docker run -it --gpus all --entrypoint /bin/bash rbgcsail/diffdock; micromamba activate diffdock`。
3. 批量前置：`python scripts/prepare_batch_csv.py --create --output batch_input.csv` 出模板；`python scripts/prepare_batch_csv.py my_input.csv --validate` 校验路径与 SMILES。
4. 推理：`python -m inference --config default_inference_args.yaml --protein_ligand_csv batch_input.csv --out_dir results/batch/ --batch_size 10`。
5. 分析：`python scripts/analyze_results.py results/batch/ --top 5 --threshold 0.0 --export summary.csv --best 20`。
6. 关键调参：`samples_per_complex` 默认 10，难例 20–40；`inference_steps` 默认 20，可增到 25–30；`temp_sampling_tor` 默认 7.04，柔性配体 8–10、刚性配体 5–6，越高姿势越多样。
7. 交互使用：`python app/main.py` → http://localhost:7860；无本地环境可用 https://huggingface.co/spaces/reginabarzilaygroup/DiffDock-Web。

## 验证契约（Validations）
- confidence 分级：>0 高（strong，可能准确）、-1.5 到 0 中（reasonable，需细验）、<-1.5 低（uncertain，必须外部验证）；`analyze_results.py --threshold 0.0` 按此过滤。
- confidence ≠ affinity：高置信只表示模型对结构确定，不代表结合强，最终排序须重打分。
- 上下文调期望：配体 >500 Da、多链蛋白、新蛋白家族均可能拉低置信度。
- 多采样看共识：至少审阅前 3–5 个 pose，一致性优于单帧判断。
- 结果合理性：视觉检查是否有非物理接触/穿模，蛋白需无缺失残基、远端水已去除。

## 资源引用（Resources）
- 脚本：`scripts/setup_check.py`、`scripts/prepare_batch_csv.py`、`scripts/analyze_results.py`。
- 参考文档：`references/parameters_reference.md`、`references/confidence_and_limitations.md`、`references/workflows_examples.md`。
- 资产：`assets/batch_template.csv`、`assets/custom_inference_config.yaml`。
- 推理入口：`inference.py`（模块调用 `python -m inference`），配置 `default_inference_args.yaml`；ESM 嵌入预算脚本 `datasets/esm_embedding_preparation.py`。
- 上游仓库 https://github.com/gcorso/DiffDock；引用 DiffDock-L: Corso et al. ICLR 2024, arXiv:2402.18396；原始 DiffDock: Corso et al. ICLR 2023, arXiv:2210.01776。

## 前后置任务（Task Graph）
无强制前后置。上游常见工作：蛋白结构准备（补缺失残基、去远端水、必要时指定结合位点）、配体 SMILES 规范化；下游常见工作：GNINA / MM-GBSA 亲和力重打分、FEP/TI 自由能计算、pose 视觉检查、生化实验验证。

## 缺口与降级（Fallback / Gap）
- 全线低 confidence：把 `samples_per_complex` 提到 20–40，改集成对接，回头验蛋白结构（补缺失残基）。
- OOM：降 `--batch_size 2` 或一次处理更少复合物。
- 慢：核 CUDA 是否可用 `python -c "import torch; print(torch.cuda.is_available())"`，切 GPU；同时启用 ESM 嵌入预算与批量。
- Pose 不合理：查蛋白缺失残基、去远端水、考虑显式指定结合位点。
- Module not found：回到 `setup_check.py` 诊断依赖或环境。
- 亲和力缺口：DiffDock 不产 ΔG/Kd，必须外接 GNINA `--score_only`、AmberTools MMPBSA.py / gmx_MMPBSA、或 OpenMM+OpenFE / GROMACS FEP/TI。
- 大体系缺口：蛋白-蛋白或大肽直接换 DiffDock-PP / AlphaFold-Multimer，别硬跑 DiffDock。
