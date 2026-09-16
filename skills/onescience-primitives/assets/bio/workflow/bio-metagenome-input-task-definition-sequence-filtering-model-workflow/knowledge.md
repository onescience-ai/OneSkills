# 工作流：bio-metagenome-input-task-definition-sequence-filtering-model-workflow

- domain: bio
- 步骤数: 4
- 共用场景数: 7

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 宏基因组输入与任务定义
- desc: 读取DNA序列驱动的微生物致病性识别所需的序列、丰度或宿主标签。
- depend: []
- prompt: 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立DNA序列驱动的微生物致病性识别任务。
- step_input:
  - {METAGENOME_INPUT} (required=True, type=doc, var_name=宏基因组输入, hint=输入序列或特征表, default=microbial_genomes.fasta)
  - {MODEL_NAME} (required=True, type=enum, var_name=宏基因组模型, hint=选择场景使用的模型, default=PathoLM)
  - {SEQUENCE_TYPE} (required=False, type=enum, var_name=序列类型, hint=选择输入序列粒度, default=contig)
- outputs: ['标准化序列', '样本与标签表', '任务配置']
- quality_gate: ['序列字符合法', '样本来源可追溯', '标签定义无冲突']

### s02 序列过滤与模型准备
- desc: 加载权重并进行长度过滤、分词和参考信息编码。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}和{REFERENCE_DB}，过滤短于{MIN_CONTIG_LENGTH}的序列并生成模型特征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=patholm.pt)
  - {MIN_CONTIG_LENGTH} (required=False, type=int, var_name=最短序列长度, hint=设置最短序列碱基数, default=1000)
  - {REFERENCE_DB} (required=False, type=doc, var_name=参考数据库, hint=参考数据库名称, default=GTDB_R220)
- outputs: ['过滤后序列', '序列表征', '过滤统计']
- quality_gate: ['过滤阈值已记录', '参考版本可追溯', '序列与样本映射保持']

### s03 微生物预测与聚合
- desc: 批量完成分类、分箱、宿主关联或耐药性预测。
- depend: ['s02']
- prompt: 以批次{BATCH_SIZE}和种子{SEED}运行DNA序列驱动的微生物致病性识别，用{DECISION_THRESHOLD}输出序列及样本级结果。
- step_input:
  - {BATCH_SIZE} (required=True, type=int, var_name=批次大小, hint=设置序列批次大小, default=64)
  - {DECISION_THRESHOLD} (required=False, type=float, var_name=判定阈值, hint=设置阳性判定阈值, default=0.5)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定聚类或评测结果, default=29)
- outputs: ['序列级预测', '样本级汇总', '运行日志']
- quality_gate: ['每条序列有结果', '聚合规则可复现', '低置信结果未强制归类']

### s04 生态与分类质量评估
- desc: 计算AUROC并检查跨物种、样本和数据集泛化。
- depend: ['s03']
- prompt: 计算AUROC，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。
- step_input:
  - {MIN_CONFIDENCE} (required=False, type=float, var_name=置信度下限, hint=设置报告置信度下限, default=0.7)
  - {REPORT_UNKNOWN} (required=False, type=bool, var_name=报告未知类别, hint=是否保留未知类别结果, default=True)
- outputs: ['评测汇总', 'AUROC明细', '未知与异常清单']
- quality_gate: ['评测按样本隔离', '未知类别未被静默丢弃', '结果可回溯原序列']

## 使用本工作流的场景（场景→工作流映射）
- B95
- B93
- B91
- B96
- B92
- B94
- B97
