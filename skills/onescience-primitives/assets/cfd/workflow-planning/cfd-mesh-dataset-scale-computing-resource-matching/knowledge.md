# 大规模网格CFD数据集规模与计算资源匹配

## 适用范围

面向需要接入百万节点级三维PDE网格数据的CFD机器学习任务，解决数据集规模与计算资源匹配、合成数据替代判断、真实数据源检索等问题。适用于涉及湍流模拟、流场预测、PDE求解器替代模型等场景。

**不适用场景**：
- 小规模2D流场数据（节点数<10万）
- 纯数值实验无需真实数据的场景
- 仅使用合成数据验证算法可行性（无需真实数据）

## 输入

- 任务要求的数据规模（节点数、样本数）
- 可用计算资源（GPU显存、HPC节点数）
- 数据格式要求（HDF5/NetCDF/PyG）

## 输出

- 数据源清单（公开数据集URL/DOI）
- 数据规模与资源匹配报告
- 合成数据适用域说明（如适用）

## 流程节点

### Step 1：数据可用性预检
- **操作**：检查任务要求的数据规模是否可从公开源获取
- **参数**：目标节点数≥100万，数据格式=HDF5/NetCDF
- **工具**：网络检索（OpenFOAM benchmarks、NASA TMR、CGNS数据库）
- **质量门禁**：至少找到1个可追溯的公开数据源

### Step 2：数据规模与GPU显存匹配
- **操作**：估算数据加载到GPU所需的显存
- **参数**：单样本显存=节点数×特征数×4字节（float32），batch_size×单样本显存≤GPU显存
- **工具**：显存计算器
- **质量门禁**：数据可放入可用GPU显存（16GB/32GB/80GB）

### Step 3：数据格式选择
- **操作**：根据任务框架选择数据格式
- **参数**：PyTorch Geometric→PyG格式，TensorFlow→HDF5/TFRecord，通用→NetCDF
- **工具**：格式转换脚本
- **质量门禁**：数据格式与训练框架兼容

### Step 4：合成数据标注规范
- **操作**：若无真实数据，使用合成数据时必须标注
- **参数**：标注字段=is_synthetic=true, data_source=synthetic, physical_fidelity=low
- **工具**：metadata写入
- **质量门禁**：dataset_manifest.json明确标注为合成数据

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 百万节点单样本显存(float32) | ~4GB/特征 | 计算值 | 1M节点×1特征×4字节 |
| 百万节点10特征显存 | ~40GB | 计算值 | 1M节点×10特征×4字节 |
| 最小GPU显存要求 | ≥16GB | [D1] | 百万节点至少需16GB显存 |
| 推荐GPU显存 | ≥32GB | [D1] | 含batch和梯度开销 |
| HDF5文件大小估算 | 节点数×特征数×4字节 | [D4] | 未压缩时 |
| 合成数据必须标注 | is_synthetic=true | [1] | 避免误导性结论 |
| 数据源可追溯性 | 至少1个公开URL/DOI | [1] | 不得使用来源不明的数据 |

### 校准数值（体系专属）

以下数值来自某CFD流场预测任务（百万节点3D PDE网格），供量级校准；其他任务需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务要求节点数 | ≥100万 | [1] | 任务prompt明确要求 |
| 实际使用节点数 | 32,768 | [1] | 合成数据，严重不足 |
| 实际样本数 | 10 | [1] | 合成数据，严重不足 |
| 网格尺寸 | 32×32×32 | [1] | 合成数据 |
| 数据来源 | 合成(sin/cos函数) | [1] | 无真实CFD物理场特征 |
| data_audit.md标注 | 合成演示数据集 | [1] | 但未标注为BLOCKED |
| HPC资源 | NULL（无HPC） | [1] | 无法运行大规模仿真 |

## 边界与分流

- **无真实数据且无HPC**：按prompt要求声明BLOCKED，说明无法获取百万节点真实数据，不使用合成数据替代
- **有真实数据但规模不足**：标注数据规模与要求的差距，评估是否可接受
- **有真实数据且规模足够**：验证数据格式兼容性，执行数据加载测试
- **合成数据仅用于算法验证**：明确标注is_synthetic=true，评估结果仅作为算法可行性参考

## 质量检查

- dataset_manifest.json中total_nodes≥目标节点数（或明确标注BLOCKED）
- 数据来源为可追溯的公开数据集（URL/DOI）或用户自有数据（需用户确认）
- 合成数据标注is_synthetic=true
- 数据加载测试通过（无内存溢出、格式兼容）
- data_audit.md中数据来源和规模与manifest一致

## 回退策略

- 无真实数据：声明BLOCKED，不使用合成数据替代
- 真实数据规模不足：标注差距，评估是否可接受（用户确认）
- 数据格式不兼容：转换格式或选择替代数据源
- GPU显存不足：减小batch_size或使用数据分片加载

## 资源召回建议

当任务要求百万节点级PDE网格数据时召回本卡片。配套资源：onescience-data-standardizer的数据接入阶段。

## 补充证据（开源文档）

[D1] "NASA Turbulence Modeling Resource", NASA Langley Research Center, URL: https://turbmodels.larc.nasa.gov/（accessed 2026-09-17，权威机构数据源）
[D2] "OpenFOAM Foundation Documentation", OpenFOAM Foundation, URL: https://openfoam.org/documentation/（accessed 2026-09-17，开源CFD工具文档）
[D3] "CFD General Notation System (CGNS) Standard", CGNS Steering Committee, URL: https://cgns.github.io/CGNS/（accessed 2026-09-17，标准组织文档）
[D4] "h5py FAQ - What datatypes are supported?", h5py Project, version 3.16, URL: https://docs.h5py.org/en/stable/faq.html（accessed 2026-09-17，HDF5存储估算参考）

## 证据来源

[1] CFD_S006归因报告：synthetic_data_not_meeting_scale_requirement issue，任务要求百万节点真实PDE数据，实际使用合成数据(32×32×32, 32768节点, 10样本)，data_audit.md标注为合成演示数据集但未标注BLOCKED
