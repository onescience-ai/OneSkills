# RFdiffusion 执行要点

常见模式由 Hydra 参数控制：`contigmap.contigs`、`inference.input_pdb`、`ppi.hotspot_res`、`diffuser.partial_T`、`inference.symmetry`、`inference.num_designs`、`inference.output_prefix`。

输出 PDB 多为骨架，设计残基常以 Glycine 表示。TRB 文件保存 contig、配置和残基映射，必须保留用于后续 ProteinMPNN 或筛选。

失败常见原因：contig 语法错误、input PDB 链/残基编号不匹配、checkpoint 与任务不匹配、IGSO3 cache 首次构建耗时、显存不足。
