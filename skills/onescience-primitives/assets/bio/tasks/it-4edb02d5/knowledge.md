# 实例任务：结构预测或序列采样 @ B81

- domain: bio
- 骨架: tk-bio-273fa79a
- 场景: sc-e51af581 (B81)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B81
- 关联论文: Accurate RNA 3D structure prediction using a language model-based deep learning approach | doi:; BAnG: Bidirectional Anchored Generation for Conditional RNA Design | doi:

## 本实例步骤描述
执行折叠、反向设计或复合物亲和力推理。

## 本实例执行 prompt
运行语言模型驱动的RNA三维结构预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

## 本实例输入槽
- {NUM_CANDIDATES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构或序列数 | default=100
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制RNA候选多样性 | default=0.8
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=31

## 本实例产出
- RNA候选
- 模型得分
- 推理日志

## 本实例质量门禁
- 候选数量达标
- 配对关系可解析
- 输出与输入链一致

## 可调资源（edge:resource，仅真实存在）
- models/alphafold

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
