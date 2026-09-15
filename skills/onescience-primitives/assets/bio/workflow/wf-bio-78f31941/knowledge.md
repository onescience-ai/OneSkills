# 工作流：wf-bio-78f31941

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 蛋白样本与目标定义
- desc: 读取低样本多模态蛋白功能预测的序列、结构或变异样本及目标标签。
- depend: []
- prompt: 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的低样本多模态蛋白功能预测任务。
- step_input:
  - {PROTEIN_DATA} (required=True, type=doc, var_name=蛋白任务数据, hint=输入序列结构或标签表, default=fewshot_functions.csv)
  - {MODEL_NAME} (required=True, type=enum, var_name=功能模型, hint=选择场景使用的模型, default=Multi-modal Protein Model)
  - {TARGET_TYPE} (required=False, type=enum, var_name=预测目标, hint=选择功能或效应目标, default=continuous)
- outputs: ['标准化样本', '标签字典', '数据检查报告']
- quality_gate: ['序列字符合法', '变异位点有效', '标签类型与目标一致']

### s02 表征与参考数据准备
- desc: 加载权重并构建序列、结构或底物联合表征。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}和{REFERENCE_DATA}，将序列裁剪或分块至{MAX_SEQUENCE_LENGTH}并生成联合表征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=multimodal_protein.pt)
  - {REFERENCE_DATA} (required=False, type=doc, var_name=参考数据, hint=参考数据集名称, default=UniProtKB_2025_01)
  - {MAX_SEQUENCE_LENGTH} (required=False, type=int, var_name=序列长度上限, hint=限制模型输入长度, default=1024)
- outputs: ['蛋白表征', '参考标签映射', '预处理日志']
- quality_gate: ['权重加载成功', '序列分块可回溯', '参考标签无重复冲突']

### s03 功能或效应推理
- desc: 批量输出功能类别、连续效应或检索分数。
- depend: ['s02']
- prompt: 以批次{BATCH_SIZE}和种子{SEED}运行低样本多模态蛋白功能预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- step_input:
  - {BATCH_SIZE} (required=True, type=int, var_name=批次大小, hint=设置单批处理样本数, default=32)
  - {DECISION_THRESHOLD} (required=False, type=float, var_name=判定阈值, hint=设置阳性判定阈值, default=0.5)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定评测随机过程, default=11)
- outputs: ['样本级预测', '模型分数', '推理日志']
- quality_gate: ['每个样本都有结果', '分数为有限值', '失败样本已记录']

### s04 评测与解释汇总
- desc: 计算宏平均F1并输出残基、结构域或样本层解释。
- depend: ['s03']
- prompt: 计算宏平均F1并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- step_input:
  - {MIN_METRIC} (required=False, type=float, var_name=指标下限, hint=设置合格指标下限, default=0.6)
  - {EXPORT_EXPLANATION} (required=False, type=bool, var_name=导出解释, hint=是否输出模型解释, default=True)
- outputs: ['评测汇总', '宏平均F1明细', '解释与误差报告']
- quality_gate: ['数据切分无泄漏', '指标定义明确', '解释可定位到原始样本']

## 使用本工作流的场景（场景→工作流映射）
- B39
- B32
- B38
- B37
- B31
- B34
- B35
- B36
- B40
- B33
