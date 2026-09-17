# OpenFold 组件消融与结构泛化评测工作流

## 适用范围

面向 OpenFold/AlphaFold2 风格蛋白质结构预测模型的组件消融实验与结构泛化能力评测。覆盖标准 4 步工作流（s01-s04）：输入校验、权重准备、模型推理、结果筛选。适用于评估模型各组件（Evoformer、Template Module、IPA 等）对预测精度的贡献，以及在不同蛋白家族上的泛化能力。

## 输入

- 目标蛋白质序列（FASTA 格式）
- 模型权重文件（.pt 或 .npz 格式）
- 序列比对数据（可选，可运行时生成）
- 模板数据库（MMCIF 格式）
- 消融方案配置（指定要消融的组件）

## 输出

- 预测结构（PDB 格式）
- TM-score / GDT-TS 评估指标
- 消融实验对比报告
- 组件贡献度分析

## 流程节点

### s01: 输入校验与链标识检查

操作：校验输入序列格式、链标识唯一性和任务设置

检查项：
- FASTA 格式正确性
- 序列字符合法性（ACDEFGHIKLMNPQRSTVWY + BXZUO）
- 链标识唯一性（A, B, C... 或自定义标识）
- 序列长度在模型支持范围内
- 模型支持的实体类型确认

工具：序列验证器（参考 `bio-protein-sequence-validation`）

参数：
- `--input_fasta_dir`: 输入 FASTA 目录
- `--template_mmcif_dir`: 模板目录（必须提供，即使无模板）

质量门禁：所有校验通过，生成标准化输入清单

### s02: 权重准备与版本验证

操作：下载/验证模型权重，确认版本和许可

权重类型：
| 权重文件 | 用途 | 许可 |
|----------|------|------|
| params_model_1.npz | AlphaFold 官方权重（有模板） | CC BY 4.0 |
| params_model_1_ptm.npz | AlphaFold 官方权重（有模板+ptm） | CC BY 4.0 |
| finetuning_ptm_2.pt | OpenFold 训练权重（默认推荐） | Apache 2.0 |
| finetuning_no templ_*.pt | OpenFold 无模板权重 | Apache 2.0 |

验证项：
- 权重文件完整性（checksum）
- 权重与配置预设匹配
- 许可条款确认

工具：下载脚本 + 校验和验证

参数：
- `--openfold_checkpoint_path`: OpenFold 权重路径
- `--jax_param_path`: AlphaFold 权重路径

质量门禁：权重版本可追溯，许可已确认

### s03: 模型推理

操作：运行消融实验的模型推理

配置预设（`--config_preset`）：
| 预设 | 模板 | ptm | 适用场景 |
|------|------|-----|----------|
| model_1 | ✓ | ✗ | 标准推理 |
| model_1_ptm | ✓ | ✓ | 需要 pTM 评分 |
| model_3 | ✗ | ✗ | 无模板推理 |
| model_3_ptm | ✗ | ✓ | 无模板+ptm |

消融选项：
- 禁用 Evoformer 某些层
- 禁用 Template Module
- 禁用 IPA (Invariant Point Attention)
- 调整 MSA 深度

工具：`run_pretrained_openfold.py`

参数：
- `--model_device "cuda:0"`: 指定 GPU
- `--config_preset model_1_ptm`: 配置预设
- `--use_deepspeed_inference`: 启用 DeepSpeed 加速
- `--long_sequence_inference`: 长序列优化

质量门禁：推理完成，无运行时错误

### s04: 结果筛选与评估

操作：筛选预测结果，计算评估指标

评估指标：
- **TM-score**: 结构相似性（0-1，>0.5 表示同折叠）
- **GDT-TS**: 全局距离测试（0-100）
- **lDDT**: 局部距离差异测试
- **pTM**: 预测的 TM-score 置信度

筛选标准：
- pTM > 0.5 表示高置信度预测
- 排除异常短/长的预测
- 按置信度排序

工具：结构比对工具（TM-align, US-align）

质量门禁：生成完整的评估报告

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 标准工作流步骤数 | 4 (s01-s04) | [D1] | 固定步骤顺序 |
| 默认权重 | finetuning_ptm_2.pt | [D1] | OpenFold 推荐 |
| 配置预设数 | 5 种 | [D1] | model_1-5 |
| 模板要求 | 必须提供目录 | [D1] | 即使无模板 |

### 校准数值

以下数值来自 OpenFold 实践，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| OpenFold vs AlphaFold 推理速度 | 最快 2x | [D1] | Ampere GPU |
| 长序列最大长度 | >4000 残基 | [D1] | 单卡 A100 |
| DeepSpeed 推理加速 | 2-3x | [D1] | 无额外显存 |
| DeepSpeed 显存降低 | 13x | [D1] | 峰值显存 |

## 边界与分流

- **前提 1**：输入校验通过 (s01) → 否则中止并报告格式错误
- **前提 2**：权重文件可访问且版本正确 (s02) → 否则尝试重新下载或使用替代权重
- **前提 3**：GPU 可用且显存充足 (s03) → 否则启用 CPU Offloading 或减少批量
- **前提 4**：评估指标可计算 (s04) → 否则仅输出结构文件

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| 输入校验 | 0 错误 | 修复格式问题 |
| 权重完整性 | checksum 匹配 | 重新下载 |
| 推理完成 | 无运行时错误 | 检查 GPU/内存 |
| 结果有效 | TM-score > 0 | 调整参数重试 |

## 回退策略

1. 输入格式错误 → 使用 `bio-protein-sequence-validation` 修复
2. 权重下载失败 → 尝试 HuggingFace 或 Google Drive 备用源
3. GPU 显存不足 → 启用 `--long_sequence_inference`
4. 推理超时 → 增加超时时间或减少批量大小

## 资源召回建议

- 当执行 OpenFold/AlphaFold2 相关任务时召回本卡
- 当需要设计消融实验方案时召回本卡
- 配套资源：
  - `bio-protein-sequence-validation`（输入验证）
  - `general-gpu-compute-requirements`（GPU 配置）
  - `general-scientific-computing-offline-installation`（环境安装）

## 补充证据

[D1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html (accessed_at, 官方文档)
[D2] OpenFold Installation Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Installation.html (accessed_at, 官方文档)
[D3] OpenFold GitHub Repository, aqlaboratory, 2024, URL: https://github.com/aqlaboratory/openfold (accessed_at, 官方仓库)

## 证据来源

[1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html
[2] OpenFold Installation Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Installation.html
[3] OpenFold GitHub Repository, aqlaboratory, 2024, URL: https://github.com/aqlaboratory/openfold
[4] OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization, Ahdritz et al., bioRxiv, 2022, DOI: 10.1101/2022.11.20.517210
