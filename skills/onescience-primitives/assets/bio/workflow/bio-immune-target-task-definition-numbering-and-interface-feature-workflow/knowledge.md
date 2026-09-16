# 工作流：bio-immune-target-task-definition-numbering-and-interface-feature-workflow

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 免疫对象与任务定义
- desc: 读取CD4 T细胞表位加工与呈递预测所需的抗原、抗体或受体数据。
- depend: []
- prompt: 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的CD4 T细胞表位加工与呈递预测任务。
- step_input:
  - {IMMUNE_INPUT} (required=True, type=doc, var_name=免疫输入数据, hint=输入序列结构或配对表, default=viral_proteome.fasta)
  - {MODEL_NAME} (required=True, type=enum, var_name=免疫模型, hint=选择场景使用的模型, default=APLSuite)
  - {TASK_MODE} (required=False, type=enum, var_name=任务模式, hint=选择预测或设计任务, default=design)
- outputs: ['标准化免疫数据', '链与表位映射', '任务配置']
- quality_gate: ['链类型可识别', '样本标识唯一', '任务标签定义明确']

### s02 编号与界面特征准备
- desc: 加载权重并构建CDR、表位和界面条件特征。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，对{CDR_REGIONS}编号并限制单段长度为{MAX_CDR_LENGTH}，构建界面特征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=aplsuite.pt)
  - {CDR_REGIONS} (required=False, type=list[str], var_name=设计CDR区域, hint=选择参与任务的CDR, default=['H1', 'H2', 'H3'])
  - {MAX_CDR_LENGTH} (required=False, type=int, var_name=CDR长度上限, hint=限制单段CDR长度, default=30)
- outputs: ['标准抗体编号', 'CDR掩码', '抗原界面特征']
- quality_gate: ['CDR编号连续', '长度不超限', '抗原抗体链映射正确']

### s03 免疫预测或候选生成
- desc: 执行任务并产生可重复的得分或设计候选。
- depend: ['s02']
- prompt: 运行CD4 T细胞表位加工与呈递预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- step_input:
  - {NUM_CANDIDATES} (required=True, type=int, var_name=候选数量, hint=设置候选结果数量, default=50)
  - {TEMPERATURE} (required=False, type=float, var_name=采样温度, hint=控制候选序列多样性, default=0.3)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=73)
- outputs: ['候选序列或配对', '模型得分', '推理日志']
- quality_gate: ['候选数量达标', '序列字符合法', '得分与样本一一对应']

### s04 特异性与可开发性质控
- desc: 按表位AUPRC及序列、结构和特异性指标筛选结果。
- depend: ['s03']
- prompt: 计算表位AUPRC和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- step_input:
  - {SCORE_THRESHOLD} (required=False, type=float, var_name=得分阈值, hint=设置候选得分下限, default=0.7)
  - {TOP_K} (required=False, type=int, var_name=保留数量, hint=设置最终保留数量, default=20)
- outputs: ['排序候选', '表位AUPRC结果', '可开发性报告']
- quality_gate: ['关键CDR未异常截断', '低特异候选已标记', '保留规则可复现']

## 使用本工作流的场景（场景→工作流映射）
- B26
- B22
- B28
- B27
- B23
- B25
- B21
- B30
- B29
- B24
