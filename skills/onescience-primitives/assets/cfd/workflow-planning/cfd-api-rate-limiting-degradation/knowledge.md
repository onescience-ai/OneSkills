# API Rate Limiting and Degradation Strategy

## 适用范围

本卡片面向学术API速率限制与降级方案，提供OpenAlex/Europe PMC/Semantic Scholar等API的请求间隔要求、指数退避参数、429响应处理流程，以及多源检索优先级与降级规则。适用于知识检索、文献搜索、论文获取等场景，确保在API限流时仍能获取足够的领域知识。

## 输入

- 检索查询词（英文，2-4组）
- 目标论文数量
- API密钥（可选）
- 网络环境配置

## 输出

- 论文池（pool.json）：包含标题、作者、DOI、摘要等信息
- 检索状态报告：成功/失败/降级记录
- 降级日志：API切换记录与原因

## 流程节点

### 步骤1：API速率限制要求

**各API速率限制对比**：

| API | 请求间隔 | 每日上限 | 429响应码 | 来源 |
|-----|---------|---------|----------|------|
| OpenAlex | ≥1秒 | 100,000 | HTTP 429 | 官方文档 |
| Europe PMC | ≥0.5秒 | 无明确限制 | HTTP 429 | 官方文档 |
| Semantic Scholar | ≥1秒 | 100（无密钥）/ 1000（有密钥） | HTTP 429 | 官方文档 |

**推荐请求间隔**：所有API统一使用≥1秒间隔，确保兼容性 [报告CFD_S039证据]。

### 步骤2：指数退避策略

**标准指数退避参数**：

```python
def exponential_backoff(attempt, base_delay=1, max_delay=60):
    """
    指数退避计算
    
    Args:
        attempt: 当前重试次数（从0开始）
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
    
    Returns:
        延迟时间（秒）
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    # 添加随机抖动（0-1秒）防止雷群效应
    delay += random.uniform(0, 1)
    return delay
```

**退避阶段**：

| 阶段 | 延迟 | 重试次数 | 说明 |
|------|------|---------|------|
| 初始 | 1秒 | 1-2次 | 短暂网络波动 |
| 中期 | 2-8秒 | 3-5次 | API暂时限流 |
| 后期 | 16-60秒 | 6-8次 | 严重限流或服务降级 |
| 放弃 | >60秒 | >8次 | 切换到降级通道 |

**CFD_S039案例**：仅使用固定1秒延迟和30秒重试，未采用指数退避，导致连续429错误无法恢复 [报告证据]。

### 步骤3：429响应处理流程

**标准处理流程**：
```
1. 检测到429响应
2. 解析Retry-After头（如果存在）
3. 计算退避延迟
4. 等待延迟时间
5. 重试请求
6. 若重试次数超限，切换到降级通道
7. 记录降级日志
```

**实现代码示例**：
```python
import time
import requests

def api_request_with_retry(url, max_retries=8, base_delay=1):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 429:
                # 解析Retry-After头
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    delay = int(retry_after)
                else:
                    delay = min(base_delay * (2 ** attempt), 60)
                    delay += random.uniform(0, 1)
                print(f"Rate limited, waiting {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(min(base_delay * (2 ** attempt), 60))
    return None
```

### 步骤4：多源检索优先级与降级规则

**检索通道优先级**：
1. **OpenAlex**（主通道）：数据最全面，DOI解析准确
2. **Europe PMC**（第一降级）：免费OA全文，无需API密钥
3. **Semantic Scholar**（第二降级）：引用关系丰富，但有严格限流
4. **本地缓存**（最终降级）：已检索论文的本地存储

**降级触发条件**：

| 触发条件 | 降级目标 | 操作 |
|---------|---------|------|
| OpenAlex 429错误 | Europe PMC | 切换API端点 |
| Europe PMC 404/500 | Semantic Scholar | 切换API端点 |
| Semantic Scholar 429 | 本地缓存 | 使用缓存数据 |
| 所有API失败 | 本地缓存 | 检索终止，使用现有数据 |

