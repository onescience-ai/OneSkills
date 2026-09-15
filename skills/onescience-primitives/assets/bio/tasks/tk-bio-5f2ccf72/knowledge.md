# 骨架任务：口袋与模型特征准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并定义口袋中心、范围和图特征。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，围绕{POCKET_CENTER}和{POCKET_RADIUS}构建口袋及蛋白配体图特征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=deltadock.pt
- {POCKET_CENTER} | required=False | type=list[float] | var_name=口袋中心 | hint=填写三维中心坐标 | default=[0, 0, 0]
- {POCKET_RADIUS} | required=False | type=float | var_name=口袋半径 | hint=设置口袋搜索半径 | default=12

## 产出
- 口袋定义
- 模型加载记录
- 蛋白配体特征

## 质量门禁 quality_gate
- 中心包含有效坐标
- 口袋残基非空
- 配体拓扑保持

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0395d8ae
- it-132243ce
- it-150bc503
- it-3776c0c2
- it-5ca8bd69
- it-a5d2eda3
- it-a6a7584a
- it-d3c6b1cd
- it-f1834d33
- it-f6995db5

## 复用场景
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
