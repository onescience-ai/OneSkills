# 实例任务：物理几何质控与排序 @ B48

- domain: bio
- 骨架: tk-bio-64746d14
- 场景: sc-f3f3db2d (B48)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B48
- 关联论文: QuickBind: A Light-Weight And Interpretable Molecular Docking Model | doi:

## 本实例步骤描述
按RMSD通过率、碰撞和内部几何筛选对接结果。

## 本实例执行 prompt
检查碰撞与键几何，计算RMSD通过率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。

## 本实例输入槽
- {MAX_RMSD} | required=False | type=float | var_name=RMSD阈值 | hint=设置成功构象阈值 | default=2
- {TOP_K} | required=False | type=int | var_name=保留姿态数 | hint=设置每配体保留数量 | default=5

## 本实例产出
- 排序姿态
- RMSD通过率汇总表
- 几何质控报告

## 本实例质量门禁
- 入选姿态无严重碰撞
- 排序分数定义明确
- 失败配体原因已记录

## 可调资源（edge:resource，仅真实存在）
- models/diffdock

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
