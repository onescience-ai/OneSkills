# 骨架任务：成分与结构搜索空间定义

- domain: matchem
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 建立成分、压力和对称性约束。

## 执行 prompt（跨场景聚合去重）
- 根据 {COMPOSITION} 和 {STRUCTURE_CONSTRAINTS} 生成合法搜索空间；不明确的价态或压力边界标记 BLOCKED。

## 输入槽（var/hint/default）
- {COMPOSITION} | required=True | type=str | var_name=成分与化学计量 | hint=给出元素、比例、价态假设和电荷约束。 | default=目标化学式
- {STRUCTURE_CONSTRAINTS} | required=True | type=object | var_name=结构约束 | hint=空间群、压力、原子数、层状或配位约束。 | default={'pressure_GPa': 0, 'max_atoms': 64}

## 产出
- 初始构型
- 搜索空间清单

## 质量门禁 quality_gate
- 化学计量和电荷约束一致
- 结构约束可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1d2275db
- it-3bafb5df
- it-51cbb5d7
- it-a1ad7e61
- it-d25a8ba1
- it-f772625e

## 复用场景
- 图神经网络晶体结构预测与优化
- 有限温度晶体结构预测
- 钙钛矿氧化物与卤化物容忍因子稳定性筛选
- 钠酰胺条件晶体结构深度生成预测
- 高压晶体结构深度学习搜索
- 高居里温度二维铁磁材料高通量筛选
