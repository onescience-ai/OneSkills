# description

Protenix 规划知识用于按 `Protenix.forward` 的真实 feature/label/mode 契约构建复合物结构训练、推理或评估代码，并召回对应 OneScience modules。

# when_to_use

- 已有 Protenix/AF3 风格 input feature dict，需要复合物结构预测。
- 需要以源码 `train`、`inference` 或 `eval` 模式运行 Protenix。
- 需要组合 protein、nucleic acid、ligand 等 token/atom 特征。
- 不用于直接消费 JSON、FASTA 或 SMILES 字符串。

# inputs

- 完整 `configs` 与匹配 checkpoint。
- `input_feature_dict`。
- train/eval 所需 `label_full_dict`、`label_dict`。
- train 所需 `current_step` 与 `SymmetricPermutation`。
- mode、device、precision 和 runtime 资源。

# outputs

- `(pred_dict, label_dict, log_dict)`。
- inference prediction 中的 coordinates、confidence 和 contact probabilities。
- train/eval 所需预测、更新标签、耗时和置换日志。
- 明确的 mode-specific 字段清单。

# procedure

1. 召回 `protenix_data_pipeline`，按训练或推理模式构造真实 Protenix input feature dict、标签与映射。
2. 从 checkpoint 读取/匹配 configs，构造 `Protenix(configs)`。
3. 严格加载模型权重并移动到目标设备。
4. inference 以 label 参数为 `None` 调用 `mode="inference"`。
5. train 设置模型 training 状态，准备完整/裁剪 label、current step 和 symmetric permutation，再调用 `mode="train"`。
6. eval 按是否有真值准备 label，调用 `mode="eval"`。
7. 按 mode 解析实际返回字段并验证 coordinate shape。

# constraints

- 直接调用 `onescience.models.protenix.protenix.Protenix`。
- 输入 feature dict 必须先完成 atom/token/pair 级特征化。
- mode 只能是 `train`、`inference`、`eval`。
- train 不得省略 labels 或 symmetric permutation。

# next_phase_recommendation

- inference 结果进入结构序列化、confidence 排序和复合物评估。
- train 结果交给 Protenix loss、optimizer 和分布式 runtime。
- 对显存敏感任务调节 cycle、seed、diffusion batch 与 chunk size。

# fallback

- feature key/shape 失败时回到 `protenix_data_pipeline`，不在模型内伪造字段。
- train assertion 失败时检查 mode、model.training、labels 和 permutation。
- 显存不足时先降低配置中的采样/循环规模并启用 chunking。
