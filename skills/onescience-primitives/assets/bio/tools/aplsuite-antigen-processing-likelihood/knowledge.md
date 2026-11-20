# APLSuite 抗原加工似然实现与依赖

## 适用范围

APLSuite 提供抗原加工似然（APL）计算及相关组件，适用于既有抗原的加工/呈递预测与排序。APL 应用、EasyAPI-APLSuite 算法/服务组件与 gpuCOREX 计算组件是不同的软件身份；源码与版本可核验不代表本地已安装、加载或具备离线运行条件。数值方法、条件分支及评价口径见 [场景知识](../../workflow-planning/cd4-t-cell-epitope-processing-presentation/knowledge.md) 和 [规格说明](../../workflow-planning/cd4-t-cell-epitope-processing-presentation/spec.md)。

## 输入输出

- APL 使用与真实抗原残基顺序和坐标对齐的序列熵、晶体 B-factor/适用的柔性输入、COREX 保护因子及 SASA 特征。结构文件只提供部分输入，不能以零向量或合成特征补足真实缺口。
- 残基分数与真实肽的对应依赖实体、链、插入码和表位坐标；联合 MHC 分支另需指定方法、版本、等位基因与真实肽的精确匹配。在线请求包装器不等于离线实现。
- 输出包括所选组件的特征或 APL 分数；仅在联合分支所需输入齐全时形成相应组合分数。独立标签及原测定条件决定能否开展 AP/AUPRC 评价，预测分数本身不是免疫原性或临床有效性证据。

## 版本与依赖

- APL 应用固定提交为 `182c0faaf4f104f1621089f9b4a7899ed62deaa0`。README 说明完整应用依赖 Python 3.12，并说明 Clustal-Omega 依赖；这不构成其他 Python 版本已测试成功或失败的证据。
- EasyAPI-APLSuite 2.0.11 固定提交为 `a76754506c7515bc58b967ff16537ee0440619d4`。其 setup.py 指定 EasyAPI 1.0.1、biopandas 0.4.1、biopython 1.83、freesasa 2.2.1 及 gpuCOREX 0.0.2；同时列有 requests、numpy、pandas、python_on_whales、scipy 和 Levenshtein。
- gpuCOREX tag 0.0.2 指向提交 `0e55fd9f9ca6c279e3ceebd3f2e71f402e16ad1d`，setup.py 的依赖包括 PyTorch、Cython、biopandas、biotite、numpy、pandas、scipy 等。组件的版本约束需要与实际加载环境相容，不能用已有通用科学包代替缺失组件。
- 非致病同源输入及其比对、COREX/SASA 计算和精确离线 MHC 资源是按所选分支满足的技术依赖；软件源码不能替代这些数据、工具或必要文件。现有来源没有证明 `aplsuite.pt` 是这些实现的必要权重。
- APL 与 EasyAPI-APLSuite 固定提交中的 LICENSE 均为 GPLv3（仓库标识 GPL-3.0）。gpuCOREX 0.0.2 的 LICENSE 为 GPLv3，而 setup.py 声明 Apache 2.0；此许可冲突尚未解决，不能合并成统一授权结论。

## 计算资源

- 结构解析与实体映射可走 CPU 串行路径；COREX 涉及构象采样和中间张量，其开销随蛋白长度、采样规模、数值精度、batch 和并发变化，不能由结构文件大小推算全流程内存。
- 固定 EasyAPI-APLSuite 的 COREX wrapper 在 `gpu_num=0` 时选择 CPU；其他分支选择 CUDA。该事实只描述此组件的设备接口，不能推断完整应用无 GPU 需求或已在任意 GPU/DCU 环境通过兼容测试。
- 129 残基的四个 float64 特征向量裸数据规模为 `129 × 4 × 8 = 4128` 字节；这只是数组存储估算，不包含结构解析、采样、中间张量、运行库或输出开销。
- 完整负载的 CPU 核数/并行度、GPU 数量及显存、主存和磁盘峰值均待实际负载测量；现有来源没有支持通用硬件最低配置或全规模容量保证。

## 限制

单结构输入可支持结构质控，但不足以证明完整预测可执行。缺少真实对齐特征、所需同源资料、离线 MHC 实现或独立标签时，相应分支保持未验证；公开目录出现标签记录也不代表完整独立受测集合，不把未测记为阴性或跨条件拼接真值。

## 来源

- [APL 固定提交 README](https://github.com/Jiarui0923/APL/blob/182c0faaf4f104f1621089f9b4a7899ed62deaa0/README.md) 与 [LICENSE](https://github.com/Jiarui0923/APL/blob/182c0faaf4f104f1621089f9b4a7899ed62deaa0/LICENSE)。
- [EasyAPI-APLSuite 固定提交 setup.py](https://github.com/Jiarui0923/EasyAPI-APLSuite/blob/a76754506c7515bc58b967ff16537ee0440619d4/setup.py)、[COREX wrapper](https://github.com/Jiarui0923/EasyAPI-APLSuite/blob/a76754506c7515bc58b967ff16537ee0440619d4/aplsuite/corex/_corex.py) 与 [LICENSE](https://github.com/Jiarui0923/EasyAPI-APLSuite/blob/a76754506c7515bc58b967ff16537ee0440619d4/LICENSE)。
- [gpuCOREX tag 0.0.2 身份](https://api.github.com/repos/Jiarui0923/gpuCOREX/git/ref/tags/0.0.2)、[固定提交 setup.py](https://github.com/Jiarui0923/gpuCOREX/blob/0e55fd9f9ca6c279e3ceebd3f2e71f402e16ad1d/setup.py) 与 [LICENSE](https://github.com/Jiarui0923/gpuCOREX/blob/0e55fd9f9ca6c279e3ceebd3f2e71f402e16ad1d/LICENSE)。
