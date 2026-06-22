# SimpleFold 执行要点

SimpleFold 是 flow matching 生成式折叠模型。推理流程可从 FASTA CLI 进入，但模型内部需要 atom 特征、token 元信息和 ESM 表征。更换模型规模时，不要只改 hidden size；要使用 example/config 中配套规模和 checkpoint。

显存不足时先降低 samples、序列长度或采样步数。输出检查包括结构坐标、残基数、confidence/pLDDT 和日志中的 ESM/feature 生成状态。
