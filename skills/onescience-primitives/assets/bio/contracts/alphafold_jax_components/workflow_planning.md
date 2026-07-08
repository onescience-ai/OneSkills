# description

该卡用于在任务编排中识别 AlphaFold v2 JAX 原版推理组件，并判断是否需要沿用原生 pipeline、读取 OpenFold 替代组件，或规划 OneScience wrapper 适配。

# when_to_use

- 用户任务是 AF2 JAX monomer/multimer 推理或结果解释。
- 需要定位 Evoformer、StructureModule 或 confidence head。
- 需要把 AF2 JAX 组件映射到 OneScience 组件语义，但暂不要求立即可运行的 PyTorch wrapper。

# inputs

- FASTA 或已生成 raw features。
- model preset、data preset、max template date。
- 是否 monomer/multimer。
- 是否要求迁移到 `One*` registry。

# outputs

- 组件选择：`AlphaFoldJAXEvoformer`、`AlphaFoldJAXStructureModule`、`AlphaFoldJAXConfidenceHead`。
- 入口建议：原生 `RunModel` 或目标 `One*` 适配。
- 风险清单：参数格式、feature pipeline、框架兼容性。

# procedure

1. 先确认任务是否必须使用 AlphaFold JAX 原版。
2. 若只是 PyTorch AF2-style 训练或微调，转向 OpenFold 组件。
3. 若是原版推理，沿用 `RunModel.process_features` 和 `RunModel.predict`。
4. 若要组件化改造，先写薄适配层，再考虑注册目标 `One*` style。

# constraints

- 不把 JAX/Haiku 模块直接当 PyTorch `One*` 模块。
- 不混用 monomer 与 multimer feature pipeline。
- 不把外部数据库搜索职责放进模型 forward。

# next_phase_recommendation

若需要执行推理，交给 runtime 检查数据库、参数和命令行环境；若需要改造成模块，优先补 wrapper 与 registry，再补测试样例。

# fallback

若 AlphaFold JAX 依赖不可用，降级为生成 feature/pipeline 规划说明；若任务要求 PyTorch 训练，切换到 `openfold_evoformer` 与 `openfold_structure_module`。
