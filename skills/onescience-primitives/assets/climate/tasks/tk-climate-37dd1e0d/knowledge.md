# 骨架任务：WRF偏差订正模型训练与产品生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 学习WRF预报与WRF-ERA5参考之间的偏差关系，生成与原产品同契约的订正预报。

## 执行 prompt（跨场景聚合去重）
- 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并冻结订正模型，对{TARGET_WRF_FORECAST}生成{OUTPUT_INTERVAL}间隔的订正预报和偏差场至{OUTPUT_DIRECTORY}，保留原始—订正产品对应关系、模型身份和日志。

## 输入槽（var/hint/default）
- {TARGET_WRF_FORECAST} | required=True | type=str | var_name=待订正WRF产品 | hint=输入待订正产品路径。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 产出
- WRF智能订正模型与权重
- 原始—订正产品索引、日志和产品清单
- 订正预报场和偏差场

## 质量门禁 quality_gate
- 极端和稀有样本未被静默剔除
- 模型和数据版本、训练配置及随机性可追溯
- 订正前后产品在变量、网格、时次和单位上可逐项对应
- 训练目标和推理输入不存在未来真值泄漏

## 可调资源（edge:resource，仅真实存在）
- datasets/ERA5

## 实例任务（本骨架在各场景的实例化）
- it-0acad4f1

## 复用场景
- E108
