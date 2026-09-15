# 骨架任务：雷达质控与模型输入构造

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行缺测掩膜、异常值处理、网格统一、雨强变换和历史序列堆叠，形成模型输入。

## 执行 prompt（跨场景聚合去重）
- 依据{PREPROCESS_CONFIG}和{RADAR_GRID_SPEC}处理通过预检的雷达序列，应用{MISSING_VALUE_POLICY}，统一投影、网格、单位和值域，生成按时间堆叠的输入张量和有效区掩膜。不得将缺测编码为零降水。

## 输入槽（var/hint/default）
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=雷达预处理配置 | hint=输入预处理配置路径。 | default=None
- {RADAR_GRID_SPEC} | required=True | type=str | var_name=雷达网格规格 | hint=输入投影、分辨率和网格范围。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理策略 | hint=输入掩膜或拒绝策略。 | default=None

## 产出
- 有效区与缺测掩膜
- 标准化雷达历史张量
- 雷达预处理转换清单

## 质量门禁 quality_gate
- 时间维、空间维、投影、单位和通道顺序与模型输入契约一致
- 缺测区与无降水区能够区分
- 裁剪和重采样没有引入时间错位
- 输入张量不存在未解释的NaN、Inf或异常负值

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-5ed7a724

## 复用场景
- E2
