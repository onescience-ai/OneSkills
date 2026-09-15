# 工作流：wf-matchem-128b457b

- domain: matchem
- 步骤数: 4
- 共用场景数: 21

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 数据与目标定义
- desc: 清洗数据并固定预测目标、单位和约束。
- depend: []
- prompt: 读取 {DATASET}，检查重复、缺失、泄漏、单位和数据许可；定义 {TARGET}，缺失关键标签时标记 BLOCKED。
- step_input:
  - {DATASET} (required=True, type=doc, var_name=训练与验证数据, hint=包含样本来源、目标值、单位和许可信息。, default=CSV/JSON/数据库导出)
  - {TARGET} (required=True, type=str, var_name=优化目标, hint=明确目标性质、单位、方向和约束。, default=目标材料性质)
- outputs: ['清洗数据表', '目标定义', '数据审计报告']
- quality_gate: ['训练/验证/测试划分可追溯', '无未说明的数据泄漏']

### s02 根源模型训练与适用域评估
- desc: 按记录的根源模型训练并评估泛化和适用域。
- depend: ['s01']
- prompt: 使用 {MODEL_CONFIG} 训练模型，保留随机种子、特征和版本；报告交叉验证、外部测试与适用域。
- step_input:
  - {MODEL_CONFIG} (required=True, type=object, var_name=模型配置, hint=模型根源、版本、特征、随机种子和超参数必, default={'model': '按论文或用户配置', 'seed': 42})
- outputs: ['模型检查点', '性能指标', '适用域报告']
- quality_gate: ['外部测试与训练数据隔离', '不能以训练误差替代泛化性能']

### s03 约束候选生成与排序
- desc: 在定义的成分或工艺空间内生成候选并按目标排序。
- depend: ['s02']
- prompt: 在 {TARGET} 的约束内生成候选；同时报告预测值、不确定性和适用域标记。
- step_input:
  - {TARGET} (required=True, type=str, var_name=优化目标, hint=明确目标性质、单位、方向和约束。, default=目标材料性质)
- outputs: ['候选排序', '预测值与不确定性']
- quality_gate: ['所有候选满足硬约束', '适用域外候选单独标识']

### s04 独立验证与结论
- desc: 用独立实验或高保真计算验证优先候选。
- depend: ['s03']
- prompt: 有 {VALIDATION_DATA} 时进行独立验证；没有时明确为待验证预测，不得宣称实验成功。
- step_input:
  - {VALIDATION_DATA} (required=False, type=doc, var_name=独立验证数据, hint=留出测试集、外部实验或高保真计算结果。, default=optional)
- outputs: ['验证对照', 'PASS/REJECT/BLOCKED 结论']
- quality_gate: ['预测与验证分开报告', '失败候选保留记录']

## 使用本工作流的场景（场景→工作流映射）
- B2多主元金属间化合物单相发现
- CO2光催化剂数据驱动可合成性筛选
- MOF合成应用多模态机器学习关联
- MOF结构力学稳定性机器学习预测
- 力学超材料目标响应逆向设计
- 半赫斯勒热电材料无监督发现
- 卤化物钙钛矿兼容分子数据驱动优化
- 多孔材料数据高效基础模型构建
- 振动稳定材料机器学习筛选
- 无铅杂化钙钛矿稳定性机器学习筛选
- 有机半导体主动学习发现
- 热稳定无机荧光粉主晶格机器学习筛选
- 热超材料可见红外兼容伪装逆向设计
- 金属玻璃机器学习成分筛选
- 钙钛矿封装层降解抑制机器学习筛选
- 钙钛矿温度稳定性机器人学习发现
- 钙钛矿结晶机器学习加速优化
- 长效注射聚合物配方机器学习优化
- 高熵固溶体形成机器学习预测
- 高熵碳化物硬度成分机器学习设计
- 高熵陶瓷机器学习发现
