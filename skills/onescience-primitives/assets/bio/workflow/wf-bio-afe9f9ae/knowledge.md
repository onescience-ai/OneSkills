# 工作流：wf-bio-afe9f9ae

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 基因组输入与坐标规范化
- desc: 读取DNA语言模型生物任务基准评测的DNA、区间、变异或表观信号。
- depend: []
- prompt: 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立DNA语言模型生物任务基准评测任务。
- step_input:
  - {GENOMICS_INPUT} (required=True, type=doc, var_name=基因组输入, hint=输入序列区间或变异, default=BEND_tasks)
  - {MODEL_NAME} (required=True, type=enum, var_name=基因组模型, hint=选择场景使用的模型, default=DNABERT-2)
  - {REFERENCE_GENOME} (required=False, type=enum, var_name=参考基因组, hint=选择坐标参考版本, default=hg38)
- outputs: ['标准化基因组输入', '坐标检查报告', '任务配置']
- quality_gate: ['坐标位于参考范围', '等位基因方向一致', '样本标识唯一']

### s02 序列窗口与模型准备
- desc: 加载权重并构造满足上下文长度的正反链输入。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，按{CONTEXT_LENGTH}构造序列窗口，并按{REVERSE_COMPLEMENT}生成方向增强特征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=dnabert2.bin)
  - {CONTEXT_LENGTH} (required=False, type=int, var_name=上下文长度, hint=设置DNA窗口碱基数, default=131072)
  - {REVERSE_COMPLEMENT} (required=False, type=bool, var_name=反向互补增强, hint=是否加入反向互补序列, default=True)
- outputs: ['序列窗口', '方向映射', '模型加载记录']
- quality_gate: ['窗口长度符合模型要求', '中心坐标未偏移', '反向映射可恢复']

### s03 基因组预测或序列生成
- desc: 批量执行轨迹、分类、变异评分或条件生成。
- depend: ['s02']
- prompt: 以批次{BATCH_SIZE}和种子{SEED}运行DNA语言模型生物任务基准评测，分别输出{CELL_CONTEXTS}上下文的结果。
- step_input:
  - {BATCH_SIZE} (required=True, type=int, var_name=批次大小, hint=设置序列批次大小, default=8)
  - {CELL_CONTEXTS} (required=False, type=list[str], var_name=细胞上下文, hint=选择组织或细胞类型, default=['K562', 'HepG2'])
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定生成或评测结果, default=2025)
- outputs: ['基因组预测', '变异或生成分数', '运行日志']
- quality_gate: ['每个区间均有结果', '正反链结果已对齐', '数值无NaN或Inf']

### s04 轨迹与效应质量评估
- desc: 计算综合排名并导出区间、碱基或变异层结果。
- depend: ['s03']
- prompt: 计算综合排名，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- step_input:
  - {SCORE_THRESHOLD} (required=False, type=float, var_name=结果阈值, hint=设置显著结果阈值, default=0.5)
  - {OUTPUT_LEVEL} (required=False, type=enum, var_name=输出粒度, hint=选择结果输出粒度, default=variant)
- outputs: ['结果表', '综合排名汇总', '基因组质控报告']
- quality_gate: ['参考与替代等位可区分', '输出坐标未越界', '指标与数据切分匹配']

## 使用本工作流的场景（场景→工作流映射）
- B65
- B70
- B64
- B66
- B63
- B69
- B62
- B68
- B67
- B61
