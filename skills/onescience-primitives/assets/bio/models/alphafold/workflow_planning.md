# description

AlphaFold 规划知识用于基于 `RunModel` 构建 JAX/Haiku 单体或多聚体结构推理代码，并确保配置、参数树与特征管线相互匹配。

# when_to_use

- 已有 AlphaFold 配置、参数和数据管线特征，需要直接构建模型推理。
- 需要单体或多聚体 AlphaFold 结果与 pLDDT、PAE、pTM/ipTM 等置信度。
- 需要检查特征处理、模型 shape 或 checkpoint 是否与源码接口兼容。
- 不用于构建原生训练循环；`RunModel` 只实现推理包装。

# inputs

- `ml_collections.ConfigDict` 模型配置。
- 与配置匹配的 Haiku 参数树；若省略将随机初始化。
- AlphaFold 数据管线输出的 raw feature dict 或已处理 feature dict。
- `random_seed` 与目标 JAX device/runtime。

# outputs

- `RunModel` 实例及可复用的特征处理、shape 检查和预测调用代码。
- 模型 prediction dictionary，包括结构与可用置信度字段。
- 对单体/多聚体模式、参数来源和 feature contract 的显式记录。

# procedure

1. 从用户任务确定 monomer 或 multimer，并读取真实配置中的 `multimer_mode`。
2. 加载与该配置匹配的参数树；没有预训练参数时明确标记随机初始化。
3. 使用对应数据管线生成 raw feature dict。
4. 实例化 `RunModel(config, params)`，调用 `process_features`。
5. 可选调用 `eval_shape` 提前验证 JIT shape。
6. 调用 `predict(feat, random_seed)`，按字典中实际存在的字段消费结果。
7. 若需要文件产物，在模型调用之后另建序列化步骤。

# constraints

- 只从 `onescience.flax_models.alphafold` 及其数据管线导入实现。
- monomer/multimer 配置、参数和特征不可交叉混用。
- FASTA 不是 `predict` 的直接输入，必须先通过数据管线。
- 不把随机初始化结果声明为预训练推理结果。

# next_phase_recommendation

- 将预测字典交给结构序列化或质量评估步骤。
- 多模型结果可按 `ranking_confidence` 排序。
- 若用户要求训练，转交编码规划补充独立 Haiku 训练循环和损失规格。

# fallback

- JIT shape 失败时先用 `eval_shape` 定位不匹配字段。
- 参数树不匹配时回到 checkpoint 与 config 配对，不修改层名绕过加载。
- 特征缺失时回到对应单体/多聚体数据管线重新构造。
