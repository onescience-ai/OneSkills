# 实例任务：器件堆叠与失效边界定义 @ 准二维钙钛矿绿光LED相组分钝化优化

- domain: matchem
- 骨架: tk-matchem-33ff5801
- 场景: sc-be7d60e9 (准二维钙钛矿绿光LED相组分钝化优化)
- step_id: s01
- depend: []

## 场景研究主体
- 准二维钙钛矿绿光LED相组分钝化优化
- 关联论文: Efficient green light-emitting diodes based on quasi-two-dimensional composition and phase engineered perovskite with surface passivation | doi:

## 本实例步骤描述
固定组成、界面和工作环境。

## 本实例执行 prompt
读取 {DEVICE_STACK} 和 {STRESS_CONDITION}，定义对照样、效率指标和失效阈值。

## 本实例输入槽
- {DEVICE_STACK} | required=True | type=object | var_name=器件与材料堆叠 | hint=钙钛矿组成、传输层、界面层、厚度和制备路 | default={'perovskite': 'specified', 'stack': 'specified'}
- {STRESS_CONDITION} | required=True | type=object | var_name=运行与老化条件 | hint=光照、温湿度、偏压、气氛和测试时长。 | default={'temperature_C': 25, 'relative_humidity_percent': 20}

## 本实例产出
- 器件设计表
- 失效判据

## 本实例质量门禁
- 层序和面积明确
- 测试环境可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
