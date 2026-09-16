# 工作流：bio-receptor-ligand-input-precheck-pocket-model-feature-preparation-workflow

- domain: bio
- 步骤数: 4
- 共用场景数: 10

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 受体配体输入预检
- desc: 标准化全局盲对接构象生成与置信度排序的受体、配体或候选姿态输入。
- depend: []
- prompt: 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立全局盲对接构象生成与置信度排序任务。
- step_input:
  - {DOCKING_INPUT} (required=True, type=doc, var_name=对接输入, hint=输入复合物或配体数据, default=1a46_complex)
  - {MODEL_NAME} (required=True, type=enum, var_name=对接模型, hint=选择场景使用的模型, default=DiffDock)
  - {ADD_HYDROGENS} (required=False, type=bool, var_name=补充氢原子, hint=是否标准化质子化状态, default=True)
- outputs: ['标准化受体', '标准化配体', '输入异常清单']
- quality_gate: ['受体结构可解析', '配体化学价合法', '实体标识不重复']

### s02 口袋与模型特征准备
- desc: 加载权重并定义口袋中心、范围和图特征。
- depend: ['s01']
- prompt: 加载{CHECKPOINT}，围绕{POCKET_CENTER}和{POCKET_RADIUS}构建口袋及蛋白配体图特征。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=模型权重名称, default=diffdock_model.pt)
  - {POCKET_CENTER} (required=False, type=list[float], var_name=口袋中心, hint=填写三维中心坐标, default=[0, 0, 0])
  - {POCKET_RADIUS} (required=False, type=float, var_name=口袋半径, hint=设置口袋搜索半径, default=12)
- outputs: ['口袋定义', '蛋白配体特征', '模型加载记录']
- quality_gate: ['中心包含有效坐标', '口袋残基非空', '配体拓扑保持']

### s03 构象采样与打分
- desc: 采样平移、旋转和扭转自由度并输出候选得分。
- depend: ['s02']
- prompt: 运行全局盲对接构象生成与置信度排序，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- step_input:
  - {POSES_PER_LIGAND} (required=True, type=int, var_name=每配体姿态数, hint=设置每个配体姿态数, default=40)
  - {INFERENCE_STEPS} (required=False, type=int, var_name=推理步数, hint=设置构象采样步数, default=20)
  - {SEED} (required=False, type=int, var_name=随机种子, hint=固定随机采样结果, default=101)
- outputs: ['候选姿态', '对接得分', '采样日志']
- quality_gate: ['每个成功配体有候选', '坐标为有限值', '配体键连接未改变']

### s04 物理几何质控与排序
- desc: 按RMSD通过率、碰撞和内部几何筛选对接结果。
- depend: ['s03']
- prompt: 检查碰撞与键几何，计算RMSD通过率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- step_input:
  - {MAX_RMSD} (required=False, type=float, var_name=RMSD阈值, hint=设置成功构象阈值, default=2)
  - {TOP_K} (required=False, type=int, var_name=保留姿态数, hint=设置每配体保留数量, default=5)
- outputs: ['排序姿态', 'RMSD通过率汇总表', '几何质控报告']
- quality_gate: ['入选姿态无严重碰撞', '排序分数定义明确', '失败配体原因已记录']

## 使用本工作流的场景（场景→工作流映射）
- B41
- B45
- B50
- B47
- B46
- B49
- B42
- B43
- B48
- B44
