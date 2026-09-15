# 工作流：wf-bio-856a5702

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 分子设计目标定义
- desc: 解析Best-of-K对齐的靶标特异性三维分子生成的靶点、种子分子和生成任务。
- depend: []
- prompt: 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的Best-of-K对齐的靶标特异性三维分子生成任务。
- step_input:
  - {MOLECULE_INPUT} (required=True, type=doc, var_name=分子设计输入, hint=输入靶点或分子文件, default=target_pocket.pdb)
  - {MODEL_NAME} (required=True, type=enum, var_name=分子模型, hint=选择场景使用的模型, default=BoKDiff)
  - {GENERATION_MODE} (required=False, type=enum, var_name=生成模式, hint=选择分子生成任务, default=de_novo)
- outputs: ['标准化分子输入', '靶点条件', '生成任务配置']
- quality_gate: ['分子化学价合法', '靶点条件可解析', '生成模式与输入兼容']

### s02 模型与性质条件准备
- desc: 加载权重并编码靶点、片段和优化性质。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，编码{OBJECTIVES}性质目标，并按{KEEP_SCAFFOLD}决定是否固定种子骨架。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=bokdiff.ckpt)
  - {OBJECTIVES} (required=False, type=list[str], var_name=优化目标, hint=列出需要优化的性质, default=['QED', 'SA', 'affinity'])
  - {KEEP_SCAFFOLD} (required=False, type=bool, var_name=保留核心骨架, hint=是否固定输入分子骨架, default=False)
- outputs: ['模型加载记录', '性质条件向量', '骨架约束']
- quality_gate: ['权重版本可追溯', '性质定义完整', '固定骨架原子映射有效']

### s03 三维分子生成与采样
- desc: 生成分子拓扑和构象并记录随机性参数。
- depend: ['s02']
- prompt: 运行Best-of-K对齐的靶标特异性三维分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- step_input:
  - {NUM_MOLECULES} (required=True, type=int, var_name=生成分子数, hint=设置生成候选数量, default=1000)
  - {TEMPERATURE} (required=False, type=float, var_name=采样温度, hint=控制生成分布宽度, default=1)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=42)
- outputs: ['候选分子SDF', '生成轨迹', '模型分数']
- quality_gate: ['生成数量达标', '原子坐标为有限值', '每个分子可被化学解析']

### s04 性质过滤与候选排序
- desc: 按对接分数、药物相似性和合成可行性汇总候选。
- depend: ['s03']
- prompt: 用{PROPERTY_LIMITS}过滤候选，计算对接分数并进行去重聚类，最终保留前{TOP_K}个分子。
- step_input:
  - {PROPERTY_LIMITS} (required=False, type=object, var_name=性质阈值, hint=设置分子性质过滤阈值, default={'qed_min': 0.6, 'sa_max': 6})
  - {TOP_K} (required=False, type=int, var_name=保留分子数, hint=设置最终保留数量, default=100)
- outputs: ['排序分子集', '对接分数明细', '性质与多样性报告']
- quality_gate: ['入选分子通过化学检查', '重复结构已合并', '筛选规则可复现']

## 使用本工作流的场景（场景→工作流映射）
- B53
- B56
- B57
- B54
- B59
- B52
- B58
- B60
- B55
- B51
