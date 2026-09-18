# 学术API限流处理与重试策略

## 适用范围

面向学术API调用过程中的限流处理，提供HTTP 429错误的检测、指数退避重试策略、多API降级通道的实现方法。适用于文献检索、数据获取、知识采集等依赖外部API的工作流。

## 输入

- API类型：OpenAlex、Semantic Scholar、Google Scholar、arXiv
- 请求频率：当前QPS、历史调用模式
- 错误类型：HTTP 429 (Too Many Requests)、连接超时、服务不可用

## 输出

- 重试策略配置（初始延迟、退避因子、最大重试次数）
- 多API降级通道顺序
- 限流状态监控和预警

## 流程节点

1. **错误检测** → 捕获HTTP 429响应码，解析Retry-After头
2. **退避计算** → 指数退避：delay = base_delay × (2 ^ attempt) + jitter
3. **重试执行** → 按计算延迟等待后重试请求
4. **降级切换** → 重试耗尽后切换到备用API通道
5. **状态恢复** → API恢复后自动切回主通道

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 初始延迟 | 1-2秒 | [1] | 首次重试等待时间 |
| 退避因子 | 2.0 | [1] | 指数退避基数 |
| 最大重试次数 | 3-5次 | [1] | 超过则降级或终止 |
| 最大延迟上限 | 60秒 | [1] | 防止无限等待 |
| Jitter范围 | 0-1秒 | [1] | 随机化避免惊群效应 |

### 校准数值（学术API场景）

| API | 限流策略 | 推荐QPS | 降级通道 | 来源 |
|-----|----------|---------|----------|------|
| OpenAlex | 429 + Retry-After | ≤10 req/s | Semantic Scholar → arXiv | [文档] |
| Semantic Scholar | 429 + 指数退避 | ≤5 req/s | OpenAlex → arXiv | [文档] |
| Google Scholar | CAPTCHA + 临时封禁 | ≤1 req/s | Semantic Scholar → arXiv | 经验值 |
| arXiv API | 3秒间隔限制 | ≤0.3 req/s | Semantic Scholar → OpenAlex | [文档] |

## 边界与分流

- **单次限流**：自动重试（3次内）
- **持续限流**：切换到备用API通道
- **所有API限流**：暂停检索，等待冷却期（5-10分钟）
- **CAPTCHA验证**：终止自动检索，提示人工介入

## 质量检查

- 重试成功率监控
- API可用性健康检查
- 降级通道切换日志记录

## 回退策略

- 所有API不可用：使用本地缓存数据
- 降级通道也限流：延长等待时间或终止
- 数据不完整：标注"证据有限"，继续工作流

## 资源召回建议

- 实现文献检索或数据获取功能时召回本卡片
- 配套资源：cfd-multifidelity-aerodynamic-dataset（数据源）、cfd-workflow-fault-recovery（容错机制）

## 证据来源

[1] Application-layer Fault-Tolerance Protocols, De Florio, 2016, DOI: 10.48550/arXiv.1611.02273
[2] Scheduling and Checkpointing optimization algorithm for Byzantine fault tolerance in Cloud Clusters, Chinnathambi & Santhanam, 2018, DOI: 10.48550/arXiv.1802.00951

## 补充证据（开源文档）

[D1] OpenAlex API Documentation, OpenAlex, 2024, URL: https://docs.openalex.org/（accessed_at，官方文档）
[D2] Semantic Scholar API Documentation, Allen Institute for AI, 2024, URL: https://api.semanticscholar.org/api-docs/（accessed_at，官方文档）
