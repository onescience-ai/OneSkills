# 分子结构准备工具 (molecular-structure-preparation)

## 定位与适用任务

本卡整合三个互补的结构准备工具：Open Babel（格式转换与 SMILES→3D 生成）、RDKit 构象生成器（多构象采样与力场优化）、Packmol（混合物堆积初始构型）。覆盖从 SMILES 文本到可计算 3D 结构的完整准备链路，适用于分子动力学初始化、对接前配体准备、量子化学输入文件生成、多组分体系建模。

## 安装与访问方式

- **Open Babel**：`uvx --from openbabel obabel ...`（需 uv + 网络访问）。无需本地安装，uvx 自动拉取。
- **RDKit 构象生成器**：`uv run <skill_path>/scripts/rdkit_conf_helper.py conf ...`（需 uv）。PEP 723 内联元数据自动安装 rdkit + pandas 依赖。注意：必须用 `uv run <script>` 而非 `uv run python <script>`。
- **Packmol**：`uvx packmol -i ${system_name}.inp`（需 uv + 网络访问）。备选：`uvx --from packmol packmol -i ...`。

## 核心操作模式

### Open Babel 格式转换与 3D 生成
- 格式转换：`uvx --from openbabel obabel input.xyz -ixyz -opdb -O output.pdb`
- SMILES→3D：`uvx --from openbabel obabel -:CCO --gen3d -omol -O ethanol.mol`
- Gaussian 输入生成：`uvx --from openbabel obabel -:CC --gen3d -ogjf | sed "1c %nproc=28\n#opt b3lyp/6-31g(d,p)" > CC.gjf`
- 2D 图像渲染：`uvx --from openbabel obabel -:"SMILES" -opng -O mol.png`

### RDKit 构象生成（rdkit_conf_helper.py）
- 单分子：`uv run <path>/rdkit_conf_helper.py conf --smiles "CCO" --output out.sdf`
- 批量 CSV：`uv run <path>/rdkit_conf_helper.py conf --file data.csv --smiles-col smiles --output data.sdf`
- 多构象采样：默认 `--num-confs 10`（ETKDGv3），优化后保留最低能量构象。大环/柔性分子增至 50+。
- 力场选择：`--ff mmff94s`（默认，参数缺失时自动降级 UFF）、`--ff uff`、`--ff none`（跳过优化）。
- 困难分子：`--use-random-coords --max-attempts 500`。
- 可复现性：`--seed 123`（-1 为非确定性）。

### Packmol 混合物堆积
- 输入 YAML 定义组分文件/数量/密度或盒长/容差。
- 密度→盒长换算：`L_A = (M_total / N_A / density * 1e24)^(1/3)`。
- 写 `.inp` 文件（每组分一个 `structure...end structure` 块，共享 `inside box 0 0 0 L L L`）。
- 运行：`uvx packmol -i mixture.inp`，输出堆积后 XYZ。
- LAMMPS 后处理：`uvx --from lammps-md-tools lammps-fix-box --in input.data --out fixed.data --L 60.69 --wrap`。

## 输出契约与关键字段

- **Open Babel**：目标格式文件（mol/pdb/xyz/gjf/smi/png/svg）。`--gen3d` 输出含 3D 坐标。
- **RDKit 构象生成器**：SDF（V2000 多分子格式，每分子一个最低能量构象）或 XYZ（Å 单位，分子名为注释行）。日志：`[INFO] Done: N_3d 3D, N_2d 2D-fallback, N_skip skipped`；`[RESULT] conf_sdf=/abs/path`。失败分子记录在 `*.skipped.csv` 和 `*.fallback.csv`。
- **Packmol**：`${system_name}.inp`、`${system_name}.xyz`（堆积坐标）、`packmol.out`（日志）。XYZ 仅含坐标，无拓扑/力场类型。

## 性能与合规

- RDKit ETKDGv3 嵌入：单分子 ~0.1-1s；`--num-confs 10` 线性增加。大规模 CSV 无内置并行，需外部拆分。
- Packmol 堆积：分子数 >1000 或容差 <1.5 Å 时收敛慢/可能失败。常用容差 2.0 Å。
- Open Babel `--gen3d` 使用简单力场，精度不如 RDKit ETKDGv3 + MMFF94s。
- 许可：Open Babel LGPL-3.0、RDKit BSD-3-Clause、Packmol LGPL-3.0。

## 常见坑与降级

- **SMILES 含特殊字符**：shell 中必须引号包裹（如 `"[C@@H](O)(F)Cl"`）；Open Babel 的 `-:` 后紧跟 SMILES 无空格。
- **RDKit 3D 嵌入全部失败**：自动降级为 2D（Z=0），输出 `[WARN]` 并记录 fallback.csv。2D 构象不适用于对接/3D-QSAR → 尝试 `--use-random-coords --max-attempts 500`。
- **MMFF94s 参数缺失**：透明降级为 UFF；若两者均不适用则用 `--ff none` 保留原始 ETKDG 几何。
- **`uv run python <script>` 不装依赖**：必须用 `uv run <script>` 触发 PEP 723 内联元数据。
- **Packmol 堆积失败**：分子数过多/容差过小 → 增大容差至 2.5-3.0 Å、增大盒长、或减少分子数分批堆积。
- **dpdata 转换后盒边界错误**：dpdata XYZ→LAMMPS data 可能写默认 0-100 Å box → 用 `lammps-fix-box --L <actual> --wrap` 修正。
- **Open Babel Gaussian 输出需检查**：`sed` 替换头行后务必验证 route section 和资源行（%nproc, method/basis）正确。

## 来源与许可

封装自上游 compchem 技能：`data-processing__openbabel.md`、`molecular-conformer__rdkit-conf.md`、`data-processing__packmol-generate-mixture.md`（均 LGPL-3.0）。本卡不编造 commit 号，所有参数与命令模式均忠于源技能文档记录。
