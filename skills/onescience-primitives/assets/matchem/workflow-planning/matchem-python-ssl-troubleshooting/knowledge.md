# Python SSL证书配置和API调用故障诊断

## 适用范围
- **触发条件**：onescience-live-literature 或 onescience-knowledge-harvester 执行 API 调用失败时
- **适用场景**：Python脚本调用外部API（如OpenAlex、Europe PMC）时遇到SSL证书验证错误
- **不适用场景**：非SSL相关的网络问题、本地文件操作

## 输入
### 错误信息
```python
# 典型错误
SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1131)
URLError: <urlopen error [Errno 2] No such file or directory>
```

### 环境信息
| 参数 | 检查方法 |
|------|----------|
| Python版本 | `python --version` |
| 系统时间 | `date` 或 `datetime.now()` |
| 代理设置 | `echo $http_proxy $https_proxy` |
| 证书文件 | `ls /etc/ssl/certs/` |

## 输出
### 诊断报告
```yaml
diagnosis:
  error_type: "SSL证书验证失败"
  likely_causes:
    - "系统时间不准确"
    - "缺少根证书"
    - "代理服务器拦截"
    - "防火墙设置"
  confidence: 0.85
```

### 解决方案
```yaml
solutions:
  - method: "禁用SSL验证（临时）"
    command: "requests.get(url, verify=False)"
    risk: "安全风险，仅用于测试"
   适用场景: "快速验证问题"
  
  - method: "设置环境变量"
    command: "export PYTHONHTTPSVERIFY=0"
    risk: "影响所有HTTPS请求"
    适用场景: "开发环境"
  
  - method: "更新证书包"
    command: "pip install --upgrade certifi"
    risk: "低"
    适用场景: "生产环境"
```

## 流程节点
1. **错误捕获** → 捕获SSL相关异常
2. **环境检查** → 检查系统时间、证书、代理
3. **原因分析** → 根据错误信息判断原因
4. **方案选择** → 根据场景选择解决方案
5. **实施验证** → 执行解决方案并验证

## 关键参数
| 常见原因 | 检查方法 | 解决方案 |
|----------|----------|----------|
| 系统时间错误 | `date` 命令 | 校准时间 |
| 缺少根证书 | 检查证书目录 | 安装certifi |
| 代理拦截 | 检查环境变量 | 配置代理证书 |
| 防火墙 | 检查网络连接 | 配置白名单 |

## 边界与分流
### 决策树
```
SSL错误类型？
├─ CERTIFICATE_VERIFY_FAILED
│   ├─ 系统时间正确？ → 检查证书包
│   └─ 系统时间错误？ → 校准时间
├─ CONNECTION_REFUSED
│   ├─ 代理设置？ → 检查代理配置
│   └─ 无代理？ → 检查防火墙
└─ TIMEOUT
    ├─ 网络正常？ → 增加超时时间
    └─ 网络异常？ → 检查网络连接
```

### 降级策略
1. **首选方案失败** → 尝试备用方案
2. **所有方案失败** → 使用替代数据源（如webfetch）
3. **无法恢复** → 记录错误并继续其他任务

## 质量检查
- [ ] 错误信息已完整记录
- [ ] 环境信息已检查
- [ ] 解决方案已验证
- [ ] 任务已恢复执行

## 回退策略
1. SSL问题无法解决 → 使用webfetch替代API调用
2. 网络完全不通 → 使用本地缓存数据
3. 数据源不可用 → 标记任务为PARTIAL

## 资源召回建议
- **何时召回**：API调用失败时、SSL证书错误时
- **配套资源**：general-offline-scientific-computing-resource-access（离线资源获取策略）

## 证据来源
本知识卡片基于实践经验总结，无特定论文来源。
主要参考：
- Python官方文档：ssl模块
- Requests库文档：SSL Verification
- OpenAlex API文档：错误处理