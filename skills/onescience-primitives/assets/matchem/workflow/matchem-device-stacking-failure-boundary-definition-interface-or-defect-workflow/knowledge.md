# 工作流：matchem-device-stacking-failure-boundary-definition-interface-or-defect-workflow

- domain: matchem
- 步骤数: 4
- 共用场景数: 9

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 器件堆叠与失效边界定义
- desc: 固定组成、界面和工作环境。
- depend: []
- prompt: 读取 {DEVICE_STACK} 和 {STRESS_CONDITION}，定义对照样、效率指标和失效阈值。
- step_input:
  - {DEVICE_STACK} (required=True, type=object, var_name=器件与材料堆叠, hint=钙钛矿组成、传输层、界面层、厚度和制备路, default={'perovskite': 'specified', 'stack': 'specified'})
  - {STRESS_CONDITION} (required=True, type=object, var_name=运行与老化条件, hint=光照、温湿度、偏压、气氛和测试时长。, default={'temperature_C': 25, 'relative_humidity_percent': 20})
- outputs: ['器件设计表', '失效判据']
- quality_gate: ['层序和面积明确', '测试环境可复现']

### s02 界面或缺陷调控实施
- desc: 制备或建模界面钝化、组分、晶粒或缺陷调控方案。
- depend: ['s01']
- prompt: 在保持对照一致的前提下实施调控，记录全部工艺参数或计算设置。
- step_input:
  - {DEVICE_STACK} (required=True, type=object, var_name=器件与材料堆叠, hint=钙钛矿组成、传输层、界面层、厚度和制备路, default={'perovskite': 'specified', 'stack': 'specified'})
- outputs: ['候选方案', '工艺/模型日志']
- quality_gate: ['仅改变预定义变量', '对照样完整']

### s03 光电性能与老化响应评估
- desc: 获取效率、滞后、相稳定性和退化响应。
- depend: ['s02']
- prompt: 用 {CHARACTERIZATION_DATA} 或新测试比较性能和老化，关联界面/缺陷证据。
- step_input:
  - {CHARACTERIZATION_DATA} (required=False, type=doc, var_name=表征或器件数据, hint=J-V、EQE、PL、XRD、XPS 或, default=optional)
- outputs: ['性能与老化数据', '机制分析']
- quality_gate: ['初始效率和稳定性同时报告', '不以单点效率替代稳定性']

### s04 优化方案与复核
- desc: 输出优先方案及独立复核条件。
- depend: ['s03']
- prompt: 基于性能、稳定性和可制造性排序；没有长期测试时标明待验证。
- step_input:
- （源场景未提供）
- outputs: ['推荐方案', '复核计划', 'PASS/REJECT/BLOCKED 结论']
- quality_gate: ['所有结论有对照支撑', '工艺可追溯']

## 使用本工作流的场景（场景→工作流映射）
- TiO2CsPbBr3异质结CO2光还原设计
- 二维三维钙钛矿界面长期稳定设计
- 二维钙钛矿实验室机器学习合成
- 倒置钙钛矿晶粒界面配体锚定优化
- 全无机无铅钙钛矿原生氧化物钝化
- 准二维钙钛矿绿光LED相组分钝化优化
- 平面钙钛矿太阳能电池接触钝化优化
- 柔性钙钛矿组件SnO2界面钝化设计
- 钙钛矿太阳能电池氧诱导碘缺陷退化分析
