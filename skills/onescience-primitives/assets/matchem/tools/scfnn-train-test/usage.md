## launch

从下列固定版本取得源码和配套参数表。在独立可写的 `train_test` 工作目录运行数据装配及 `main.py`/`main_test.py`，不要向只读源码目录写入产物。可选 C++ 路线由 `MDcode/SCFNN/CMakeLists.txt` 构建 `MD`；实际可执行路径取构建产生的对象，不把源码位置或演示二进制当作已安装入口。

```yaml
resource_locations:
  - resource_id: scfnn-train-test
    resource_version: 'v1.0.0 / 5a9c68719e961ac958ea63a0d75e9f1f331578d7'
    kind: tool
    availability: planned
    local_path: null
    shared_path: null
    planned_path: /public/share/sugonhpcapp01/onestore/rsi/tools/scfnn-train-test
    required_files:
      - {path: LICENSE, role: 软件许可}
      - {path: train_test/parameters.py, role: 体系与组索引参数}
      - {path: train_test/bad_configurations.txt, role: 作者排除清单}
      - {path: train_test/assemble_data.py, role: 训练数据拼装}
      - {path: train_test/assemble_data_test.py, role: 持出数据解析及拼装}
      - {path: train_test/produce_features.py, role: 训练侧描述符}
      - {path: train_test/produce_features_test.py, role: 诊断侧描述符}
      - {path: train_test/produce_features_d_new.cpp, role: D0 特征与导数生成}
      - {path: train_test/get_Ewald.py, role: 周期及外加场}
      - {path: train_test/rotation_neighbour_dist_functions.py, role: 局部坐标与邻居}
      - {path: train_test/useful_functions.py, role: 数组辅助函数}
      - {path: train_test/train_networks.py, role: 训练与状态导出}
      - {path: train_test/test_networks.py, role: 参考条件化诊断}
      - {path: train_test/main.py, role: 训练入口}
      - {path: train_test/main_test.py, role: 诊断入口}
      - {path: MDcode/SCFNN/CMakeLists.txt, role: 可选 C++ MD 构建配置}
      - {path: MDcode/SCFNN/main_final_twobath.cpp, role: 可选 C++ MD 源码}
      - {path: MDcode/SCFNN/build/models/G2_parameters_OO.txt, role: GT G2 表}
      - {path: MDcode/SCFNN/build/models/G2_parameters_OH.txt, role: GT G2 表}
      - {path: MDcode/SCFNN/build/models/G2_parameters_HO.txt, role: GT G2 表}
      - {path: MDcode/SCFNN/build/models/G2_parameters_HH.txt, role: GT G2 表}
      - {path: MDcode/SCFNN/build/models/G4_parameters_OOO.txt, role: GT G4 表}
      - {path: MDcode/SCFNN/build/models/G4_parameters_OOH.txt, role: GT G4 表}
      - {path: MDcode/SCFNN/build/models/G4_parameters_OHH.txt, role: GT G4 表}
      - {path: MDcode/SCFNN/build/models/G4_parameters_HHO.txt, role: GT G4 表}
      - {path: MDcode/SCFNN/build/models/G4_parameters_HOO.txt, role: GT G4 表}
      - {path: MDcode/SCFNN/build/models/wG2_parameters_OO.txt, role: GT 中心表}
      - {path: MDcode/SCFNN/build/models/wG2_parameters_OH.txt, role: GT 中心表}
      - {path: MDcode/SCFNN/build/models/wG4_parameters_OO.txt, role: GT 中心表}
      - {path: MDcode/SCFNN/build/models/wG4_parameters_OH.txt, role: GT 中心表}
      - {path: MDcode/SCFNN/build/models/dwG2_parameters_OO.txt, role: 中心扰动表}
      - {path: MDcode/SCFNN/build/models/dwG2_parameters_OH.txt, role: 中心扰动表}
      - {path: MDcode/SCFNN/build/models/dwG4_parameters_OO.txt, role: 中心扰动表}
      - {path: MDcode/SCFNN/build/models/dwG4_parameters_OH.txt, role: 中心扰动表}
      - {path: MDcode/SCFNN/build/models/fG2_parameters_OO.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG2_parameters_OH.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG2_parameters_HO.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG2_parameters_HH.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG4_parameters_OO.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG4_parameters_OH.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG4_parameters_HO.txt, role: 力扰动表}
      - {path: MDcode/SCFNN/build/models/fG4_parameters_HH.txt, role: 力扰动表}
    scope: 同一提交的 SCFNN 训练和条件化诊断源码及参数，可选作者 MD 源码；不包括演示权重或二进制
    source:
      - https://doi.org/10.5281/zenodo.5919317
      - https://github.com/andy90/SCFNN/tree/5a9c68719e961ac958ea63a0d75e9f1f331578d7
```

## input_schema

`ROOT_IMPLEMENTATION_MANIFEST` 关联源代码提交、实际输入数据与分组摘要、描述符参数文件和有效依赖；`POTENTIAL_CONFIG` 绑定相同描述符、Ewald 配置、单位、随机种子和训练超参数。三场配对按数据卡；固定 `get_Ewald.py` 按 z 方向的 V/Å 外场除以 `51.4` 转原子单位，不能将标称 V/Å 值当作原子单位。

## runtime_interfaces

