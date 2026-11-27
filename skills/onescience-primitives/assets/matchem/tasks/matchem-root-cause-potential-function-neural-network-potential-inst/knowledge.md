# 实例任务：根源势函数训练 @ 神经网络势长程静电自洽训练

- domain: matchem
- 骨架: matchem-root-cause-potential-function-training-task
- 场景: matchem-neural-network-potential-long-range-electrostatic-training-scenario (神经网络势长程静电自洽训练)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 神经网络势长程静电自洽训练
- 关联论文: Self-consistent determination of long-range electrostatics in neural network potentials | doi:10.1038/s41467-022-29243-2

## 本实例步骤描述
按论文的自洽场神经网络势 SCFNN 从头训练。短程基态（GT）力和 GT Wannier 中心与中心扰动、O 力扰动、H 力扰动分开建模。D0 提供 GT 的短程描述符输入，不是 GT 标签的替代：固定提交的 `train_test/main.py` 对每个母组的各场参考值扣除相应的预测扰动，再沿场轴取平均，构造 GT 目标。中心用映射到局部坐标系的参考中心与预测扰动；O/H 力用原坐标系的参考总力与反旋转后的预测扰动。独立自洽预测以预测中心反馈至周期 Ewald 场并迭代，不是用参考中心算场再做一次条件化回归。作者短程径向截断 12 Bohr，与 Ewald 平滑参数 `sigma=8` 是不同参数。

## 本实例执行 prompt
仅使用 s01 放行并冻结的训练组拟合和缩放。`tools/scfnn-train-test` 固定到 SCFNN v1.0.0，列出入口和参数表。在独立可写的 `train_test` 工作目录按审计分组设置有效索引，由解析段生成 D0 的核坐标和盒长文本，再生成 C++ G2/G4 特征及导数，并由 `assemble_data.py` 拼装与缩放。区分六个 `*_allconfigs.npy`、另行生成的场响应特征和 GT 力拟合所需的六个已缩放特征/导数张量；按工具卡核对文件名、组顺序、尺度及 NumPy/PyTorch 依赖，再由 `main.py` 训练。实测 import、兼容性和真实训练更新不能用包元数据代替。

## 本实例输入槽
- {POTENTIAL_CONFIG} | required=True | type=object | var_name=势函数根源模型配置 | `models/scfnn` 的版本、截断、描述符、平滑/场参数、实际种子及超参数，并绑定 s01 数据和划分摘要；未指定的种子记录实选依据，不把 42 当成论文参数。
- {ROOT_IMPLEMENTATION_MANIFEST} 记录 `tools/scfnn-train-test` 的同提交源码、参数表、前处理输出、有效配置和依赖版本；区分只读源码与从可写目录产生的特征、缩放和训练产物。

## 本实例产出
- 同一次训练的五部件检查点、训练端尺度文件、实际使用的描述符参数和配置；文件身份、数据/划分版本、各文件摘要及整套摘要按模型卡交接。实际采用 TorchScript 的消费者还需同次的五个导出对象。
- 训练日志记录真实优化更新、损失及有效参数。独立进程冷加载同一检查点，保存并重开实际输出；部件重载只证明该部件可用，不等于全势可用。作者 Python 测试以参考中心条件化，C++ MD 用中心差判定收敛且不是静态单构型接口，不能据此宣称独立 E/F/应力验证通过。

## 本实例质量门禁
- 模型名称不以变体替代根源
- 训练过程可复现

## 可调资源（edge:resource，仅真实存在）
- models/scfnn：根源架构、同次状态与冷重载契约。
- tools/scfnn-train-test：真实数据拼装、特征生成、训练和受限的验证入口；C++ 构建条件见工具卡。

## 验收/缺失策略（继承场景）
- 无 s01 放行的数据、有限缩放或可调用依赖时，不启动不满足条件的训练；出现非有限损失或无有效更新时保留已生成的证据与失败位置。只有同次部件、参数与尺度完整并实测冷重载，才交接完整势；不得以作者示例、别次部件或近邻模型补齐。训练成功也不等于独立预测或泛化通过。
