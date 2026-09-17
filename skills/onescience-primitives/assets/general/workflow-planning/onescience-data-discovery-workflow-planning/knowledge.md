# OneScience 数据发现与工作流规划通用知识

## 适用范围

面向 OneScience 工作空间中的科研任务，需要在工作空间中定位输入数据文件、利用 workflow planning primitive 指导工作流步骤规划、并将 primitive 的 metadata 信息映射为数据来源线索和参数配置。

**触发条件**：
- 代理接收科研任务后需要在工作空间中搜索输入数据文件
- 代理需要利用 workflow planning primitive 的内容指导工作流步骤规划
- 代理需要从 primitive 的 metadata（source_papers、tags、tier）推断数据来源
- 代理需要将 primitive 的 workflow_nodes 映射为标准步骤结构

**适用场景**：
- 任务验证阶段发现输入文件缺失，需要扩展搜索范围
- 工作流规划阶段需要对齐标准4步结构（s01-s04）
- 需要从 primitive 的 source_papers DOI 获取示例数据
- 需要从 primitive 的 parameters 获取默认配置

**不适用场景**：
- 已知输入文件完整路径的简单文件读取
- 不涉及 OneScience primitives 系统的独立科研脚本
- 已有明确数据规范文档的成熟项目

## 输入

| 输入项 | 说明 |
|--------|------|
| 任务上下文 | 任务ID、任务目标、相关产物路径 |
| workflow planning primitive | 从 onescience-primitives 检索到的工作流规划原语 |
| 工作空间根目录 | 当前项目的根路径 |
| 任务产物目录 | results/task-artifact/{task_id} |

## 输出

| 输出项 | 说明 |
|--------|------|
| 数据发现日志 | 记录搜索路径、优先级、命中结果 |
| 对齐后的工作流步骤规划 | 与标准4步结构对齐的 global_plan |
| primitive 内容解析结果 | 提取的数据来源、步骤结构、参数配置 |

## 流程节点

### Step 1：数据文件多路径搜索

在工作空间中按优先级搜索输入数据文件：

**优先级顺序**：
1. **任务产物目录**（最高优先级）：`results/task-artifact/{task_id}/`
2. **工作空间根目录**：项目根路径下的直接文件
3. **.onescience/data/ 子目录**：OneScience 标准数据存放位置
4. **模型注册表**：通过 ModelScope 或数据注册表获取

**搜索操作**：
- 对每个路径执行文件存在性检查（Test-Path / os.path.exists）
- 记录每个路径的搜索结果到数据发现日志
- 若在高优先级路径找到文件，记录并停止搜索

**质量门禁**：
- 搜索覆盖所有标准路径
- 每个路径的搜索结果已记录
- 找到的文件格式和版本已验证

### Step 2：Primitive 内容解析

解析 workflow planning primitive 的 metadata 和 content，提取关键信息：

**从 metadata 提取**：
- `source_papers`：论文 DOI 列表，可用于定位示例数据（如论文 2607.20057）
- `tags`：工具和模型标识，指导参数配置
- `tier`：质量等级，影响决策置信度
- `scenario_id`：场景标识，关联场景需求书

**从 content 提取**：
- `workflow_nodes`：标准步骤结构（通常为4个节点）
- `typed parameters`：每步的输入输出参数及默认值
- `dependencies`：步骤间的依赖关系
- `quality gates`：每步的质量门禁

**操作指令**：`解析{PRIMITIVE}的metadata和content，提取数据来源线索（source_papers）、标准步骤结构（workflow_nodes）、参数配置（parameters）和依赖关系（dependencies）。`

**质量门禁**：
- source_papers 中的 DOI 已解析为可访问的 URL
- workflow_nodes 数量和顺序已确认
- 每步的输入输出参数已列出
- 依赖关系链已验证无环

### Step 3：数据来源映射

将 primitive 的 source_papers 映射为数据来源线索：

**映射规则**：
- 若 source_papers 包含论文 DOI，可通过 DOI 查询论文中的示例数据
- 若 primitive 的 tags 包含模型名称，可通过模型名搜索关联数据集
- 若 primitive 的 description 中提到默认输入文件名，以此为线索搜索

**回退策略**：
- DOI 查询失败时，使用论文标题在 OpenAlex/Semantic Scholar 搜索
- 模型名搜索无结果时，检查 .onescience/data/ 目录下的数据集

**质量门禁**：
- 每个数据来源线索已记录到数据发现日志
- 回退路径已执行（若有需要）

### Step 4：工作流步骤对齐

将任务的工作流规划与标准4步结构对齐：

**标准4步结构**：
- **s01 输入验证**：验证输入文件、参数、模型版本，执行数据标准化
- **s02 特征准备**：加载权重，构建特征（如 CDR、表位、界面条件特征）
- **s03 推理执行**：执行模型推理，生成候选结果
- **s04 评估筛选**：评估性能指标，筛选结果，生成报告

**对齐操作**：
- 检查代理规划的步骤是否与 s01-s04 对齐
- 将代理的通用步骤（如"任务理解""数据验证"）映射到标准节点
- 确保每步的输入输出契约与 primitive 的 typed parameters 一致

