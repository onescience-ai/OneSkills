# 材料化学领域 Profile

本文档用于辅助 `skills/onescience-primitives/SKILL.md` 处理材料化学（matchem）领域的知识检索与资源召回。它合并了材料化学领域的模型、工具、数据管线与工作流索引，但只提供语义线索和候选资源建议。
最终是否命中、返回哪些内容，仍以 `assets/matchem/**/metadata.json` 及对应资源文件为准。

## 使用原则

- 仅在 `detected_domain` 或调用方 `filters.domain` 明确指向材料化学领域时使用本文档；跨领域或领域不明时先按 `domain_profile.md` 完成领域判定。
- 本文档是召回提示，不是硬性规则。若用户请求、`metadata.json.description`、资源文件内容与本文档提示不一致，应优先相信实际资源证据。
- 单模型、单数据管线、单组件或单工具需求，优先直接在对应 category 下召回资源。
- 端到端、多步骤、需要任务分流或跨节点交接的需求，可结合 `workflow-planning` 资源与本文档的工作流提示进行召回。
- 不要虚构不存在的 primitive。若需要的工具或模型不在 `assets/matchem` 中，将其标记为外部依赖或资源缺口。

## 资源类型召回提示

- 需要模型推理、训练、微调或评估时，通常建议召回 `models` 下的 `model` primitive（MACE、UMA-ESCN-MD、UMA-ESCN-MoE、Matris、DeepMD）。
- 需要模型输入准备、数据标准、格式转换、dataset adapter 时，通常建议召回 `datapipes` 下的资源。
- 需要训练/测试数据集时，通常建议召回 `datasets` 下的资源（dp、dpa3、mace、matpl、matris、mattersim、oc20）。
- 需要实现细节、组件改造、调试、接口契约或模型内部结构时，通常建议召回 `components` 下的资源。
- 需要 HPC 计算软件使用知识（VASP、LAMMPS、CP2K、Gaussian、GROMACS、DeepMD-kit、DP-GEN 等）时，通常建议召回 `tools` 下的资源。
- 需要完整科研流程规划、节点依赖、质量检查和回退策略时，通常建议召回 `workflow-planning` 下的工作流资源。

## HPC 软件工具召回提示

| 用户需求或任务信号 | 建议优先考虑的资源 |
|---|---|
| 第一性原理计算、DFT 计算、电子结构、结构弛豫、能带/态密度、过渡态搜索、声子谱 | `vasp` |
| 分子动力学模拟、经典力场 MD、NPT/NVT 系综、in.lammps 配置 | `lammps` |
| DFT+MD 混合计算、大体系 DFT、CP2K input 文件编写 | `cp2k` |
| 量子化学计算、分子轨道、激发态、Gaussian 输入文件编写 | `gaussian` |
| 生物分子 MD、蛋白质/脂质/核酸模拟、GROMACS 拓扑和 mdp 参数 | `gromacs` |
| Deep Potential 模型训练、DeepMD 数据格式、LAMMPS 部署势函数 | `deepmd_kit` |
| 并发学习训练数据生成、主动学习、DP-GEN 参数配置 | `dpgen` |

### 工具选择决策树

```
用户需求涉及材料计算工具？
├── 第一性原理（DFT）
│   ├── 周期性体系（晶体、表面、界面） → VASP
│   ├── 大体系 DFT / DFT+MD 混合 → CP2K
│   └── 分子体系量子化学（激发态、NMR等） → Gaussian
├── 分子动力学（MD）
│   ├── 经典力场（材料体系） → LAMMPS
│   ├── 经典力场（生物/软物质体系） → GROMACS
│   └── 第一性原理 MD（AIMD） → VASP / CP2K
└── 机器学习势函数
    ├── 训练 MLIP 模型 → DeepMD-kit / MACE
    ├── 主动学习数据生成 → DP-GEN
    └── 部署到 MD → LAMMPS（MLIAP 接口）
```

## 模型资源边界

### MACE 模型
- `mace`：E(3)-等变消息传递 MLIP，更适合需要能量守恒的力、应力、virial 或下游 MD/结构弛豫任务。
- 小数据材料任务可使用 MACE-MP、MACE-MPA、MACE-OMAT 或本地 checkpoint 做 fine-tuning。
- LAMMPS 部署需注意 MLIAP 分支兼容性。

