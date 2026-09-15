# 工作流：wf-bio-468b46a3

- domain: bio
- 步骤数: 4
- 共用场景数: 3

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 医学数据与任务定义
- desc: 读取临床奖励对齐的胸部X线报告生成所需的去标识影像和临床文本。
- depend: []
- prompt: 读取{MEDICAL_INPUT}并核对去标识状态，使用{MODEL_NAME}建立{MODALITY}模态的临床奖励对齐的胸部X线报告生成任务。
- step_input:
  - {MEDICAL_INPUT} (required=True, type=doc, var_name=医学输入, hint=输入去标识医学数据, default=mimic_cxr_sample.jpg)
  - {MODEL_NAME} (required=True, type=enum, var_name=医学模型, hint=选择场景使用的模型, default=DobicVLM)
  - {MODALITY} (required=False, type=enum, var_name=影像模态, hint=选择医学影像模态, default=X-ray)
- outputs: ['去标识输入', '影像元数据', '任务配置']
- quality_gate: ['患者标识已移除', '影像序列可解析', '模态与模型兼容']

### s02 影像预处理与提示构建
- desc: 加载权重、规范化影像并建立临床问题或报告提示。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}并规范化影像，用{CLINICAL_PROMPT}构建任务，限制输出为{MAX_TOKENS}个词元。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=dobicvlm.ckpt)
  - {CLINICAL_PROMPT} (required=True, type=str, var_name=临床提示, hint=填写具体临床任务问题, default=描述主要影像发现并给出依据)
  - {MAX_TOKENS} (required=False, type=int, var_name=最大输出词元, hint=限制生成内容长度, default=512)
- outputs: ['模型输入影像', '临床提示', '预处理日志']
- quality_gate: ['像素与方向信息正确', '提示不含患者身份', '权重版本可追溯']

### s03 医学推理与一致性校订
- desc: 生成问答或报告并执行可选的事实一致性校订。
- depend: ['s02']
- prompt: 以温度{TEMPERATURE}和种子{SEED}运行临床奖励对齐的胸部X线报告生成，按{REVISION_PASS}决定是否执行二次事实校订。
- step_input:
  - {TEMPERATURE} (required=False, type=float, var_name=生成温度, hint=控制医学文本随机性, default=0.2)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定医学生成结果, default=7)
  - {REVISION_PASS} (required=False, type=bool, var_name=启用二次校订, hint=是否执行事实二次核对, default=True)
- outputs: ['医学回答或报告', '证据定位', '校订记录']
- quality_gate: ['输出无患者身份信息', '结论可定位到影像证据', '不确定性已明确表达']

### s04 临床质量与安全复核
- desc: 计算RadGraph-F1并检查事实、遗漏、矛盾和安全风险。
- depend: ['s03']
- prompt: 计算RadGraph-F1并与{MIN_CLINICAL_SCORE}比较；按{REQUIRE_REVIEW}标记医生复核后方可使用。
- step_input:
  - {MIN_CLINICAL_SCORE} (required=False, type=float, var_name=临床得分下限, hint=设置临床质量下限, default=0.7)
  - {REQUIRE_REVIEW} (required=False, type=bool, var_name=要求医生复核, hint=是否标记必须人工复核, default=True)
- outputs: ['临床质控报告', 'RadGraph-F1明细', '人工复核清单']
- quality_gate: ['无依据结论已标记', '关键异常遗漏已检查', '输出明确不是最终诊断']

## 使用本工作流的场景（场景→工作流映射）
- B99
- B98
- B100
