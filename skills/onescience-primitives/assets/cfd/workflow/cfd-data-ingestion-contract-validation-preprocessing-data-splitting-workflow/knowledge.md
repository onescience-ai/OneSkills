# 工作流：cfd-data-ingestion-contract-validation-preprocessing-data-splitting-workflow

- domain: cfd
- 步骤数: 5
- 共用场景数: 49

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 数据接入与契约核验
- desc: 接入DeepCFD规则网格翼型RANS数据，核验样本、变量、单位、网格坐标及许可。
- depend: []
- prompt: 读取{DATASET_PATH}中的{DATASET_NAME}，为“规则网格CNN翼型稳态流场代理预测”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。
- step_input:
  - {DATASET_PATH} (required=True, type=doc, var_name=数据集路径, hint=目录或清单文件, default=)
  - {DATASET_NAME} (required=True, type=str, var_name=数据集名称, hint=来源与数据版本, default=DeepCFD规则网格翼型RANS数据)
  - {DATA_CONTRACT} (required=False, type=object, var_name=数据契约, hint=变量单位网格定义, default={'input_fields': [], 'target_fields': [], 'units': {}, 'coordinates': 'dataset_native'})
- outputs: ['dataset_manifest.json', 'data_contract.json', 'data_audit.md']
- quality_gate: ['数据文件可读且样本可追溯', '输入目标变量单位坐标定义完整', '不存在训练测试泄漏']

### s02 预处理与数据切分
- desc: 统一物理量与表示，按几何、工况或时间构造无泄漏切分。
- depend: ['s01']
- prompt: 依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。
- step_input:
  - {SPLIT_CONFIG} (required=True, type=object, var_name=切分配置, hint=按对象工况切分, default={'train': 0.7, 'validation': 0.15, 'test': 0.15, 'seed': 42, 'group_by': 'geometry_or_trajectory'})
  - {TARGET_FIELDS} (required=True, type=list[str], var_name=目标变量, hint=待预测物理量, default=['按data_contract.json填写'])
  - {NONDIMENSIONALIZE} (required=False, type=bool, var_name=是否无量纲化, hint=统一跨工况量纲, default=True)
- outputs: ['train_manifest.json', 'validation_manifest.json', 'test_manifest.json', 'normalization.json']
- quality_gate: ['三份切分的对象轨迹互斥', '仅用训练集计算变换统计量', '边界与掩膜语义未破坏']

### s03 模型配置与训练
- desc: 训练CNN、U-Net完成指定输入到目标物理量的映射。
- depend: ['s02']
- prompt: 使用{MODEL_NAME}，默认CNN、U-Net，和{TRAIN_CONFIG}训练“规则网格CNN翼型稳态流场代理预测”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。
- step_input:
  - {MODEL_NAME} (required=True, type=str, var_name=模型名称, hint=实现或模型注册名, default=CNN、U-Net)
  - {TRAIN_CONFIG} (required=True, type=object, var_name=训练配置, hint=超参数和随机种子, default={'framework': 'PyTorch', 'epochs': 100, 'batch_size': 8, 'learning_rate': 0.001, 'seed': 42, 'early_stopping_patience': 15})
  - {INIT_CHECKPOINT} (required=False, type=doc, var_name=初始权重, hint=可选预训练权重, default=)
- outputs: ['best_checkpoint.pt', 'train_config.json', 'training_metrics.csv', 'environment.txt']
- quality_gate: ['训练验证损失均为有限值', '最佳权重可重新加载', '配置环境随机种子可复现']

### s04 批量推理与物理恢复
- desc: 在独立测试集推理，恢复原始单位、网格和物理派生量。
- depend: ['s03']
- prompt: 加载{CHECKPOINT}及训练时数据契约，在s02独立测试集上以{DEVICE}和{BATCH_SIZE}推理。反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量，保存逐样本结果和耗时，禁止用测试标签修正预测。
- step_input:
  - {CHECKPOINT} (required=True, type=doc, var_name=模型权重, hint=通过训练门限权重, default=best_checkpoint.pt)
  - {DEVICE} (required=True, type=str, var_name=计算设备, hint=CPU或CUDA设备, default=cuda)
  - {BATCH_SIZE} (required=False, type=int, var_name=推理批大小, hint=按显存调整批量, default=8)
- outputs: ['predictions/', 'inference_manifest.json', 'timing.csv']
- quality_gate: ['预测无NaN或Inf且形状单位正确', '每个测试样本有唯一结果', '推理未使用测试目标校正']

### s05 任务验收与适用域判定
- desc: 评估统计误差、关键物理约束、泛化能力和计算收益。
- depend: ['s04']
- prompt: 按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。
- step_input:
  - {METRICS} (required=True, type=list[str], var_name=验收指标, hint=统计和物理指标, default=['relative_L2', 'RMSE', 'conservation_residual', 'boundary_error'])
  - {MAX_RELATIVE_L2} (required=False, type=float, var_name=相对误差门限, hint=测试集放行阈值, default=0.1)
  - {RUN_OOD_TEST} (required=False, type=bool, var_name=是否外推测试, hint=测试域外工况, default=True)
- outputs: ['evaluation.json', 'worst_cases.csv', 'applicability_report.md', 'PASS_REJECT_BLOCKED.txt']
- quality_gate: ['统计与物理指标同时报告', '最差样本可追溯', '结论含适用域限制与复核建议']

## 使用本工作流的场景（场景→工作流映射）
- CFD_S001
- CFD_S002
- CFD_S003
- CFD_S004
- CFD_S005
- CFD_S006
- CFD_S007
- CFD_S008
- CFD_S009
- CFD_S010
- CFD_S011
- CFD_S012
- CFD_S013
- CFD_S014
- CFD_S018
- CFD_S019
- CFD_S020
- CFD_S021
- CFD_S022
- CFD_S023
- CFD_S024
- CFD_S025
- CFD_S026
- CFD_S027
- CFD_S028
- CFD_S048
- CFD_S049
- CFD_S050
- CFD_S051
- CFD_S052
- CFD_S053
- CFD_S054
- CFD_S055
- CFD_S056
- CFD_S057
- CFD_S058
- CFD_S059
- CFD_S060
- CFD_S061
- CFD_S062
- CFD_S063
- CFD_S064
- CFD_S065
- CFD_S066
- CFD_S086
- CFD_S087
- CFD_S088
- CFD_S089
- CFD_S090
