# 骨架任务：预测组件与参数兼容性验证

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 加载所选预测组件的配置和参数文件，核验输入输出尺寸及成员采样接口并执行单次干运行。

## 执行 prompt（跨场景聚合去重）
- 加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，使用{RANDOM_SEED}执行单次成员干运行，并确认能够生成{ENSEMBLE_SIZE}个独立成员。报告代码、依赖、配置和权重版本；存在输入输出不兼容或随机接口失效时停止。

## 输入槽（var/hint/default）
- {MODEL_CHECKPOINT} | required=True | type=str | var_name=预测组件参数路径 | hint=输入模型权重文件路径。 | default=None
- {MODEL_CONFIG} | required=True | type=str | var_name=预测组件配置路径 | hint=输入模型配置文件路径。 | default=None
- {CHECKPOINT_SHA256} | required=False | type=str | var_name=权重SHA-256 | hint=输入权重SHA-256。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20
- {RANDOM_SEED} | required=False | type=str | var_name=随机种子 | hint=输入随机种子。 | default=None

## 产出
- 单成员干运行日志
- 模型与检查点身份报告
- 输入输出兼容性矩阵
- 集合采样配置

## 质量门禁 quality_gate
- 代码、配置、预处理参数和检查点属于兼容版本
- 单成员输出时空尺寸和值域正确
- 固定随机种子时结果可复现，不同成员具有可辨别差异
- 检查点SHA-256与登记值一致
- 集合规模对应的推理和存储资源已核算

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-e424cf51

## 复用场景
- E2
