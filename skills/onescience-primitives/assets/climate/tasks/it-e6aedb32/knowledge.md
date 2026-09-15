# 实例任务：粗细分辨率资料时空对齐与样本构造 @ E15

- domain: climate
- 骨架: tk-climate-2bdb8d13
- 场景: sc-acf02f5d (E15)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E15
- 关联论文: Global spatio-temporal ERA5 precipitation downscaling to km and sub-hourly scale using generative AI | doi:; A precipitation downscaling method using a super-resolution deconvolution neural network with step orography | doi:; Customized deep learning for precipitation bias correction and downscaling | doi:

## 本实例步骤描述
执行“粗细分辨率资料时空对齐与样本构造”，统一粗网格小时降水、地形及可选环境场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{PAIRING_CONFIG}、{ACCUMULATION_POLICY}、{SPLIT_PROTOCOL}完成粗细分辨率资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {PAIRING_CONFIG} | required=True | type=str | var_name=粗细样本配对 | hint=输入粗细样本配对配置。 | default=None
- {ACCUMULATION_POLICY} | required=True | type=str | var_name=累计量转换规则 | hint=输入累计量转换规则。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时空划分协议。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练与验证时空块互斥并防止目标泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