`parameters.py` 的 `good_configs` 和 `test_configs` 由作者默认范围和 `bad_configurations.txt` 生成，不是 s01 审计过的子集。只放入少量文件而保持默认枚举，装配器仍会尝试打开其余 Config。在独立可写的 `train_test` 工作目录，按冻结的分组清单分别设置 `good_configs`（合法训练 ID）和 `test_configs`（独立持出 ID），令 `nconfigs`、`nconfigs_test` 分别等于实际列表长度。每个列表内三个场目录使用同一有序 Config ID 列表，先核对成组文件完整及训练与持出母组隔离，再装配；缺场不能补造。

先按 `assemble_data.py` 的坐标解析段产生 D0 的 O/H 核与盒长文本，再在对应 Config 下用 `produce_features_d_new.cpp` 的构建产物读取九张无前缀 G2/G4 表，生成特征/导数；之后完成 `assemble_data.py` 拼装和缩放。`w`、`dw`、`f` 参数表按 `produce_features.py` 和 `main.py` 等实际相对路径装配；不用 BP/4G 参数或权重。按 `spec.md` 核对六个 `*_allconfigs.npy`、中心与场响应特征，以及 GT 力入口另行读取的已缩放 `xO.npy`、`xH.npy`、`xOO_d.npy`、`xHO_d.npy`、`xHH_d.npy`、`xOH_d.npy`。特征和导数必须对应实际训练组顺序与同一训练尺度，不能直接调用依赖预计算文件的分支而跳过生成或复核。

`assemble_data_test.py` 的读取和拼装针对独立组；若作严格持出验证，GT 力及中心描述符的缩放都使用冻结的训练统计量，不在持出组重拟合。

C++ 路线仅在构建成功、初态与适用条件合法、运行目录 `models/` 中同次五个 TorchScript、四个训练尺度（见 `models/scfnn`）和参数表齐备时可调用。`main_final_twobath.cpp` 的七个位置参数依次为 `nstep`（积分步数）、`dt`（原子单位的时间步）、`temperature`（温控目标，K）、`lambda1`（O 温控系数）、`lambda2`（H 温控系数）、`Ez`（z 向外场，V/Å，程序除以 `51.4` 转原子单位）、`restart`（`0` 新起算，`1` 续跑）。O/H 温控时间常数分别为 `lambda1 * dt` 和 `lambda2 * dt`。参数取自实际已验证的初态、目标工况和积分窗口，不套用演示值。

原样构建硬编码 1000 O、2000 H（3000 核），新起算和续跑都按该规模读取，不检查数值提取是否成功。启动前解析 `Oxyz.txt` 的 1000 个 O 和 `Hxyz.txt` 的 2000 个 H，每核须有三个有限的 Bohr 坐标；检查 H 顺序与对应水分子一致，`box.txt` 包含三个对应初态的有限正盒边长（Bohr）。续跑时 `vxyz.txt`（速度）、`axyz.txt`（加速度）各须有 3000 个有限三分量，使用原子单位，按先 O 后 H 与坐标逐核对齐并来自同一帧。从 `*_final.txt` 续跑时，将同帧的四份快照分别交到对应输入文件名，另提供该帧对应的 `box.txt`；以实际落盘步索引为准，不能假定快照来自最后一步。

缺文件、数目或顺序不匹配、工况无依据时不启动。s01 的 64 O/128 H 训练盒即使文件齐全，也不能用于原样构建；不得补行、复制体系或更换工况来绕过门禁。只有目标范围确实支持原样构建的规模且有合法初态，或另有针对目标尺寸经验证的适配构建，才可在满足 s03 放行等上游条件后继续。

## main_functions

`main.py` 依次拟合中心扰动、GT 中心、O/H 力扰动和 GT 力；产物名及冷加载契约见 `models/scfnn`。`main_test.py` 读取六个 `*_testconfigs.npy`，用持出参考 Wannier 计算场，输出仅作有标签的条件化诊断。作者 MD 源码以预测中心反馈周期场，循环只用中心差（源码阈值 `0.0005`）停止，不是经验证的有界静态接口。若另有合格静态闭环，须记录实际阈值、迭代上限、未收敛及非有限分支并保存重开输出。

## execution_resources

Python 小组训练的 CPU 路线以 1 线程、0 GPU/DCU 为待测起点，非硬件最低要求。主存下界按 float32 的核/中心张量和特征导数元素数×4 字节估计，额外峰值含局部坐标、Ewald 阵列和自动微分；磁盘按组、特征、五部件及日志实测。改用加速器时核对实际 GPU/DCU 数、设备内存和并行。

作者 MD 入口调用 `omp_set_num_threads(20)`（`main_final_twobath.cpp:127`），这是 OpenMP 线程请求，不是实测并行度或最低核数。固定 3000 核构建在 `:86`–`:116` 声明旋转坐标、距离矩阵、旋转场及 G2/G4 特征与导数的全局数组。仅特征导数就有 `(30×1000 + 27×2000)×3000×3` 个 `float`，按 4 字节约 2.82 GiB；上述全局数组合计约 3.15 GiB，不含 LibTorch、模型、临时张量和线程开销，也不是运行峰值。实际主存、并行度及按写出步距增长的轨迹磁盘用量须按构建和验证窗口实测，不能从小训练组外推。

## operation_limits

发行包元数据不证明 NumPy/PyTorch 可 import 或 LibTorch ABI 兼容。不能用作者 `.pt`、演示尺度、产物名或零步轨迹补齐真实模型或测试。参考条件化、C++ 动力学和独立单构型预测不是同一接口；只有同构型、顺序、单位与定义相同的总力能参与独立 F 误差计算，直接 E/应力输出及相应标签仍需证实。
