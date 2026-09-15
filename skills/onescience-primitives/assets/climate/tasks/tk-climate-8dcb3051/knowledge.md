# 骨架任务：生成格点海冰类别概率和集合分布

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成格点海冰类别概率和集合分布”，完成从历史海冰浓度、海气变量和季节信息到月尺度海冰概率场、冰缘和范围的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行生成格点海冰类别概率和集合分布，将历史海冰浓度、海气变量和季节信息转换为月尺度海冰概率场、冰缘和范围。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 产出
- 中间状态与运行日志
- 生成格点海冰类别概率和集合分布结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出在岸线、深水区和强梯度区无异常跳变
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-af264e77

## 复用场景
- E17
