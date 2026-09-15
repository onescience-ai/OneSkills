# 骨架任务：设计目标与约束定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 解析ProToken潜空间蛋白结构序列协同设计的目标结构、功能条件和设计范围。
- 解析全原子蛋白结构与序列联合生成的目标结构、功能条件和设计范围。
- 解析功能位点约束的蛋白骨架生成的目标结构、功能条件和设计范围。
- 解析反应条件驱动的从头酶设计的目标结构、功能条件和设计范围。
- 解析多功能基序支架蛋白生成的目标结构、功能条件和设计范围。
- 解析多构象状态兼容的蛋白序列设计的目标结构、功能条件和设计范围。
- 解析底物口袋约束的酶骨架设计的目标结构、功能条件和设计范围。
- 解析给定蛋白骨架的稳健序列设计的目标结构、功能条件和设计范围。
- 解析跨膜蛋白序列离散扩散设计的目标结构、功能条件和设计范围。
- 解析靶标特异性全原子肽类设计的目标结构、功能条件和设计范围。

## 执行 prompt（跨场景聚合去重）
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的ProToken潜空间蛋白结构序列协同设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的全原子蛋白结构与序列联合生成任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的功能位点约束的蛋白骨架生成任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的反应条件驱动的从头酶设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的多功能基序支架蛋白生成任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的多构象状态兼容的蛋白序列设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的底物口袋约束的酶骨架设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的给定蛋白骨架的稳健序列设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的跨膜蛋白序列离散扩散设计任务及可设计区域。
- 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的靶标特异性全原子肽类设计任务及可设计区域。

## 输入槽（var/hint/default）
- {DESIGN_INPUT} | required=True | type=doc | var_name=设计输入 | hint=输入结构或约束文件 | default=target_interface.pdb
- {MODEL_NAME} | required=True | type=enum | var_name=设计模型 | hint=选择场景使用的模型 | default=PepFlow
- {TARGET_LENGTH} | required=True | type=int | var_name=目标长度 | hint=设置目标残基数量 | default=256

## 产出
- 标准化设计输入
- 约束清单
- 设计区域

## 质量门禁 quality_gate
- 目标长度受模型支持
- 约束引用有效
- 设计区域无冲突

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn
- models/protoken
- models/rfdiffusion

## 实例任务（本骨架在各场景的实例化）
- it-2beb27de
- it-601f15a3
- it-6a78fb77
- it-84e192bc
- it-a816f71c
- it-bd99e94f
- it-c26d1513
- it-cb3ead0e
- it-d7c1b8bc
- it-e5eece42

## 复用场景
- B14
- B13
- B11
- B20
- B15
- B18
- B16
- B12
- B19
- B17
