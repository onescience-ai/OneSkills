# 工作流：wf-bio-42419238

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 设计目标与约束定义
- desc: 解析ProToken潜空间蛋白结构序列协同设计的目标结构、功能条件和设计范围。
- depend: []
- prompt: 读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的ProToken潜空间蛋白结构序列协同设计任务及可设计区域。
- step_input:
  - {DESIGN_INPUT} (required=True, type=doc, var_name=设计输入, hint=输入结构或约束文件, default=design_256.json)
  - {MODEL_NAME} (required=True, type=enum, var_name=设计模型, hint=选择场景使用的模型, default=PT-DiT)
  - {TARGET_LENGTH} (required=True, type=int, var_name=目标长度, hint=设置目标残基数量, default=256)
- outputs: ['标准化设计输入', '约束清单', '设计区域']
- quality_gate: ['约束引用有效', '目标长度受模型支持', '设计区域无冲突']

### s02 模型与条件特征准备
- desc: 加载权重并编码固定残基、对称性及功能条件。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，编码{FIXED_POSITIONS}固定残基与{SYMMETRY}对称条件，生成模型输入特征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=PT_DiT_params_2000000.pkl)
  - {FIXED_POSITIONS} (required=False, type=list[int], var_name=固定残基位点, hint=列出保持不变的位点, default=[10, 25])
  - {SYMMETRY} (required=False, type=str, var_name=对称群, hint=填写蛋白对称群, default=C1)
- outputs: ['条件特征', '固定残基掩码', '模型加载记录']
- quality_gate: ['固定位点在长度范围内', '对称群可解析', '条件特征无缺失']

### s03 候选生成与序列采样
- desc: 生成结构或序列候选并记录随机性参数。
- depend: ['s02']
- prompt: 以温度{TEMPERATURE}和种子{SEED}运行ProToken潜空间蛋白结构序列协同设计，生成{NUM_DESIGNS}个候选。
- step_input:
  - {NUM_DESIGNS} (required=True, type=int, var_name=设计数量, hint=设置生成候选数量, default=64)
  - {TEMPERATURE} (required=False, type=float, var_name=采样温度, hint=控制采样多样性, default=0.2)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=17)
- outputs: ['设计候选', '采样分数', '生成日志']
- quality_gate: ['候选数量达标', '固定残基未改变', '序列与结构长度一致']

### s04 回折叠与设计筛选
- desc: 按自洽TM-score、结构自洽性和约束满足度筛选候选。
- depend: ['s03']
- prompt: 计算自洽TM-score并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- step_input:
  - {METRIC_THRESHOLD} (required=False, type=float, var_name=筛选阈值, hint=设置核心指标下限, default=0.6)
  - {KEEP_DIVERSE} (required=False, type=bool, var_name=保留多样候选, hint=是否执行序列去冗余, default=True)
- outputs: ['入选设计', '自洽TM-score汇总表', '约束质控报告']
- quality_gate: ['入选设计满足硬约束', '结构几何无严重冲突', '序列多样性已报告']

## 使用本工作流的场景（场景→工作流映射）
- B14
- B13
- B11
- B20
- B15
- B18
- B16
- B12
- B19
- B17
