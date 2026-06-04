# MolSculptor 执行要点

MolSculptor 输入是 SMILES、分子图或 case-local 初始分子，不是蛋白或基因组输入。推理路径涉及 JAX/Flax、RDKit、graph padding、vocab 和 checkpoint 配套。

若运行 case 脚本，先确认 receptor、PDBQT、OpenBabel/DSDP、缓存目录和奖励函数。没有外部 docking 依赖时，只能做生成和轻量性质筛选。

输出检查包括 SMILES 有效性、去重、QED/SA/LogP 或自定义 reward、SDF/CSV/PKL 是否存在，以及失败分子比例。
