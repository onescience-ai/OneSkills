# 实例任务：结构验证与输出 @ 高压晶体结构深度学习搜索

- domain: matchem
- 骨架: tk-matchem-b36bb559
- 场景: sc-167e59e3 (高压晶体结构深度学习搜索)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- 高压晶体结构深度学习搜索
- 关联论文: OpenCSP: a deep learning framework for crystal structure prediction from ambient to high pressure | doi:

## 本实例步骤描述
对优先结构做独立检查和可合成性判断。

## 本实例执行 prompt
输出前列候选及结构文件；把动力学、有限温度或实验验证缺口明确列为待验证项。

## 本实例输入槽
- （源场景未提供）

## 本实例产出
- 优先结构
- 验证清单
- PASS/REJECT/BLOCKED 结论

## 本实例质量门禁
- 不将能量最低等同于可实验合成
- 输入和命令可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
