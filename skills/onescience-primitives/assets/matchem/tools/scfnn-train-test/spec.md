## architecture_overview

SCFNN v1.0.0（`5a9c68719e961ac958ea63a0d75e9f1f331578d7`）包括 Python/NumPy/PyTorch 数据装配、训练与诊断，以及 C++ 描述符和 LibTorch MD 两类执行入口。Python 测试不是独立闭环；C++ MD 是单独构建及调用的程序。

## input_schema

`train_test` 以当前工作目录读取 `parameters.py` 所定义的三场目录和经审计的组列表，以及排除清单和描述符参数表。真实 Config 成员契约见 `datasets/scfnn-water-reference-v2`。D0 C++ 特征步骤读取中心化的 `Oxyz.txt`、`Hxyz.txt` 和 `box.txt` 及 G2/G4 表。`main.py` 读取六个 `*_allconfigs.npy`（O/H 核、Wannier 中心、盒长、O/H 参考力）；坐标为 Bohr，字段形状和力/场单位同数据与模型契约。中心扰动和 O/H 力扰动另用 `features_wannier_peturb.npy`、`features_force_peturb_O.npy`、`features_force_peturb_H.npy`，GT 中心用 `features_wannier_GT_scaled.npy`，均不是 GT 力的输入张量。

作者 MD 构建另需合法初态、积分参数与同次 `models/` 状态。核数写死为 1000 O、2000 H（共 3000 核）：`Oxyz.txt` 和 `Hxyz.txt` 分别输入 `(1000, 3)`、`(2000, 3)` 的 Bohr 坐标，`box.txt` 输入三个 Bohr 盒边长。续跑速度和加速度各为 `(3000, 3)`，按内部先 O 后 H 的核顺序与坐标逐核对应。源码按固定规模提取数值且不验证读取成功，不能将训练用的 64 水分子盒（64 O、128 H）直接交给原样构建；启动前的尺寸、顺序与工况检查见 `usage.md`。

`train_networks.py` 的 `train_force_GT` 从 `assemble_data.py` 的缩放输出读入以下六个 NumPy 数组并转为 float32；它们仅含 D0 描述符及其导数，不含场轴：

| 文件 | 内容与轴顺序 |
|---|---|
| `xO.npy`、`xH.npy` | O/H 中心描述符，分别为 `(组, 64, 30)` 和 `(组, 128, 27)`。 |
| `xOO_d.npy`、`xHO_d.npy` | O 中心描述符对 O/H 核坐标的导数，分别为 `(组, 64, 3, 64, 30)` 和 `(组, 128, 3, 64, 30)`。 |
| `xHH_d.npy`、`xOH_d.npy` | H 中心描述符对 H/O 核坐标的导数，分别为 `(组, 128, 3, 128, 27)` 和 `(组, 64, 3, 128, 27)`。 |

导数轴依次为组、被微分的核、xyz、描述符中心、特征。描述符按对应中心物种的训练均值与极差缩放 `(值−均值)/极差`，导数只除以同一极差；按训练组顺序对齐 GT 力目标，核对尺度非退化、各张量有限。

## output_schema

D0 C++ 前处理产生 `features_G2*.txt`、`features_G4*.txt` 及对应的 `features_dG2*.txt`、`features_dG4*.txt`。`assemble_data.py` 将原始组成员拼装成六个 `*_allconfigs.npy`，将上述特征文本拼装、缩放成 `train_force_GT` 读取的六个张量，并保存 `xO_scalefactor.txt`、`xH_scalefactor.txt`。`main.py` 调用五个拟合部件，保存模型卡列明的 `.pth` 和 TorchScript、中心尺度及实际训练记录。`main_test.py` 输出参考条件化的力/中心诊断。

作者 MD 仅在零基积分步索引 `0, 100, 200, …` 到达写出分支时记录帧，不逐步落盘；索引 `0` 对应首个已推进步，不是未推进的初态。`xyz_hist.txt` 每帧先写三行步索引与盒边长，再写 3000 行核坐标；`wxyz_hist.txt` 每帧头含步索引和源码写出的 `iter+1`，随后是 4000 行 Wannier 中心坐标；两者坐标均为 Bohr。同一分支覆盖写 `Oxyz_final.txt`、`Hxyz_final.txt`、`vxyz_final.txt`、`axyz_final.txt`，对应最近一次已写出的帧，不一定对应最后一个积分步。`force_hist.txt` 只打开，写力调用被注释，不提供力历史。验收按实际重开的完整帧和步索引判断，空文件和文件名不能作轨迹、力或独立验证证据。

## key_dependencies

Python 路径依赖 NumPy 和可实际加载的 PyTorch；D0 特征需要可用 C++ 编译器。作者 CMake 以 C++14、Torch 及可选 OpenMP 构建 `MD`，含站点专用的 LibTorch 路径和编译选项。README 的 oneAPI、CPU C++11 ABI LibTorch 1.9.0 是作者示例兼容条件，需核实当前构建、ABI 和运行依赖，不复用示范 ELF。

## implementation_risks

源码默认索引及排除表不是实物清单，装配脚本不能在空目录直接运行；特征导数、场/构型轴或缩放不一致会使训练/验证失真。`assemble_data_test.py` 的原始缩放段会按测试输入重新算统计量，严格持出验证须复用训练尺度。`main_test.py` 用参考 Wannier 计算场，只能作条件诊断。作者 MD 循环的中心差停止条件不是有迭代上限、非有限检查及独立静态 I/O 的单构型契约；无经证实的直接 E/应力输出。

## code_references

软件归档 doi:10.5281/zenodo.5919317，版本入口 `andy90/SCFNN` v1.0.0；固定源码位置和参数表见 `usage.md`。MD 尺寸及读取见同提交 `MDcode/SCFNN/main_final_twobath.cpp:17`、`:485`、`:546`；步距、落盘及格式见 `:154`、`:166`、`:471`、`:756`、`:771`、`:2177`。论文 doi:10.1038/s41467-022-29243-2 用于方法核验，不代替接口和实物证据。
