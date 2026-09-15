# DeePMD 势函数训练 (deepmd-potential-training)

## 任务目标
使用 DeePMD-kit 完成机器学习原子势的全流程训练：从数据准备（dpdata 格式转换）、模型选择（se_e2_a / DPA3）、训练（dp train）、监控（lcurve.out）、冻结（dp freeze）、测试（dp test），到微调（fine-tune from pretrained）、Python 推理（DeepPot API）、数据精简（dpgen simplify）与作业提交（dpdisp-submit）。覆盖 PyTorch/TensorFlow 后端，支持单任务与多任务训练。

## 适用范围 / 不适用场景
适用：需要训练/微调 DeePMD 势函数的场景；从 DFT/MD 原始输出转换为 deepmd/npy 或 deepmd/hdf5 训练数据；使用预训练模型（DPA-3.1-3M、DPA-3.2-5M、DPA-3.3-1M）微调；dpgen simplify 数据精简迭代；Python 推理与模型偏差计算。
不适用：非 DeePMD 架构的势函数训练；路由层不编造环境激活命令、不猜测 conda/module 名称。

## 实体槽（Entity Slots）
- model_family: se_e2_a（DeepPot-SE 基线）/ DPA3（高精度/LAM）
- backend: pytorch / tensorflow / jax / paddle
- data_format: deepmd/npy / deepmd/hdf5 / deepmd/raw
- type_map: 元素类型列表（必须与数据和预训练模型一致）
- numb_steps: 训练总步数
- learning_rate: start_lr / stop_lr / decay_steps（exp 调度）
- loss: start_pref_e / limit_pref_e / start_pref_f / limit_pref_f / start_pref_v / limit_pref_v
- optimizer: AdamW（weight_decay）
- finetune_source: self-trained .pt / multi-task pretrained / built-in pretrained
- model_branch: 多任务模型分支选择
- trust_thresholds: model_devi_f_trust_lo / model_devi_f_trust_hi（dpgen simplify）

## 输入输出契约
输入：
- 训练数据：deepmd/npy 或 deepmd/hdf5 格式，含 type_map、training/validation systems 路径
- 原始数据（需转换）：VASP OUTCAR、LAMMPS dump 等，通过 dpdata CLI 转换
- input.json：模型架构、学习率、损失函数、优化器、训练参数
- 微调额外：预训练模型文件（.pt）、--use-pretrain-script、--model-branch
- dpgen simplify：param.json + machine.json

输出：
- lcurve.out：训练曲线（validation RMSE、loss、learning rate）
- model.ckpt.pt：检查点（可 --restart 恢复）
- model.pth：冻结模型（dp --pt freeze -o model.pth）
- dp test 结果：Energy RMSE、Force RMSE、Virial RMSE（eV / eV/Å）
- dpgen simplify 输出：精简后数据集与迭代日志

## 方法路线（可替换）
模型选择决策：
- se_e2_a：稳健基线，中小体系，兼容性优先，算力有限
- DPA3：高精度，多样/大规模数据集，LAM 训练，动态邻居选择，预训练变体

训练命令：
- PyTorch：`dp --pt train input.json`
- 恢复训练：`dp --pt train input.json --restart model.ckpt.pt`
- 微调：`dp --pt train input.json --finetune pretrained.pt --use-pretrain-script`
- 多任务微调：`dp --pt train multi_input.json --finetune multitask_pretrained.pt`
- 冻结：`dp --pt freeze -o model.pth`（多任务加 `--head downstream`）
- 测试：`dp --pt test -m model.pth -s /path/to/test_system -n 30`

数据转换（dpdata CLI）：
- `uvx dpdata OUTCAR -i vasp/outcar -O deepmd_data -o deepmd/raw`
- `uvx dpdata OUTCAR -i vasp/outcar -O deepmd_npy -o deepmd/npy`

数据精简（dpgen simplify）：
- `dpgen simplify param.json machine.json`

