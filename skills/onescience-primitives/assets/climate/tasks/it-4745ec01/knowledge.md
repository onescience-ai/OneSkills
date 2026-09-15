# 实例任务：水文强迫和流域资料时空对齐与样本构造 @ E46

- domain: climate
- 骨架: tk-climate-8a3f6bde
- 场景: sc-9013f97f (E46)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E46
- 关联论文: Skillful subseasonal soil moisture drought forecasts with deep learning-dynamic models | doi:; A comprehensive study of deep learning for soil moisture prediction | doi:

## 本实例步骤描述
执行“水文强迫和流域资料时空对齐与样本构造”，统一初始土壤湿度、气象预报、陆面属性的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{TIME_RESOLUTION}、{SPATIAL_MAPPING}、{WARMUP_POLICY}、{MISSING_VALUE_POLICY}完成水文强迫和流域资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {TIME_RESOLUTION} | required=True | type=str | var_name=时间分辨率 | hint=输入时间分辨率。 | default=None
- {SPATIAL_MAPPING} | required=True | type=str | var_name=空间映射配置 | hint=输入流域空间映射配置。 | default=None
- {WARMUP_POLICY} | required=False | type=str | var_name=预热期规则 | hint=输入状态预热规则。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练验证按时间或流域隔离并防止未来泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
