# VASP输入文件生成配置

## 适用范围
VASP在OneScience环境中的配置要求、调用方式和输入文件生成规则，包括INCAR参数设置、POSCAR构建、KPOINTS网格选择、POTCAR赝势拼接和执行命令格式；特别覆盖金属表面/溶液周期性界面（如 Cu(111)/水/K/CO2）的初始模型构建。

## 输入
- 材料结构信息（POSCAR格式）
- 计算参数要求（如泛函、截断能、k点网格等）
- OneScience环境配置（conda环境、VASP可执行文件路径、POTCAR赝势库路径）

## 输出
- INCAR文件（输入参数）
- POSCAR文件（原子坐标）
- KPOINTS文件（k点网格）
- POTCAR文件（赝势）
- VASP执行日志

## 文件集交付一致性（硬约束 · 全有或全无）
一次交付必须落在以下两种状态之一，**禁止交付“看似可跑、实则残缺”的半套输入**：
- **仅结构模式**：用户只要结构/初始模型时，只交付 POSCAR（及可选 .cif/.xyz 可视化文件），**不得附带 INCAR/KPOINTS**，避免暗示这是一套可直接提交的计算。
- **完整可提交模式**：用户要求“适合后续 VASP 计算的输入”时，POSCAR + INCAR + KPOINTS + POTCAR **四件必须齐全**，且通过“完整性 gate”后方可交付。
- POTCAR 只能由平台 VASP 赝势库（如 PBE_54/64）按 POSCAR 元素顺序拼接生成，**严禁编造、留空或让用户“自行补齐”**。
- 若赝势库/授权不可用而无法产出 POTCAR：不得改交“POSCAR+INCAR+KPOINTS”冒充可跑套件；应交付 POSCAR 并显式标记 **BLOCKED（原因：POTCAR 赝势库缺失）**，同时给出补齐路径。

## 表面/溶液界面建模（水层覆盖度硬规则）
针对“金属表面 + 显式水层 + 吸附物/离子”的周期性固液界面（如 Cu(111)/水/K/CO2）：
- **水分子数不得随手拍定**，须由目标水膜厚度与密度反推：`n_water ≈ ρ_target × V_water_layer / m_H2O`，其中水膜体积 `V_water_layer = 面内表面积 × 水膜高度`，`m_H2O = 18.015 u`。
- 显式水层默认按 **液态水密度 ρ ≈ 0.9–1.0 g/cm³**、水膜高度 **≥ 10 Å** 铺够；铺完水膜后其上方再留 **≥ 10–15 Å 真空**（配合 IDIPOL=3 / LDIPOL=.TRUE. 偶极校正）。
- 经验锚点（务必对齐，不得少于此量级）：**4×4 Cu(111) 四层 slab（64 Cu）+ 1 CO2 + 1 K 的界面，水分子数应约为 40（即 H≈80、O≈42，全体系约 188 原子）**；仅铺 8 个水分子（H16、92 原子）属于明显不足，不予交付。
- 交付前必须做 **水层密度/覆盖度校验**：报告实际水分子数、水膜厚度、估算密度；密度显著低于约 0.8 g/cm³ 或水膜不连续时判 REJECT 并补铺。

## 流程节点
1. 判定交付模式（仅结构 / 完整可提交），二者对文件集的要求见“文件集交付一致性”。
2. 构建POSCAR文件（原子坐标、晶格参数）；固液界面按“水层覆盖度硬规则”铺够水分子并加 Selective dynamics（固定底部层）。
3. 设置INCAR文件（泛函、截断能、电子步、离子步等）。
4. 生成KPOINTS文件（k点网格密度）。
5. 由赝势库拼接POTCAR文件（元素顺序与POSCAR一致）；赝势库获取遵循下方 resource_acquisition 契约。
6. 验证输入文件完整性（四件套 gate：缺任一件即 BLOCKED/REJECT，不得半交）。
7. 执行VASP计算（若环境可用）。
8. 解析输出文件（OUTCAR、OSZICAR、CONTCAR）。

