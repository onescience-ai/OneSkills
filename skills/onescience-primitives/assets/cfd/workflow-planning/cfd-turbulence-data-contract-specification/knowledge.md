# 湍流数据集数据契约生成规范

## 适用范围
本规范适用于湍流场数据集（如直接数值模拟、大涡模拟数据）的标准化数据契约生成，旨在确保数据在采集、存储、共享和分析过程中的可追溯性、可验证性和互操作性。适用于需要生成 `data_contract.json`、`dataset_manifest.json` 和 `data_audit.md` 等核验文档的场景。不适用于非湍流流体数据或非结构化数据。

## 输入
- 湍流场原始数据文件（如 `.npy`、`.h5`、`.zarr` 格式）
- 数据采集元信息（模拟参数、网格分辨率、时间步长等）
- 领域标准参考（如 FAIR 原则、CFD 数据规范）

## 输出
- `data_contract.json`：定义数据变量、单位、坐标系、数据类型等
- `dataset_manifest.json`：列出数据集包含的所有文件、样本ID、数据来源
- `data_audit.md`：数据质量审计报告，包括完整性、一致性检查结果

## 流程节点
1. **变量定义** → 识别数据场中的物理量（速度、压力、涡量等），定义变量名、符号、物理意义
2. **单位与坐标系** → 确定每个变量的国际单位（SI），定义坐标系（笛卡尔、柱坐标等）和参考系
3. **数据类型与精度** → 指定每个变量的数据类型（float32、float64）和存储精度
4. **样本标识** → 为每个数据样本生成唯一ID，包含时间步、空间位置等信息
5. **数据来源记录** → 记录数据生成方法（DNS/LES）、模拟参数、数据处理历史
6. **契约生成** → 将上述信息整合为结构化 JSON 文件，并生成审计报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 变量命名 | 遵循领域惯例（如 `u`, `v`, `w` 表示速度分量） | 领域知识 | 确保一致性 |
| 单位系统 | 国际单位制（SI） | [D1] | 避免单位混淆 |
| 坐标系 | 笛卡尔坐标系（x, y, z） | 领域知识 | 湍流模拟常用 |
| 数据类型 | float32 或 float64 | 领域知识 | 平衡精度与存储 |
| 样本ID格式 | `{dataset}_{time}_{resolution}_{hash}` | 领域知识 | 唯一标识 |

## 边界与分流
- **数据格式不支持**：若原始数据为非标准格式，需先进行格式转换，再生成契约
- **变量信息缺失**：若缺少变量定义，需从数据文件头或模拟文档中提取，或使用默认命名
- **坐标系不明确**：需从数据生成代码或文档中推断，或假设为笛卡尔坐标系并标注不确定性

## 质量检查
- 验证 `data_contract.json` 包含所有必要字段（`input_fields`, `target_fields`, `units`, `coordinates`）
- 检查变量命名是否一致，单位是否符合 SI 标准
- 确保样本ID唯一，无重复
- 审计报告需包含数据完整性、一致性检查结果

## 回退策略
- 若无法自动生成数据契约，可手动创建模板并填充已知信息
- 若单位信息缺失，可参考领域标准单位或使用无量纲化表示
- 若坐标系不明确，可假设为笛卡尔坐标系并在审计报告中注明

## 资源召回建议
当任务涉及湍流数据预处理、数据核验、数据共享时，应召回本卡片。配套资源：`cfd-turbulence-data-split-manifest`（切分清单生成）、`cfd-turbulence-dataset-jhtdb-access`（JHTDB 数据获取）。

## 补充证据（开源文档/用户自有，可选）
[D1] FAIR Guiding Principles for scientific data management and stewardship, GO FAIR Foundation, 2016, URL: https://www.go-fair.org/fair-principles/（accessed_at: 2026-09-17，权威标准）

## 证据来源
[1] FAIR Guiding Principles for scientific data management and stewardship, Wilkinson et al., Scientific Data, 2016, DOI: 10.1038/sdata.2016.18