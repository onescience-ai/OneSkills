# 骨架任务：数据与目标定义

- domain: matchem
- 复用场景数: 21
- 实例任务数: 21

## 步骤描述（跨场景聚合去重）
- 清洗数据并固定预测目标、单位和约束。

## 执行 prompt（跨场景聚合去重）
- 读取 {DATASET}，检查重复、缺失、泄漏、单位和数据许可；定义 {TARGET}，缺失关键标签时标记 BLOCKED。

## 输入槽（var/hint/default）
- {DATASET} | required=True | type=doc | var_name=训练与验证数据 | hint=包含样本来源、目标值、单位和许可信息。 | default=CSV/JSON/数据库导出
- {TARGET} | required=True | type=str | var_name=优化目标 | hint=明确目标性质、单位、方向和约束。 | default=目标材料性质

## 产出
- 数据审计报告
- 清洗数据表
- 目标定义

## 质量门禁 quality_gate
- 无未说明的数据泄漏
- 训练/验证/测试划分可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/perovskite-stability-benchmark-dataset
- datasets/xjtu-sy-rolling-bearing-accelerated-life-test-protocol-and-dataset
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/dataset-contract-auditor

## 实例任务（本骨架在各场景的实例化）
- matchem-data-objective-definition-b2-multi-principal-intermeta-inst
- matchem-data-objective-definition-co2-photocatalyst-data-inst
- matchem-data-objective-definition-half-heusler-thermoelectric-inst
- matchem-data-objective-definition-halide-perovskite-compatible-inst
- matchem-data-objective-definition-high-entropy-carbide-hardnes-inst
- matchem-data-objective-definition-high-entropy-ceramic-ml-inst
- matchem-data-objective-definition-high-entropy-solid-solution-inst
- matchem-data-objective-definition-lead-free-hybrid-perovskite-inst
- matchem-data-objective-definition-long-acting-injectable-inst
- matchem-data-objective-definition-mechanical-metamaterial-inst
- matchem-data-objective-definition-metallic-glass-machine-inst
- matchem-data-objective-definition-mof-mechanical-stability-inst
- matchem-data-objective-definition-mof-synthesis-multimodal-inst
- matchem-data-objective-definition-organic-semiconductor-inst
- matchem-data-objective-definition-perovskite-crystallization-inst
- matchem-data-objective-definition-perovskite-encapsulation-inst
- matchem-data-objective-definition-perovskite-temperature-inst
- matchem-data-objective-definition-porous-material-data-efficie-inst
- matchem-data-objective-definition-thermal-metamaterial-visible-inst
- matchem-data-objective-definition-thermally-stable-inorganic-inst
- matchem-data-objective-definition-vibration-stable-material-inst

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
