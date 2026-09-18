# CFD数据驱动建模工作流验证最佳实践

## 适用范围
面向CFD（计算流体动力学）数据驱动建模任务，提供从任务状态管理、数据预处理、模型验证到验收评估的全流程规范与最佳实践。适用于工程LES等效源项、高保真校准、湍流模型训练等CFD数据驱动场景，确保工作流的可重复性、可信度和鲁棒性。

## 输入
- CFD模拟数据（DNS/LES/RANS）
- 任务配置文件（JSON格式）
- 工作流脚本（Python）
- 计算资源清单（HPC/本地）

## 输出
- 工作流执行报告
- 模型验证结果
- 验收评估报告（PASS/REJECT/BLOCKED）
- 知识卡片（可被onescience-primitives召回）

## 流程节点
1. **任务状态管理** → 确保任务状态一致性，避免在BLOCKED状态下执行
2. **数据预处理** → 确保数据切分无泄漏，类型规范一致
3. **模型验证** → 验证模型可信度，包括验证、验证和不确定性量化
4. **验收评估** → 评估模型在目标应用中的适用性
5. **知识沉淀** → 将经验转化为可复用的知识卡片

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务状态检查 | 必须 | [论文1] | 任务状态为BLOCKED时必须跳过训练和评估步骤 |
| 数据类型校验 | 必须 | [论文1] | 数据加载后须显式转换为正确类型 |
| JSON完整性检查 | 必须 | [论文1] | 写入后必须验证JSON完整性 |
| 模型风险评估 | 必须 | [论文1] | 模型风险 = 模型影响力 × 决策后果 |
| 数据完整性 | ALCOA+框架 | [论文1] | Attributable, Legible, Contemporaneously recorded, Original, Accurate + Complete, Consistent, Enduring, Available |
| 验证验证 | V&V标准 | [论文1] | 验证（Verification）、验证（Validation）和不确定性量化（UQ） |

### 校准数值
以下数值来自CFD数据驱动建模任务，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差阈值 | <0.1 | [论文1] | 先验评估通过阈值 |
| 模型可信度等级 | 低/中/高 | [论文1] | 基于风险评估确定 |
| 验证比较器 | 体外/体内/真实世界数据 | [论文1] | 可接受的验证数据来源 |

## 边界与分流

### 关键前提不成立时的转向
1. **前提：任务状态为BLOCKED**
   - 不成立时转向：仅产出代码框架和接口规范，不执行训练和评估
   - 知识内容：BLOCKED状态下的降级策略应为仅产出代码产物清单，所有步骤产物标注NOT_EXECUTED

2. **前提：数据类型正确**
   - 不成立时转向：增加类型断言和转换逻辑
   - 知识内容：切分配置中group_by字段值必须为字符串类型，数据加载后须显式转换为str

3. **前提：JSON完整性**
   - 不成立时转向：增加try-except和schema校验
   - 知识内容：评估脚本应校验上游JSON schema符合性，缺失字段时使用默认值或标记BLOCKED

4. **前提：CFD求解器可用**
   - 不成立时转向：s04后验部分标记BLOCKED并跳过
   - 知识内容：后验耦合需要(1)可执行的CFD求解器二进制或Python绑定(2)网格/边界条件/物理模型配置文件(3)源项注入接口文档

5. **前提：HPC算力可用**
   - 不成立时转向：s04后验部分标记BLOCKED并跳过
   - 知识内容：后验CFD耦合需要足够的计算资源，若缺失则仅执行先验评估

## 质量检查
- 验证点：任务状态一致性、数据类型正确性、JSON完整性、模型可信度、数据完整性
- 阈值：相对L2误差<0.1、模型可信度等级≥中、数据完整性ALCOA+
- 失败处理：任何验证失败都必须产出verdict结论（PASS/REJECT/BLOCKED）

## 回退策略
- 任务状态为BLOCKED时：仅产出代码产物清单，不执行训练和评估
- 数据预处理失败时：检查数据类型并转换，重新执行预处理
- JSON序列化失败时：检查numpy标量类型并转换为Python原生类型
- CFD求解器缺失时：标记后验部分为BLOCKED，仅执行先验评估
- HPC算力不足时：标记后验部分为BLOCKED，仅执行先验评估

## 资源召回建议
- 何时应召回本卡片：CFD数据驱动建模任务的规划、执行和验收阶段
- 配套资源：onescience-primitives中的CFD工作流卡片、模型验证卡片、数据预处理卡片

## 补充证据（开源文档/用户自有，可选）
[D1] ASME V&V 40 Standard - Risk-Informed Credibility Assessment Framework, ASME, 2018, URL: https://www.asme.org/codes-standards/find-codes-standards/v-v-40-on-verifying-and-validating-in-silico-computational-models-in-medical-devices (accessed_at 2026-09-18, 交叉验证)

## 证据来源
[1] Horner M, Amar A, Frangi AF, et al. Ensuring the quality of in silico evidence: application to medical devices. Briefings in Bioinformatics, 2026, DOI: 10.1093/bib/bbag442
[2] Bridgeford EW, Campbell ID, Chen Z, et al. Twelve quick tips for AI-assisted coding in science. PLoS Computational Biology, 2026, DOI: 10.1371/journal.pcbi.1014428
[3] Ang MY, Lipovich L, Choo SW, et al. Trustworthy Agentic AI in Bioinformatics: From Workflow Automation to Traceable and Validated Biological Inference. Biology, 2026, DOI: 10.3390/biology15171537
[4] King RA, Abowd L, Broderick CW, et al. Ten simple rules for effective use of generative AI for code development in environmental science. PLoS Computational Biology, 2026, DOI: 10.1371/journal.pcbi.1014627