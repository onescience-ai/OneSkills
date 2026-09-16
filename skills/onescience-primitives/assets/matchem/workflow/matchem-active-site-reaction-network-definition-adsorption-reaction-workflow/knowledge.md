# 工作流：matchem-active-site-reaction-network-definition-adsorption-reaction-workflow

- domain: matchem
- 步骤数: 4
- 共用场景数: 19

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 活性位与反应网络定义
- desc: 建立催化剂活性位、目标产物和竞争反应网络。
- depend: []
- prompt: 读取 {CATALYST_STRUCTURE} 与 {REACTION_CONDITION}，定义活性位、反应中间体和竞争路径；缺少电位或对照条件时标记 BLOCKED。
- step_input:
  - {CATALYST_STRUCTURE} (required=True, type=doc, var_name=催化剂结构或制备信息, hint=活性位、晶面、组成、缺陷或制备方法。, default=CIF/POSCAR/制备配方)
  - {REACTION_CONDITION} (required=True, type=object, var_name=反应条件, hint=目标产物、温度、压力、电位/pH、反应物, default={'target_product': 'specified product', 'temperature_K': 298})
- outputs: ['活性位模型', '反应网络']
- quality_gate: ['活性位和目标产物明确', '竞争反应未被忽略']

### s02 吸附与反应响应获取
- desc: 计算或测量关键中间体、速率和选择性。
- depend: ['s01']
- prompt: 按 {CALCULATION_CONFIG} 获取吸附、自由能、能垒或实验性能，保留参考态和校准信息。
- step_input:
  - {CALCULATION_CONFIG} (required=False, type=object, var_name=计算或表征配置, hint=如采用 DFT，记录软件、泛函、溶剂、电, default={'method': 'experiment_or_user_confirmed_simulation'})
- outputs: ['原始计算/实验数据', '关键中间体响应']
- quality_gate: ['吸附能、自由能和能垒不混用', '基准与对照齐全']

### s03 活性选择性稳定性联评
- desc: 比较目标产物、竞争反应和结构稳定性。
- depend: ['s02']
- prompt: 在 {REACTION_CONDITION} 下联评活性、选择性、稳定性和副反应，输出限制步骤或证据缺口。
- step_input:
  - {REACTION_CONDITION} (required=True, type=object, var_name=反应条件, hint=目标产物、温度、压力、电位/pH、反应物, default={'target_product': 'specified product', 'temperature_K': 298})
- outputs: ['综合性能表', '限制步骤分析']
- quality_gate: ['不以单一描述符替代完整选择性分析', '长期稳定性不由短时数据替代']

### s04 候选筛选与验证设计
- desc: 给出优先候选及验证实验或高保真计算。
- depend: ['s03']
- prompt: 输出优先候选、关键参数和验证方案；把模型适用域外结论标为待验证。
- step_input:
- （源场景未提供）
- outputs: ['候选排序', '验证方案', 'PASS/REJECT/BLOCKED 结论']
- quality_gate: ['每项推荐有原始数据支撑', '预测与实验结果分列']

## 使用本工作流的场景（场景→工作流映射）
- CuSn原子界面CO2到CO选择性优化
- FeNx位点耐久性质子交换膜燃料电池分析
- Fe单原子催化硝酸盐还原制氨
- Fe单原子氧还原燃料电池催化剂设计
- LaMn掺杂钴尖晶石酸性析氧催化设计
- MOF电催化CO2还原活性位设计
- MoS2CoSe2异质结构析氢催化设计
- Ni单原子Mo2C水分解微环境优化
- PdCeO2单原子催化剂CO氧化动态分析
- Pt单原子异质结构碱性析氢优化
- Ru单原子NiFe层状双氢氧化物水分解优化
- SnBi合金CO2到甲酸盐稳定电催化设计
- 分子金属界面CO2到乙醇催化设计
- 氧化衍生铜CO2电还原活性位分析
- 超薄MOF阵列电催化水分解设计
- 金属氮掺杂碳CO2电还原选择性设计
- 铜纳米晶CO2到C2产物选择性设计
- 镍催化剂CO2活化与碳碳偶联分析
- 高熵合金晶格氧活化析氧催化设计
