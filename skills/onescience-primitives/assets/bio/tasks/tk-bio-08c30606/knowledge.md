# 骨架任务：影像预处理与提示构建

- domain: bio
- 复用场景数: 3
- 实例任务数: 3

## 步骤描述（跨场景聚合去重）
- 加载权重、规范化影像并建立临床问题或报告提示。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}并规范化影像，用{CLINICAL_PROMPT}构建任务，限制输出为{MAX_TOKENS}个词元。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=alter_ct.pt
- {CLINICAL_PROMPT} | required=True | type=str | var_name=临床提示 | hint=填写具体临床任务问题 | default=描述主要影像发现并给出依据
- {MAX_TOKENS} | required=False | type=int | var_name=最大输出词元 | hint=限制生成内容长度 | default=512

## 产出
- 临床提示
- 模型输入影像
- 预处理日志

## 质量门禁 quality_gate
- 像素与方向信息正确
- 提示不含患者身份
- 权重版本可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1c29da63
- it-a7a49712
- it-f6464f4d

## 复用场景
- B99
- B98
- B100
