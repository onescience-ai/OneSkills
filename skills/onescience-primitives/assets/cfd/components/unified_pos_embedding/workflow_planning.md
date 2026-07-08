# description
将 unified_pos_embedding 规划为规则网格的位置/距离特征生成阶段，用于跨分辨率参考锚点表达。

# when_to_use
当模型需要固定参考网格的相对距离特征，而输入是规则 1D/2D/3D 网格时使用。

# inputs
- 输入网格尺寸。
- 参考分辨率 ref。
- batchsize 和设备。
- 下游是否接受距离矩阵形状 `(B,N,M)`。

# outputs
- 距离位置编码张量。
- 内存估算。
- 下游字段名和拼接/加性 bias 策略。

# procedure
1. 从输入张量确定 shapelist。
2. 根据预算选择 ref。
3. 估算输出矩阵大小。
4. 调用函数生成 pos。
5. 接入 attention bias 或特征拼接分支。

# constraints
shapelist 长度必须为 1、2 或 3；ref 不宜过大；非结构网格应改用坐标编码或图位置特征。

# next_phase_recommendation
若用于大规模 3D，下一阶段应实现缓存、低秩近似或按块生成，避免重复构造大距离矩阵。

# fallback
显存不足时降低 ref、减小 batch、转 CPU 预计算或改用局部/可学习位置编码。
