# 骨架任务：弛豫与稳定性排序

- domain: matchem
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 对候选结构统一弛豫并计算稳定性指标。

## 执行 prompt（跨场景聚合去重）
- 按 {RELAX_CONFIG} 弛豫候选，比较能量、体积和稳定性；不同设置的结果不得直接排序。

## 输入槽（var/hint/default）
- {RELAX_CONFIG} | required=False | type=object | var_name=弛豫设置 | hint=如采用第一性原理计算，必须写明软件、泛函 | default={'method': 'user-confirmed'}

## 产出
- 弛豫结构
- 稳定性排序

## 质量门禁 quality_gate
- 参考态定义明确
- 收敛标准统一

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-relaxation-stability-ranking-finite-temperature-crystal-inst
- matchem-relaxation-stability-ranking-graph-neural-network-crystal-inst
- matchem-relaxation-stability-ranking-high-curie-temperature-2d-inst
- matchem-relaxation-stability-ranking-high-pressure-crystal-inst
- matchem-relaxation-stability-ranking-perovskite-oxide-and-halide-inst
- matchem-relaxation-stability-ranking-sodium-amide-conditional-inst

## 复用场景
- 图神经网络晶体结构预测与优化
- 有限温度晶体结构预测
- 钙钛矿氧化物与卤化物容忍因子稳定性筛选
- 钠酰胺条件晶体结构深度生成预测
- 高压晶体结构深度学习搜索
- 高居里温度二维铁磁材料高通量筛选
