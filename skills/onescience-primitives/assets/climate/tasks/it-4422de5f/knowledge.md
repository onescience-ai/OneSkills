# 实例任务：对新预报生成残差订正 @ E53

- domain: climate
- 骨架: tk-climate-fadd0ae4
- 场景: sc-a5021c3d (E53)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E53
- 关联论文: A Deep Learning Method for Bias Correction of ECMWF 24–240 h Forecasts | doi:; ECMWF short-term prediction accuracy improvement by deep learning | doi:

## 本实例步骤描述
按冻结配置执行“对新预报生成残差订正”，完成从原始NWP预报、起报分析、历史验证资料到同网格多时效近地面变量订正场的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_INTERVAL}执行对新预报生成残差订正，将原始NWP预报、起报分析、历史验证资料转换为同网格多时效近地面变量订正场。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=生成成员数 | hint=输入生成成员数量。 | default=1
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 对新预报生成残差订正结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出均值、极端尾部和空间频谱均可检查

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