## 操作序列（Operations）
1. 确认环境：`dp --version`，确认后端（PyTorch 用 `dp --pt ...`）
2. 准备数据：原始输出通过 dpdata 转换为 deepmd/npy 或 deepmd/hdf5
3. 选择模型：根据数据规模/精度需求/算力选 se_e2_a 或 DPA3
4. 编写 input.json：type_map、数据路径、learning_rate、loss、optimizer、training（numb_steps、gradient_max_norm、disp_file、save_freq）
5. 训练：`dp --pt train input.json`
6. 监控：检查 lcurve.out 中 validation RMSE 下降、无 NaN、train/val 无发散
7. 冻结与测试：`dp --pt freeze -o model.pth` → `dp --pt test -m model.pth -s ... -n 30`
8. 微调（可选）：下载预训练模型 `dp pretrained download DPA-3.2-5M`，用 --finetune + --use-pretrain-script
9. 数据精简（可选）：构建 param.json + machine.json，运行 `dpgen simplify`
10. 提交（可选）：通过 dpdisp-submit 交接 HPC 执行

## 验证契约（Validations）
- type_map 一致性：必须与数据和预训练模型匹配
- lcurve.out 健康：validation RMSE 持续下降，无 NaN/exploding loss，train/val 无发散
- 微调元素子集：下游数据元素必须是预训练模型 type_map 的子集
- 学习率降低：微调 start_lr（如 1e-4）应小于从头训练（如 1e-3）
- dp test RMSE 报告：Energy RMSE/Natoms、Force RMSE、Virial RMSE 需汇报用户
- dpgen simplify 前置：`dpgen --version` 可用、JSON 语法合法、数据路径存在
- input.json 合法性：必须为有效 JSON
- 模型偏差计算：多模型只加载一次，避免内存泄漏

## 资源引用（Resources）
- 核心工具：DeePMD-kit（dp CLI，https://github.com/deepmodeling/deepmd-kit）
- 数据工具：dpdata（格式转换，50+ 格式支持）、dpdata-driver（System.predict 标注）、dpdata-minimizer（System.minimize 几何优化）
- 数据精简：DP-GEN simplify（https://github.com/deepmodeling/dpgen）
- 提交工具：dpdisp-submit（Shell/Slurm/PBS/LSF/Bohrium）
- 物种查询：search-species（pubchem/opsin/wikidata，获取 SMILES/formula/mass）
- 预训练模型：DPA-3.1-3M、DPA-3.2-5M、DPA-3.3-1M、DPA3-Omol-Large
- Python 推理：DeepPot API（deepmd.infer）、calc_model_devi

## 前后置任务（Task Graph）
无强制前后置。典型上游：DFT/MD 计算产出原始数据（VASP OUTCAR 等）供 dpdata 转换。典型下游：训练好的 model.pth 用于 LAMMPS MD 生产运行或 Python 推理。dpgen simplify 可迭代精简数据集后重新训练。

## 缺口与降级（Fallback / Gap）
- 模型选择不确定：收集数据格式/规模、精度目标、算力预算、部署后端，再推荐 se_e2_a 或 DPA3
- 数据非 deepmd 格式：用 dpdata CLI 转换（支持 VASP/LAMMPS/Gaussian/QE/CP2K 等 50+ 格式）
- 微调架构未知：使用 --use-pretrain-script 继承预训练模型架构，input.json 中 descriptor/fitting_net 留空
- 多任务模型分支不明：`dp --pt show model.pt model-branch` 列出可用分支
- NaN/exploding loss：检查学习率、gradient_max_norm、数据质量
- dpgen 环境不可用：验证 `dpgen --version`，不从未激活的 shell 启动 simplify
- 内外层环境边界：outer shell 有 dpgen，inner stage jobs 需在 machine.json 的 resources.source_list 中显式激活
- 预训练模型下载：`dp pretrained download <MODEL> --cache-dir <PATH>`
- 参数文档查询：`dp doc-train-input | grep -A 7 training/numb_steps`