**降级日志格式**：
```json
{
  "timestamp": "ISO datetime",
  "original_api": "openalex",
  "fallback_api": "europepmc",
  "reason": "HTTP 429 Too Many Requests",
  "attempt": 3,
  "delay_used": 8.5
}
```

### 步骤5：检索脚本模板

**OpenAlex检索脚本（lit_search.py）**：
```python
# 关键配置
- 请求间隔：1秒（硬编码）
- 超时时间：30秒
- 重试次数：3次（固定延迟）
- User-Agent: OneSkills-harvester/0.1
```

**Europe PMC降级脚本（search_europepmc.py）**：
```python
# 关键配置
- 请求间隔：0.5秒
- 超时时间：30秒
- 重试次数：2次
- User-Agent: OneSkills-harvester/0.1
```

**CFD_S039案例**：OpenAlex脚本未包含降级逻辑，429错误后直接失败，仅通过Europe PMC webfetch获取到部分结果 [报告证据]。

### 步骤6：检索结果质量控制

**去重策略**：
- 以DOI为主键（去除https://doi.org/前缀）
- DOI缺失时使用标题（小写化）作为备用键
- 每次检索后更新已见集合（seen set）

**质量检查点**：
1. 检索结果数量是否满足需求
2. 摘要完整性（前400字符）
3. DOI有效性验证
4. OA链接可用性检查

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 请求间隔 | ≥1秒 | [报告CFD_S039] | 防止429错误 |
| 退避基数 | 1秒 | 通用建议 | 指数退避起始值 |
| 退避上限 | 60秒 | 通用建议 | 防止无限等待 |
| 最大重试次数 | 8次 | 通用建议 | 超过后切换通道 |
| 超时时间 | 30秒 | 通用建议 | 防止长时间阻塞 |

### 校准数值（体系专属值）

以CFD_S039任务实测为例，以下数值供量级校准；其他任务需以自身证据重新锚定：

| 指标 | 实测值 | 推荐值 | 偏差 | 说明 |
|------|--------|--------|------|------|
| 重试次数 | 5次 | 8次 | -3 | 未达到放弃阈值 |
| 退避策略 | 固定30秒 | 指数1-60秒 | - | 未采用指数退避 |
| 降级通道数 | 1 | 4 | -3 | 仅使用Europe PMC |
| 检索成功率 | ~30% | >80% | -50% | 严重低于推荐值 |

## 边界与分流

### 异常处理

| 异常情况 | 处理方案 |
|---------|---------|
| 网络完全断开 | 使用本地缓存，记录断开时间 |
| API服务不可用 | 切换到下一个优先级通道 |
| API密钥失效 | 降级到无密钥限制的API |
| 检索结果为空 | 扩大查询词范围，尝试同义词 |

### 降级策略

1. **API限流**：使用指数退避重试，超限后切换通道
2. **网络故障**：使用本地缓存，记录故障时间
3. **数据缺失**：标注"检索失败"，不阻塞主流程
4. **质量不足**：扩大检索范围，增加查询词变体

## 质量检查

- [ ] 所有API请求间隔≥1秒
- [ ] 429响应正确处理（指数退避）
- [ ] 降级日志完整记录
- [ ] 检索结果去重有效
- [ ] 摘要完整性检查通过

## 回退策略

1. **完全失败**：记录失败原因，跳过本次检索
2. **部分成功**：使用已获取的结果，标注覆盖范围
3. **质量不足**：增加检索轮次，扩大查询词范围

## 资源召回建议

- 当任务涉及学术API检索且可能遇到限流时召回本卡
- 配套卡片：`cfd-bayesian-pinn-training-convergence`（知识应用）
- 当需要实时文献检索时，调用`onescience-live-literature`作为兜底通道

## 证据来源

[1] CFD_S039归因报告，知识检索事件分析，2026
[2] OpenAlex API官方文档（https://docs.openalex.org）
[3] Europe PMC API文档（https://www.ebi.ac.uk/europepmc/webservices/rest）
[4] Semantic Scholar API文档（https://api.semanticscholar.org/api-docs）
