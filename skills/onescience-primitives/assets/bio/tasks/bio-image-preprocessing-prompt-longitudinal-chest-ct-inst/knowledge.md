# 实例任务：影像预处理与提示构建 @ B100

- domain: bio
- 骨架: bio-image-preprocessing-prompt-construction-task
- 场景: bio-longitudinal-chest-ct-change-detection-and-report-generation-scenario (B100)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B100
- 关联论文: ALTER: Modeling Longitudinal Changes via Regional Differencing for 3D CT Report Generation | doi:

## 本实例步骤描述
加载权重、规范化影像并建立临床问题或报告提示。

## 本实例执行 prompt
加载{CHECKPOINT}并规范化影像，用{CLINICAL_PROMPT}构建任务，限制输出为{MAX_TOKENS}个词元。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=alter_ct.pt
- {CLINICAL_PROMPT} | required=True | type=str | var_name=临床提示 | hint=填写具体临床任务问题 | default=描述主要影像发现并给出依据
- {MAX_TOKENS} | required=False | type=int | var_name=最大输出词元 | hint=限制生成内容长度 | default=512

## 本实例产出
- 模型输入影像
- 临床提示
- 预处理日志

## 本实例质量门禁
- 像素与方向信息正确
- 提示不含患者身份
- 权重版本可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
