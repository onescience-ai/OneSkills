# 实例任务：界面或缺陷调控实施 @ 钙钛矿太阳能电池氧诱导碘缺陷退化分析

- domain: matchem
- 骨架: matchem-interface-or-defect-control-implementation-task
- 场景: matchem-perovskite-solar-cell-oxygen-induced-iodide-defect-degradation-scenario (钙钛矿太阳能电池氧诱导碘缺陷退化分析)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 钙钛矿太阳能电池氧诱导碘缺陷退化分析
- 关联论文: Fast oxygen diffusion and iodide defects mediate oxygen-induced degradation of perovskite solar cells | doi:

## 本实例步骤描述
制备或建模界面钝化、组分、晶粒或缺陷调控方案。

## 本实例执行 prompt
在保持对照一致的前提下实施调控，记录全部工艺参数或计算设置。

## 本实例输入槽
- {DEVICE_STACK} | required=True | type=object | var_name=器件与材料堆叠 | hint=钙钛矿组成、传输层、界面层、厚度和制备路 | default={'perovskite': 'specified', 'stack': 'specified'}

## 本实例产出
- 候选方案
- 工艺/模型日志

## 本实例质量门禁
- 仅改变预定义变量
- 对照样完整

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
