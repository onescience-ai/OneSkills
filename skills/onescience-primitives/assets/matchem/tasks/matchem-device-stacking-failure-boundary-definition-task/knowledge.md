# 骨架任务：器件堆叠与失效边界定义

- domain: matchem
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 固定组成、界面和工作环境。

## 执行 prompt（跨场景聚合去重）
- 读取 {DEVICE_STACK} 和 {STRESS_CONDITION}，定义对照样、效率指标和失效阈值。

## 输入槽（var/hint/default）
- {DEVICE_STACK} | required=True | type=object | var_name=器件与材料堆叠 | hint=钙钛矿组成、传输层、界面层、厚度和制备路 | default={'perovskite': 'specified', 'stack': 'specified'}
- {STRESS_CONDITION} | required=True | type=object | var_name=运行与老化条件 | hint=光照、温湿度、偏压、气氛和测试时长。 | default={'temperature_C': 25, 'relative_humidity_percent': 20}

## 产出
- 器件设计表
- 失效判据

## 质量门禁 quality_gate
- 层序和面积明确
- 测试环境可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-device-stacking-failure-2d-3d-perovskite-interface-inst
- matchem-device-stacking-failure-2d-perovskite-lab-ml-synthes-inst
- matchem-device-stacking-failure-all-inorganic-lead-free-inst
- matchem-device-stacking-failure-flexible-perovskite-module-inst
- matchem-device-stacking-failure-inverted-perovskite-grain-inst
- matchem-device-stacking-failure-perovskite-solar-cell-inst
- matchem-device-stacking-failure-planar-perovskite-solar-inst
- matchem-device-stacking-failure-quasi-2d-perovskite-green-inst
- matchem-device-stacking-failure-tio2-cspibr3-heterojunction-inst

## 复用场景
- TiO2CsPbBr3异质结CO2光还原设计
- 二维三维钙钛矿界面长期稳定设计
- 二维钙钛矿实验室机器学习合成
- 倒置钙钛矿晶粒界面配体锚定优化
- 全无机无铅钙钛矿原生氧化物钝化
- 准二维钙钛矿绿光LED相组分钝化优化
- 平面钙钛矿太阳能电池接触钝化优化
- 柔性钙钛矿组件SnO2界面钝化设计
- 钙钛矿太阳能电池氧诱导碘缺陷退化分析