**质量门禁**：
- 规划步骤数与标准节点数一致（通常为4）
- 每步的输入参数来自上一步的输出
- 每步的质量门禁已定义

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据文件搜索路径数 | ≥4 | [D1] | 任务产物目录、根目录、.onescience/data/、模型注册表 |
| 标准工作流步骤数 | 4 | [D1][D2] | s01 输入验证 → s02 特征准备 → s03 推理执行 → s04 评估筛选 |
| Primitive metadata 关键字段 | source_papers, tags, tier, scenario_id | [D1] | 用于推断数据来源和参数配置 |
| Primitive content 关键章节 | workflow_nodes, parameters, dependencies, quality_gates | [D1] | 用于对齐工作流步骤 |

### 校准数值（以下数值来自已有任务，供量级校准；其他任务需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 抗体设计任务标准输入 | antigen_antibody_set.json | [D1] | s01 默认输入文件 |
| 抗体设计任务标准权重 | asafm.ckpt | [D1] | s02 默认权重文件 |
| 候选数量默认值 | 50 | [D1] | s03 默认生成候选数 |
| 采样温度默认值 | 0.3 | [D1] | s03 默认采样温度 |
| 随机种子默认值 | 73 | [D1] | s03 默认随机种子 |
| 得分阈值默认值 | 0.7 | [D1] | s04 默认筛选阈值 |
| 保留数量默认值 | 20 | [D1] | s04 默认保留候选数 |

## 边界与分流

**数据文件搜索失败时的改道方案族**：
- 若在所有标准路径均未找到输入文件 → 记录 BLOCKED 状态，等待用户提供文件或通过数据标准化工具备份数据
- 若找到文件但格式不匹配 → 调用 onescience-data-standardizer 执行格式转换
- 若文件存在但版本不兼容 → 检查 primitive 的 tier 标签确认适用版本范围

**Primitive 内容解析失败时的改道方案族**：
- 若 primitive 的 source_papers 为空 → 跳过论文数据映射，直接在工作空间搜索
- 若 primitive 的 workflow_nodes 不完整 → 按标准4步结构补全缺失步骤
- 若 primitive 的 parameters 缺少默认值 → 使用领域通用默认值并标注为 proposed_candidate(待确认)

**工作流步骤对齐失败时的改道方案族**：
- 若代理规划的步骤数与标准不符 → 以标准4步结构为准重新规划
- 若步骤间的依赖关系断裂 → 检查 primitive 的 dependencies 字段修复连接

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 数据发现日志完整性 | 覆盖全部标准搜索路径 | 补充缺失路径的搜索结果 |
| Primitive metadata 解析率 | 100% 关键字段已提取 | 标注缺失字段并降级处理 |
| 工作流步骤对齐率 | 100% 步骤与标准节点对应 | 重新映射步骤到标准节点 |
| 数据来源线索数 | ≥1 条有效线索 | 记录无数据来源状态 |

## 回退策略

1. **数据搜索全失败** → 使用原始任务的默认输入文件名作为占位符，标记 BLOCKED
2. **Primitive 解析失败** → 使用标准4步结构模板，不依赖 primitive 内容
3. **DOI 查询离线** → 使用 primitive 的 tags 作为关键词搜索本地数据
4. **标准步骤不适用** → 记录偏差原因，保留代理的非标准规划但标注 legacy_instance: true

## 资源召回建议

- 当任务在数据验证阶段发现输入文件缺失时召回本卡片
- 当任务在规划阶段需要对齐标准工作流步骤时召回本卡片
- 当需要从 primitive 的 source_papers 定位数据来源时召回本卡片
- 配套资源：
  - 具体任务的 workflow-planning 卡片（如 antigen-specific-multimodal-antibody-design）
  - onescience-data-standardizer（数据格式转换）
  - onescience-data-profile（数据处理规划）
  - onescience-live-literature（在线文献兜底）

## 补充证据（权威文档）

[D1] OneScience Primitives SKILL.md - 原语资源召回技能文档，onescience-ai 官方 GitHub 组织，main 分支，accessed 2026-09-16。交叉验证：该文档详细描述了 primitives 的目录结构（assets/<domain>/<category>/<primitive>/）、metadata.json 格式（9字段+tags边契约）、workflow-planning 卡片的 content_request 处理规则、以及 resource_retrieval_request → resource_retrieval_result 的完整闭环。

[D2] OneScience-doc 基于OneScience的科学智能代码开发教程-V4，onescience-ai 官方 GitHub 组织，V4 版本，accessed 2026-09-16。单源参考：该教程描述了 OneScience 的安装流程（conda 环境创建、pip install onescience[all]）、SCNet 远程计算资源配置、以及基于 oneskills 的自然语言编程工作流。

[D3] OneScience 主仓库 README，onescience-ai 官方 GitHub 组织，main 分支，accessed 2026-09-16。交叉验证：该文档描述了 OneScience 的领域覆盖（地球科学、生命信息、计算流体、工业仿真、材料化学）、数据集信息（ERA5、TJWeather、PDB、UniRef 等）、模型列表（Pangu、FourCastNet、Xihe、AlphaFold3 等）以及安装使用流程。

## 证据来源

[D1] OneScience Primitives SKILL.md, onescience-ai, GitHub, 2026, URL: https://github.com/onescience-ai/OneScience
[D2] OneScience-doc 科学智能代码开发教程-V4, onescience-ai, GitHub, 2026, URL: https://github.com/onescience-ai/OneScience-doc
[D3] OneScience 主仓库 README, onescience-ai, GitHub, 2026, URL: https://github.com/onescience-ai/OneScience
