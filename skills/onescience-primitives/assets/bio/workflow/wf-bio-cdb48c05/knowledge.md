# 工作流：wf-bio-cdb48c05

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 单细胞数据与任务定义
- desc: 读取Geneformer与scGPT单细胞知识可解释性比较的表达、染色质或空间多组学数据。
- depend: []
- prompt: 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立Geneformer与scGPT单细胞知识可解释性比较任务。
- step_input:
  - {CELL_DATA} (required=True, type=doc, var_name=单细胞数据, hint=输入H5AD或表达矩阵, default=immune_atlas.h5ad)
  - {MODEL_NAME} (required=True, type=enum, var_name=单细胞模型, hint=选择场景使用的模型, default=Geneformer)
  - {DATA_LAYER} (required=False, type=str, var_name=表达数据层, hint=填写用于分析的数据层, default=counts)
- outputs: ['标准化AnnData', '特征与样本清单', '任务配置']
- quality_gate: ['细胞和基因标识唯一', '计数矩阵维度一致', '必要的元数据列存在']

### s02 预处理与模型表征
- desc: 加载权重并执行归一化、基因对齐和批次编码。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，按{BATCH_KEY}编码批次，并依据{NORMALIZE_COUNTS}处理计数后生成模型表征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=geneformer_v2)
  - {BATCH_KEY} (required=False, type=str, var_name=批次字段, hint=填写批次元数据列名, default=batch)
  - {NORMALIZE_COUNTS} (required=False, type=bool, var_name=归一化计数, hint=是否执行总量归一化, default=True)
- outputs: ['模型输入矩阵', '细胞表征', '预处理日志']
- quality_gate: ['基因词表已对齐', '批次标签无缺失', '输入数值均为有限值']

### s03 细胞状态推理与生成
- desc: 执行表征、注释、扰动预测或空间恢复任务。
- depend: ['s02']
- prompt: 运行Geneformer与scGPT单细胞知识可解释性比较，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- step_input:
  - {TARGET_GENES} (required=False, type=list[str], var_name=目标基因, hint=列出重点分析基因, default=['TP53', 'MYC', 'CD3D'])
  - {NUM_SAMPLES} (required=True, type=int, var_name=采样数量, hint=设置每条件采样细胞数, default=128)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定采样与评测结果, default=19)
- outputs: ['细胞级结果', '基因级结果', '推理日志']
- quality_gate: ['所有细胞有唯一结果', '输出基因顺序一致', '采样数量符合配置']

### s04 生物一致性与泛化评估
- desc: 计算概念纯度并检查细胞类型、通路和空间结构保持。
- depend: ['s03']
- prompt: 基于{LABEL_KEY}和{MIN_CORRELATION}评估概念纯度、差异表达及结构保持并汇总失败条件。
- step_input:
  - {MIN_CORRELATION} (required=False, type=float, var_name=相关性下限, hint=设置表达相关性下限, default=0.5)
  - {LABEL_KEY} (required=False, type=str, var_name=评测标签字段, hint=填写真实标签列名, default=cell_type)
- outputs: ['评测结果', '概念纯度明细', '生物一致性报告']
- quality_gate: ['训练测试样本隔离', '低质量细胞已标记', '结果保留原始细胞索引']

## 使用本工作流的场景（场景→工作流映射）
- B72
- B75
- B71
- B77
- B76
- B79
- B74
- B80
- B78
- B73
