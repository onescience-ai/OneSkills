# 气象预报数据时点规则严格执行规范

## 适用范围
适用于所有气象预报任务的数据时点规范，确保预报、预警或决策只能使用签发时已经可获得的观测、分析和已签发预报产品。覆盖不同类型数据（观测、分析、预报产品）的时点定义。

## 输入
- 输入数据（观测、分析、预报产品）
- 资料截止时间定义
- 数据时点检查配置
- 模拟数据使用限制配置

## 输出
- 资料截止时间验证记录
- 数据时点检查报告
- 事后分析数据排除记录
- 模拟数据使用限制记录

## 流程节点
1. 资料截止时间定义 → 2. 数据时点检查 → 3. 事后分析数据排除 → 4. 模拟数据使用限制 → 5. 验证记录生成

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 资料截止时间 | 观测签发时点 | [论文1] | 观测数据可被预报系统使用的最早时间 |
| 时点检查方法 | 观测时间<截止时间 | [论文2] | 验证每条输入数据的观测时间 |
| 事后分析数据 | 目标时刻之后形成 | [论文3] | 不得作为输入 |
| 模拟数据限制 | 仅用于方法验证 | [论文1] | 不得用于业务验收 |

## 边界与分流
- 资料截止时间不明确时：BLOCKED，需向数据提供方确认
- 数据时点规则违反时：BLOCKED，需重新获取合规数据
- 事后分析数据混入时：排除该数据并记录
- 模拟数据用于业务验收时：BLOCKED，需使用真实数据

## 质量检查
- 验证资料截止时间验证记录
- 检查数据时点检查报告
- 确认事后分析数据排除记录
- 验证模拟数据使用限制记录

## 回退策略
- 资料截止时间不明确：联系数据提供方获取签发时间
- 数据时点规则违反：重新获取合规时间范围内的数据
- 事后分析数据混入：排除该数据并重新获取
- 模拟数据用于业务验收：使用真实数据重新执行

## 资源召回建议
当执行气象预报任务的数据预检步骤时召回本卡片，配套资源包括资料截止时间定义工具、数据时点检查脚本和事后分析数据排除模板。

## 证据来源
[1] Short-term forecasting for Wind Speed based on machine learning using weather observation data, Hyeong-Se Jeong, Journal of the Korean Data And Information Science Society, 2020, DOI: 10.7465/jkdi.2020.31.5.823
[2] Data-driven decision analysis for weather observation technology in Japan: Integrating patent forecasting, network analytics, and economic valuation, Yong-Jae Lee, Decision Making and Analysis, 2025, DOI: 10.55976/dma.32025145386-100
[3] IoT-Driven Smart Weather Monitoring System with Global Data Access and Real-Time Visualization, Jayakrishnan x et al., International Journal of Science and Research, 2025, DOI: 10.21275/sr25417194734