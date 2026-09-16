# 骨架任务：候选结构生成与去重

- domain: matchem
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 生成多样候选构型并去除等价结构。

## 执行 prompt（跨场景聚合去重）
- 在 {STRUCTURE_CONSTRAINTS} 内生成并去重候选，保留生成器、种子和对称性信息。

## 输入槽（var/hint/default）
- {STRUCTURE_CONSTRAINTS} | required=True | type=object | var_name=结构约束 | hint=空间群、压力、原子数、层状或配位约束。 | default={'pressure_GPa': 0, 'max_atoms': 64}

## 产出
- 候选结构库
- 去重日志

## 质量门禁 quality_gate
- 无原子重叠
- 等价结构不重复计数

## 可调资源（edge:resource，仅真实存在）
- models/strain-tuning-method-for-hbn-quantum-emitters
- tools/molecular-structure-preparation

## 实例任务（本骨架在各场景的实例化）
- matchem-candidate-structure-generation-finite-temperature-crystal-inst
- matchem-candidate-structure-generation-graph-neural-network-crystal-inst
- matchem-candidate-structure-generation-high-curie-temperature-2d-inst
- matchem-candidate-structure-generation-high-pressure-crystal-inst
- matchem-candidate-structure-generation-perovskite-oxide-and-halide-inst
- matchem-candidate-structure-generation-sodium-amide-conditional-inst

## 复用场景
- 图神经网络晶体结构预测与优化
- 有限温度晶体结构预测
- 钙钛矿氧化物与卤化物容忍因子稳定性筛选
- 钠酰胺条件晶体结构深度生成预测
- 高压晶体结构深度学习搜索
- 高居里温度二维铁磁材料高通量筛选