## 关键参数
| 参数 | 推荐默认值 | 来源 | 说明 |
|------|-----------|------|------|
| ENCUT | ≥ 各元素 POTCAR ENMAX 最大值的 1.3 倍（表面/吸附常取 400–520 eV） | VASP 惯例 | 必须显式，禁止留空 |
| ISMEAR / SIGMA | 金属表面 ISMEAR=1、SIGMA=0.1–0.2；分子/绝缘 ISMEAR=0 | VASP 惯例 | 按体系金属性选择 |
| KPOINTS | 金属 slab 用 Γ-centered；表面常取 3×3×1 或 5×5×1，真空方向 k=1 | VASP 惯例 | 网格密度与面内超胞尺寸成反比 |
| POTCAR 泛函 | 与场景一致（如 PBE，PBE_54/64 库），元素顺序与 POSCAR 完全一致 | VASP 惯例 | 仅由赝势库拼接，禁止编造 |
| ISIF（relax） | slab/固液界面 ISIF=2（固定晶胞、弛豫离子），底部层用 Selective dynamics 固定 | VASP 惯例 | ion-only/cell+ion/slab 三选一须说明理由 |
| EDIFF / EDIFFG | EDIFF=1E-5、EDIFFG=-0.02（eV/Å） | VASP 惯例 | 力收敛判据 |
| 偶极校正 | IDIPOL=3、LDIPOL=.TRUE.（slab/界面） | VASP 惯例 | 配合真空层抑制面外相互作用 |

## resource_acquisition（结构化获取契约）
本卡不随包提供 VASP 赝势库；POTCAR 依赖商业授权库，执行者须按下列顺序主动获取，取不到则干净 BLOCKED 并给出根因，**禁止编造赝势内容或从非授权公开渠道下载**。

```yaml
resource_acquisition:
  - dep: "{POTCAR_LIBRARY}"          # VASP PAW 赝势库（PBE_54/64 等）
    kind: licensed_resource          # 受 VASP 许可证约束的商业授权资源
    source:
      - {provider: environment, id: "PMG_VASP_PSP_DIR / 超算 VASP 安装目录", note: "优先：读取环境已装授权库，按 POSCAR 元素顺序拼接 POTCAR"}
      - {provider: user_upload, id: "用户/管理员提供的授权 POTCAR 集", note: "环境无库时由持有 VASP 授权者提供"}
    forbid:
      - "编造或伪造赝势内容"
      - "从非授权公开渠道下载赝势库"
      - "缺库时半交 POSCAR+INCAR+KPOINTS 冒充可跑套件"
    on_missing: BLOCKED              # 根因=缺授权赝势库；补救=由 VASP 授权管理员将库放到 PMG_VASP_PSP_DIR 或上传授权 POTCAR 集后重试
```

## 边界与分流
- 当VASP环境不可用或缺赝势库时：标记BLOCKED并说明缺失条件，仅交付POSCAR结构，不得半交可跑套件。
- 当输入文件不完整时：标记REJECT并说明缺失文件。
- 当固液界面水分子数/密度不达标时：标记REJECT并补铺水层。
- 当计算不收敛时：标记PARTIAL并说明可能原因。

## 质量检查
- 交付模式一致性：仅结构模式不得含INCAR/KPOINTS；完整模式四件套齐全。
- 水层校验：水分子数、水膜厚度与密度满足覆盖度硬规则。
- 验证输入文件格式正确性、元素顺序与POTCAR映射一致。
- 验证VASP执行日志完整性、输出文件解析正确性。

## 回退策略
- 如果VASP环境不可用，使用替代DFT软件（如Quantum ESPRESSO）。
- 如果POTCAR赝势库不可得，保留POSCAR并BLOCKED上报，禁止编造赝势或半交可跑套件。
- 如果输入文件生成失败，使用模板文件。

## 资源召回建议
- 当需要执行VASP计算时召回本卡片
- 当需要生成VASP输入文件时召回本卡片
- 当需要配置VASP环境时召回本卡片
- 当需要构建金属表面/溶液界面（含水层、吸附物）周期性模型时召回本卡片

## 证据来源
- VASP 官方惯例（INCAR/KPOINTS/POTCAR 通用设置）。
- 固液界面水层覆盖度锚点参考用户提供的 AIMD 基胞结构（Cu(111) 4×4 / 64 Cu + 40 H2O + K + CO2，约 188 原子，12C-0.9V-6ps）。
