# 工作流：bio-input-and-task-definition-feature-model-preparation-structure-workflow

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 输入与任务定义
- desc: 校验OpenFold组件消融与结构泛化评测所需的序列、链组成和任务设置。
- depend: []
- prompt: 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立OpenFold组件消融与结构泛化评测任务。
- step_input:
  - {INPUT_DATA} (required=True, type=doc, var_name=序列或结构输入, hint=输入FASTA或结构文件, default=CAMEO_targets.fasta)
  - {MODEL_NAME} (required=True, type=enum, var_name=结构模型, hint=选择场景使用的模型, default=OpenFold)
  - {CHAIN_MODE} (required=False, type=enum, var_name=链处理模式, hint=指定单链或多链处理, default=auto)
- outputs: ['标准化输入', '实体清单', '任务配置']
- quality_gate: ['输入可被解析', '链标识唯一', '模型支持输入实体']

### s02 特征与模型准备
- desc: 准备模型权重、序列比对和结构模板特征。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，按{MSA_MODE}准备序列特征并最多保留{MAX_TEMPLATES}个模板。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=finetuning_ptm_2.pt)
  - {MSA_MODE} (required=False, type=enum, var_name=MSA模式, hint=选择MSA准备方式, default=precomputed)
  - {MAX_TEMPLATES} (required=False, type=int, var_name=模板上限, hint=限制结构模板数量, default=4)
- outputs: ['模型加载记录', '序列特征', '模板特征']
- quality_gate: ['权重版本可追溯', '特征长度一致', '模板数量不超限']

### s03 结构推理与采样
- desc: 运行结构推理并生成可复现的候选集合。
- depend: ['s02']
- prompt: 执行OpenFold组件消融与结构泛化评测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- step_input:
  - {NUM_SAMPLES} (required=True, type=int, var_name=候选数量, hint=设置候选结构数量, default=5)
  - {NUM_RECYCLES} (required=False, type=int, var_name=回收次数, hint=设置模型回收次数, default=10)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=2026)
- outputs: ['结构候选', '原始置信度', '推理日志']
- quality_gate: ['候选数量达标', '坐标无NaN或Inf', '实体数量与输入一致']

### s04 结构质控与汇总
- desc: 按TM-score及几何完整性筛选并汇总结果。
- depend: ['s03']
- prompt: 计算TM-score，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- step_input:
  - {QUALITY_THRESHOLD} (required=False, type=float, var_name=质量阈值, hint=设置候选质量下限, default=0.7)
  - {OUTPUT_FORMAT} (required=False, type=enum, var_name=结构格式, hint=选择结构输出格式, default=mmCIF)
- outputs: ['排序结构', 'TM-score汇总表', '结构质控报告']
- quality_gate: ['结构文件可解析', '低质量候选已标记', '结果可追溯到参数']

## 使用本工作流的场景（场景→工作流映射）
- B02
- B08
- B03
- B10
- B01
- B09
- B07
- B04
- B05
- B06
