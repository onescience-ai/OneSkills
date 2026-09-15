# 骨架任务：吸附与反应响应获取

- domain: matchem
- 复用场景数: 19
- 实例任务数: 19

## 步骤描述（跨场景聚合去重）
- 计算或测量关键中间体、速率和选择性。

## 执行 prompt（跨场景聚合去重）
- 按 {CALCULATION_CONFIG} 获取吸附、自由能、能垒或实验性能，保留参考态和校准信息。

## 输入槽（var/hint/default）
- {CALCULATION_CONFIG} | required=False | type=object | var_name=计算或表征配置 | hint=如采用 DFT，记录软件、泛函、溶剂、电 | default={'method': 'experiment_or_user_confirmed_simulation'}

## 产出
- 关键中间体响应
- 原始计算/实验数据

## 质量门禁 quality_gate
- 吸附能、自由能和能垒不混用
- 基准与对照齐全

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-026ae5d9
- it-03c7cf7e
- it-09405d70
- it-0bbc8ed7
- it-0c74e39a
- it-0e828dc8
- it-66cd8b2c
- it-69c1011b
- it-6b545637
- it-6ca15b2a
- it-6f037f1b
- it-8fa3b8da
- it-b92198eb
- it-bf5b9417
- it-c7c7c96d
- it-cbb5b727
- it-e220c395
- it-f2915b5d
- it-f53f191a

## 复用场景
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
