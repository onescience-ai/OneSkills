# 实例任务：分时效多阈值检验与交付判定 @ E2

- domain: climate
- 骨架: tk-climate-9b451aae
- 场景: sc-16d509a7 (E2)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E2
- 关联论文: Skilful nowcasting of extreme precipitation with NowcastNet | doi:; Skilful precipitation nowcasting using deep generative models of radar | doi:; Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting | doi:; RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting | doi:

## 本实例步骤描述
未来雷达资料可用时，对位置、结构、极端雨强和概率可靠性开展分时效验证。

## 本实例执行 prompt
若{VERIFICATION_RADAR}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并与相同起报时间和输入截止时间的{BASELINE_NOWCASTS}比较。分别报告普通样本、强降水样本和不同提前量，不得把重要性抽样结果外推为全年总体表现。资料或门限缺失时不得判定性能PASS。

## 本实例输入槽
- {VERIFICATION_RADAR} | required=False | type=str | var_name=未来验证雷达资料 | hint=输入未来雷达资料路径。 | default=None
- {BASELINE_NOWCASTS} | required=False | type=str | var_name=基线临近预报 | hint=输入基线预报路径。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {VALIDATION_PROTOCOL} | required=False | type=str | var_name=验证与验收协议 | hint=输入验收协议路径。 | default=None

## 本实例产出
- 分时效分阈值分尺度技能报告
- 概率可靠性与集合离散度报告
- 同协议基线比较报告
- 强降水与普通样本分层结果
- 质量判定与交付清单

## 本实例质量门禁
- 预报、基线和验证雷达采用一致的网格、掩膜、单位和有效时刻
- 验证资料未参与模型输入、训练或概率校准
- 确定性、空间结构和概率指标均按提前量分层报告
- 重要性抽样与连续时段验证结果分别报告
- 只有达到预先登记的验收门限才能判定性能PASS
- 验证资料或门限缺失时不作性能通过声明
- 配置、命令、退出码、日志、产物路径和文件哈希可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
