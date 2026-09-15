# 实例任务：训练易发性分类器 @ E76

- domain: climate
- 骨架: tk-climate-8a077b20
- 场景: sc-535f1fa2 (E76)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E76
- 关联论文: Investigating the Role of the Key Conditioning Factors in Flood Susceptibility Mapping Through Machine Learning Approaches | doi:

## 本实例步骤描述
按冻结配置执行“训练易发性分类器”，完成从DEM、河网、土地覆盖、土壤、历史洪水样点到洪水易发性概率图的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{SUSCEPTIBILITY_THRESHOLDS}、{UNCERTAINTY_CONFIG}执行训练易发性分类器，将DEM、河网、土地覆盖、土壤、历史洪水样点转换为洪水易发性概率图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=易发性制图配置 | hint=输入易发性制图配置。 | default=None
- {SUSCEPTIBILITY_THRESHOLDS} | required=True | type=str | var_name=易发性等级阈值 | hint=输入易发性等级阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 训练易发性分类器结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预警阈值在独立验证集上冻结后评估
- 输出是长期静态易发性而非某次洪水预警概率

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
