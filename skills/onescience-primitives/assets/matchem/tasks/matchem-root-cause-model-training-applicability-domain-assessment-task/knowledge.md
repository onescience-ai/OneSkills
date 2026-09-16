# 骨架任务：根源模型训练与适用域评估

- domain: matchem
- 复用场景数: 21
- 实例任务数: 21

## 步骤描述（跨场景聚合去重）
- 按记录的根源模型训练并评估泛化和适用域。

## 执行 prompt（跨场景聚合去重）
- 使用 {MODEL_CONFIG} 训练模型，保留随机种子、特征和版本；报告交叉验证、外部测试与适用域。

## 输入槽（var/hint/default）
- {MODEL_CONFIG} | required=True | type=object | var_name=模型配置 | hint=模型根源、版本、特征、随机种子和超参数必 | default={'model': '按论文或用户配置', 'seed': 42}

## 产出
- 性能指标
- 模型检查点
- 适用域报告

## 质量门禁 quality_gate
- 不能以训练误差替代泛化性能
- 外部测试与训练数据隔离

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-root-cause-model-training-b2-multi-principal-intermeta-inst
- matchem-root-cause-model-training-co2-photocatalyst-data-inst
- matchem-root-cause-model-training-half-heusler-thermoelectric-inst
- matchem-root-cause-model-training-halide-perovskite-compatible-inst
- matchem-root-cause-model-training-high-entropy-carbide-hardnes-inst
- matchem-root-cause-model-training-high-entropy-ceramic-ml-inst
- matchem-root-cause-model-training-high-entropy-solid-solution-inst
- matchem-root-cause-model-training-lead-free-hybrid-perovskite-inst
- matchem-root-cause-model-training-long-acting-injectable-inst
- matchem-root-cause-model-training-mechanical-metamaterial-inst
- matchem-root-cause-model-training-metallic-glass-machine-inst
- matchem-root-cause-model-training-mof-mechanical-stability-inst
- matchem-root-cause-model-training-mof-synthesis-multimodal-inst
- matchem-root-cause-model-training-organic-semiconductor-inst
- matchem-root-cause-model-training-perovskite-crystallization-inst
- matchem-root-cause-model-training-perovskite-encapsulation-inst
- matchem-root-cause-model-training-perovskite-temperature-inst
- matchem-root-cause-model-training-porous-material-data-efficie-inst
- matchem-root-cause-model-training-thermal-metamaterial-visible-inst
- matchem-root-cause-model-training-thermally-stable-inorganic-inst
- matchem-root-cause-model-training-vibration-stable-material-inst

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
