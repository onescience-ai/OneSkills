# 工作流：wf-bio-1964c994

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 RNA输入与任务定义
- desc: 读取RNA三维靶结构的群智能反向折叠所需的RNA序列、结构或配对样本。
- depend: []
- prompt: 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的RNA三维靶结构的群智能反向折叠任务。
- step_input:
  - {RNA_INPUT} (required=True, type=doc, var_name=RNA输入, hint=输入RNA序列或结构, default=rna_target.pdb)
  - {MODEL_NAME} (required=True, type=enum, var_name=RNA模型, hint=选择场景使用的模型, default=BeeRNA)
  - {TASK_MODE} (required=False, type=enum, var_name=RNA任务模式, hint=选择预测或设计模式, default=prediction)
- outputs: ['标准化RNA输入', '碱基与链映射', '任务配置']
- quality_gate: ['碱基字符合法', '配对索引无冲突', '模型与任务模式兼容']

### s02 结构约束与模型准备
- desc: 加载权重并编码二级、三级和固定序列约束。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，将序列限制在{MAX_LENGTH}以内，并按{ALLOW_PSEUDOKNOT}编码结构约束。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=beerna_config.json)
  - {MAX_LENGTH} (required=False, type=int, var_name=RNA长度上限, hint=限制RNA输入长度, default=512)
  - {ALLOW_PSEUDOKNOT} (required=False, type=bool, var_name=允许假结, hint=是否保留假结配对, default=False)
- outputs: ['RNA模型特征', '结构约束', '模型加载记录']
- quality_gate: ['序列长度符合要求', '结构约束可满足', '固定碱基未丢失']

### s03 结构预测或序列采样
- desc: 执行折叠、反向设计或复合物亲和力推理。
- depend: ['s02']
- prompt: 运行RNA三维靶结构的群智能反向折叠，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- step_input:
  - {NUM_CANDIDATES} (required=True, type=int, var_name=候选数量, hint=设置候选结构或序列数, default=100)
  - {TEMPERATURE} (required=False, type=float, var_name=采样温度, hint=控制RNA候选多样性, default=0.8)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=31)
- outputs: ['RNA候选', '模型得分', '推理日志']
- quality_gate: ['候选数量达标', '配对关系可解析', '输出与输入链一致']

### s04 RNA结构与功能质控
- desc: 计算结构恢复率并检查结构一致性、序列约束和候选多样性。
- depend: ['s03']
- prompt: 计算结构恢复率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- step_input:
  - {SCORE_THRESHOLD} (required=False, type=float, var_name=结果阈值, hint=设置合格结果阈值, default=0.6)
  - {OUTPUT_FORMAT} (required=False, type=enum, var_name=输出格式, hint=选择RNA结果格式, default=dot_bracket)
- outputs: ['排序候选', '结构恢复率汇总', 'RNA质控报告']
- quality_gate: ['结构格式可解析', '硬约束全部满足', '低质量候选已标记']

## 使用本工作流的场景（场景→工作流映射）
- B83
- B90
- B85
- B82
- B86
- B88
- B87
- B84
- B89
- B81