### UMA 模型族
- `uma_escn_md`：UMA-ESCN-MD 模型（Gaussian 距离展开），适用于材料体系的势函数训练与 MD 模拟。
- `uma_escn_moe`：UMA-ESCN-MoE 混合专家模型（Gaussian 距离展开），通过 MoE 架构提升多元素体系的表达能力。

### Matris 模型
- `matris`：Matris 材料势模型，适用于材料原子体系的能量/力预测任务。

### DeepMD 模型
- `deepmd`：Deep Potential 模型（DeepMD-kit 生态），基于 embedding net + fitting net 架构的 MLIP。
- 支持 se_e2_a、se_e3 等多种 descriptor 类型，可训练 energy/force/dipole/polarizability 等性质。
- 原生支持 LAMMPS 接口（`pair_style deepmd`）和 DP-GEN 并发学习框架。
- 使用场景：需要从 AIMD 数据训练 MLIP 进行大规模经典 MD 模拟。

### 模型选择建议

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 需要 E(3)-等变约束、高精度力预测 | MACE | 等变架构，能量守恒更严格 |
| 多元素体系、需要混合专家 | UMA-ESCN-MoE | MoE 提升多元素表达能力 |
| DeepMD 生态兼容、LAMMPS 原生部署 | DeepMD | 与 DP-GEN/DeepMD-kit 深度集成 |
| 通用材料势函数、快速原型 | Matris / MACE | 现有 checkpoint 丰富 |

## 数据集与数据管线匹配提示

| 用户需求或任务信号 | 建议优先考虑的资源 |
|---|---|
| DeepMD 格式训练数据 | `dp`（water + dpa3 微调 split）、`dpa3`（CH_3787 碳氢体系） |
| MACE 兼容训练数据 | `mace` 数据集 |
| Matris 兼容训练数据 | `matris` 数据集 |
| MatterSim 兼容训练数据 | `mattersim` 数据集 |
| OC20 催化剂数据 | `oc20` |
| MatPL/PWMLFF 材料势数据 | `matpl`（含 AuAg、Cu、HfO2、LiSiC 等体系） |
| 通用材料数据管线（AtomicData 格式） | `materials` datapipe |

## 常见工作流交叉索引

### MLIP 训练工作流
1. 数据准备：`datasets/dp` / `datasets/mace` / `datapipe/materials`
2. 模型选择：`models/mace` / `models/deepmd` / `models/uma_escn_md`
3. 训练执行：`tools/deepmd_kit` 或项目训练脚本
4. 部署验证：`tools/lammps`（MLIAP 接口）

### 第一性原理计算工作流
1. 计算准备：`tools/vasp`（INCAR/POSCAR/POTCAR/KPOINTS 配置）
2. 结构优化：ISIF=3, IBRION=2 弛豫
3. 性质计算：态密度/能带/光学性质等
4. 结果分析：数据管线或外部后处理工具（pymatgen、VASPKIT）

### DeepMD 并发学习工作流
1. 初始数据生成：`tools/vasp` / `tools/cp2k` AIMD 采样
2. 初始模型训练：`tools/deepmd_kit` 训练初始势函数
3. 并发学习迭代：`tools/dpgen` 主动学习探索构型空间
4. 模型部署：`tools/lammps`（`pair_style deepmd`）大规模 MD 模拟

## 检索质量检查

- 先确认请求已路由到 matchem 领域，再选择 category scope；不要直接做全局模糊搜索。
- 若用户明确请求某个 primitive 名称，优先检查该资源是否真实存在，并读取其 `metadata.json` 判断语义是否匹配。
- 若本文档建议多个候选资源，先用用户请求中的对象、输入数据、交付物和当前任务阶段缩小范围。
- 若命中模型类资源且需要规格或使用说明，按 `SKILL.md` 的规则继续检查依赖组件和相关 `components`。
- 若命中工具类资源（如 VASP、LAMMPS），应结合用户任务阶段判断是返回使用知识（`usage.md`）、规格知识（`spec.md`）还是工作流规划知识（`workflow_planning.md`）。
- `why_matched` 应说明用户需求与资源 `description`、category 或工作流语义之间的对应关系，避免只复述资源名。
- `limitations` 应来自资源文件中的约束、本文档边界提示或缺失文件说明；不确定时说明需要人工复核或外部依赖。
