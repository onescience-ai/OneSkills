# 实例任务：估计单木或样地森林结构及碳储量 @ E59

- domain: climate
- 骨架: climate-individual-tree-plot-forest-structure-carbon-stock-task
- 场景: climate-uav-lidar-image-forest-structure-carbon-stock-estimation-scenario (E59)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E59
- 关联论文: Estimating Forest Structure from UAV-Mounted LiDAR Point Cloud Using Machine Learning | doi:; Drones and machine learning for estimating forest carbon storage | doi:

## 本实例步骤描述
按冻结配置执行“估计单木或样地森林结构及碳储量”，完成从无人机点云或RGB影像、样地清查和异速生长关系到森林结构参数及碳储量图的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行估计单木或样地森林结构及碳储量，将无人机点云或RGB影像、样地清查和异速生长关系转换为森林结构参数及碳储量图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 估计单木或样地森林结构及碳储量结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出坐标、分辨率、无效值和置信信息完整

## 可调资源（edge:resource，仅真实存在）
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
