# 实例任务：同协议检验与交付判定 @ E1

- domain: climate
- 骨架: tk-climate-b34e9a7a
- 场景: sc-07460df1 (E1)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
验证资料可用时按变量、层次、区域和时效计算确定性技巧，并与同条件基线比较。

## 本实例执行 prompt
若{VERIFICATION_REFERENCE}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并在同起报、同参考和同网格条件下比较{BENCHMARK_FORECAST}；同时检查频谱、预报活动度、异常极值和长滚动稳定性。资料或门限缺失时不得用论文结果替代本次验证。

## 本实例输入槽
- {VERIFICATION_REFERENCE} | required=False | type=str | var_name=独立验证资料 | hint=输入验证资料路径。 | default=None
- {BENCHMARK_FORECAST} | required=False | type=str | var_name=基线预报 | hint=输入基线预报路径。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {VALIDATION_PROTOCOL} | required=False | type=str | var_name=验证与验收协议 | hint=输入验收协议路径。 | default=None

## 本实例产出
- 分变量分层分区域分时效技能报告
- 同协议基线比较报告
- 频谱、活动度与稳定性诊断
- 质量判定与交付清单

## 本实例质量门禁
- 预报、基线和参考资料采用一致的起报时间、网格和面积权重
- 验证资料未参与本次模型输入或参数选择
- 指标按变量、层次、区域和时效分层报告
- 只有达到预先登记的验收门限才能判定性能PASS
- 验证资料或门限缺失时不作性能通过声明
- 配置、命令、退出码、日志、产物路径和文件哈希可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
