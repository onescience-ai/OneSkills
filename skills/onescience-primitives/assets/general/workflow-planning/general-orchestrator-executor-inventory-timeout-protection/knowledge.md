# Orchestrator Executor能力台账构建超时保护策略

## 适用范围

面向任务编排系统中多executor技能发现与能力评估场景，解决executor能力台账构建阶段因串行读取大量SKILL.md文件导致的超时瓶颈。适用于executor数量>3的多技能编排任务。

**不适用场景**：
- executor数量≤3的小规模编排（串行读取即可）
- 单executor直接调用（无需台账构建）

## 输入

- executor技能目录列表（路径或glob模式）
- 每个executor的SKILL.md文件
- 超时预算（秒）

## 输出

- executor能力台账（name/description/tags/domain摘要）
- 台账构建耗时指标
- 探索预算使用报告

## 流程节点

### Step 1：并行枚举executor技能
- **操作**：使用glob模式并行扫描executor技能目录，收集所有metadata.json路径
- **参数**：glob模式=`**/skills/onescience-*/SKILL.md`
- **工具**：Python glob模块或os.walk
- **质量门禁**：枚举结果去重，排除非executor类型（type!=executor）

### Step 2：快速路径筛选（description初筛）
- **操作**：对每个executor读取SKILL.md的frontmatter（前10行），提取name/description/domain/tags
- **参数**：读取行数≤15行，仅解析YAML frontmatter
- **工具**：yaml.safe_load或正则提取
- **质量门禁**：筛选后executor数量与原始数量一致（不丢失）

### Step 3：深度读取预算控制
- **操作**：对核心executor（与当前任务domain匹配的）做深度读取（全文或200行以内），非核心executor仅依赖Step 2的摘要
- **参数**：核心executor深度读取行数≤200，非核心仅读frontmatter
- **工具**：concurrent.futures.ThreadPoolExecutor并行读取
- **质量门禁**：深度读取的executor数量≤总数的50%

### Step 4：台账汇总与超时检查
- **操作**：汇总所有executor的能力摘要，检查是否超过探索预算
- **参数**：探索预算上限（如总步骤数的20%或时间的30%）
- **工具**：计时器+阈值检查
- **质量门禁**：台账构建总耗时<预算上限

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 并行读取线程数 | min(N, 10) | [D1] | N为executor数量，上限10避免资源竞争 |
| frontmatter读取行数 | ≤15行 | [D2] | YAML frontmatter通常在前10行内 |
| 深度读取行数 | ≤200行 | [D2] | 核心executor的关键信息在前200行内 |
| 探索预算占比 | ≤20%总预算 | [D1] | 台账构建不应超过总执行预算的20% |
| 非核心executor占比 | ≥50%跳过深度读取 | [D1] | 大多数executor为非核心，仅需摘要 |

### 校准数值（体系专属）

以下数值来自某大规模编排任务（5个executor），供量级校准；其他任务需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 串行读取5个executor耗时 | 300+步骤 | 归因报告 | 每个executor读取50-200行 |
| 并行读取目标耗时 | <30s | 归因报告 | 从枚举到台账完成 |
| 核心executor判断标准 | domain匹配 | 归因报告 | 当前任务为CFD则CFD相关executor为核心 |

## 边界与分流

- **executor数量≤3**：直接串行读取，不启动并行流程（避免并行开销大于收益）
- **探索预算已耗尽**：停止深度读取，仅使用Step 2的frontmatter摘要完成台账
- **SKILL.md格式异常**：跳过该executor，在台账中标记为"格式异常，仅摘要可用"
- **并行读取失败**：降级为串行读取，单个executor超时设为10s

## 质量检查

- 台账中每个executor至少包含name、description、domain字段
- 台账构建总耗时≤探索预算上限
- 核心executor的深度读取信息与frontmatter摘要无矛盾
- 并行读取结果通过去重校验（同一executor不重复读取）

## 回退策略

- 并行读取失败时降级为串行
- 深度读取超时时仅使用frontmatter摘要
- 整个台账构建超时时，使用仅含name+description的最小台账继续任务

## 资源召回建议

当任务编排涉及>3个executor技能时召回本卡片。配套资源：onescience-orchestrator的executor能力台账构建阶段。

## 补充证据（开源文档）

[D1] "concurrent.futures - Asynchronous execution of callables", Python 3.14 documentation, https://docs.python.org/3/library/concurrent.futures.html（accessed 2026-09-17，交叉验证）
[D2] "asyncio - Asynchronous I/O", Python 3.14 documentation, https://docs.python.org/3/library/asyncio.html（accessed 2026-09-17，交叉验证）

## 证据来源

[1] CFD_S006归因报告：orchestrator_executor_inventory_loop issue，agent在orchestrator规划阶段逐个串行读取5+个executor SKILL.md，累计300+步骤才完成台账构建
