# 骨架任务：约束候选生成与排序

- domain: matchem
- 复用场景数: 21
- 实例任务数: 21

## 步骤描述（跨场景聚合去重）
- 在定义的成分或工艺空间内生成候选并按目标排序。

## 执行 prompt（跨场景聚合去重）
- 在 {TARGET} 的约束内生成候选；同时报告预测值、不确定性和适用域标记。

## 输入槽（var/hint/default）
- {TARGET} | required=True | type=str | var_name=优化目标 | hint=明确目标性质、单位、方向和约束。 | default=目标材料性质

## 产出
- 候选排序
- 预测值与不确定性

## 质量门禁 quality_gate
- 所有候选满足硬约束
- 适用域外候选单独标识

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-constrained-candidate-b2-multi-principal-intermeta-inst
- matchem-constrained-candidate-co2-photocatalyst-data-inst
- matchem-constrained-candidate-half-heusler-thermoelectric-inst
- matchem-constrained-candidate-halide-perovskite-compatible-inst
- matchem-constrained-candidate-high-entropy-carbide-hardnes-inst
- matchem-constrained-candidate-high-entropy-ceramic-ml-inst
- matchem-constrained-candidate-high-entropy-solid-solution-inst
- matchem-constrained-candidate-lead-free-hybrid-perovskite-inst
- matchem-constrained-candidate-long-acting-injectable-inst
- matchem-constrained-candidate-mechanical-metamaterial-inst
- matchem-constrained-candidate-metallic-glass-machine-inst
- matchem-constrained-candidate-mof-mechanical-stability-inst
- matchem-constrained-candidate-mof-synthesis-multimodal-inst
- matchem-constrained-candidate-organic-semiconductor-inst
- matchem-constrained-candidate-perovskite-crystallization-inst
- matchem-constrained-candidate-perovskite-encapsulation-inst
- matchem-constrained-candidate-perovskite-temperature-inst
- matchem-constrained-candidate-porous-material-data-efficie-inst
- matchem-constrained-candidate-thermal-metamaterial-visible-inst
- matchem-constrained-candidate-thermally-stable-inorganic-inst
- matchem-constrained-candidate-vibration-stable-material-inst

## 复用场景
- B2多主元金属间化合物单相发现
- CO2光催化剂数据驱动可合成性筛选
- MOF合成应用多模态机器学习关联
- MOF结构力学稳定性机器学习预测
- 力学超材料目标响应逆向设计
- 半赫斯勒热电材料无监督发现
- 卤化物钙钛矿兼容分子数据驱动优化
- 多孔材料数据高效基础模型构建
- 振动稳定材料机器学习筛选
- 无铅杂化钙钛矿稳定性机器学习筛选
- 有机半导体主动学习发现
- 热稳定无机荧光粉主晶格机器学习筛选
- 热超材料可见红外兼容伪装逆向设计
- 金属玻璃机器学习成分筛选
- 钙钛矿封装层降解抑制机器学习筛选
- 钙钛矿温度稳定性机器人学习发现
- 钙钛矿结晶机器学习加速优化
- 长效注射聚合物配方机器学习优化
- 高熵固溶体形成机器学习预测
- 高熵碳化物硬度成分机器学习设计
- 高熵陶瓷机器学习发现
