---
name: onescience-structure-viewer
description: 需要把原子结构（POSCAR/CONTCAR/XYZ）呈现为可交互三维图形，或把数据图表（PNG/JPG 训练曲线、能量温度演化、RDF）包成 OneCode 可渲染的 HTML 时使用：三维产出单文件 view.html（3Dmol.js）+ structure.json；图表用 render_chart.py 生成自包含 HTML（base64 内嵌）。任何"给出可视化/图表/效果图"的场景都应调用本技能——OneCode 平台只渲染 HTML，裸 PNG 在预览里是 base64 乱码。
type: executor
capabilities:
  owns:
    - 原子结构三维可视化
    - 数据图表HTML封装
    - 3Dmol.js渲染
    - view.html生成
    - render_chart.py
  not_owns:
    - 数据分析
    - 训练
    - 推理
    - 代码生成
  inputs:
    - structure_file
    - chart_data
  outputs:
    - view.html
    - structure.json
    - chart_html
  downstream: []
  prereq:
    - 结构文件或图表数据已就绪
  intent_aspects:
    - structure_visualization
    - chart_rendering
  operation_types:
    - create
  artifact_types:
    - visualization
    - report
  domains:
    - materials
    - general
  trigger_keywords:
    - 可视化
    - 三维结构
    - 3Dmol
    - POSCAR可视化
    - 图表渲染
    - view.html
---

# 三维结构可视化（onescience-structure-viewer）

## 这个技能解决什么

给出一个 POSCAR/XYZ，让人**在浏览器里 360° 看清楚**：晶胞轮廓、原子颜色、成键、
哪些是固定的、哪些是溶剂/吸附物/骨架。用文字描述几何（"CO2 落在顶层 Cu 上方 3.35 Å"）
不如一张可旋转的图 5 秒钟说清楚，也是 DFT 交付里最容易被漏掉的一环。

产物只有两份，**无第三方 Python 依赖**（纯标准库），JS 侧走 CDN：

| 文件 | 说明 |
|---|---|
| `view.html` | 单文件三维查看器；结构数据 inline，可 `file://` 直开 |
| `structure.json` | 结构化 payload（原子、成键、晶胞、角色分组），供其它工具复用 |

## 什么时候用

- 你**产出或消费**了任何原子结构文件，并且它要被"看"：
  - `onescience-dft-model-gate` 走完构建/门限之后 → 交付里必须附 `view.html`
  - 表面/界面/异质结/溶剂化模型的初构
  - NEB 端点、吸附位点、缺陷构型
  - MLMD/LAMMPS 轨迹的代表帧（每帧调一次或挑关键帧）
- 用户明确说"给我看一下""画个三维图""可视化"，或提交前需要自证几何合理。
- 你**不需要**为了跑 VASP 而生成图；这个技能只是让"看图"这一步不再依赖
  VESTA/OVITO 是否装在本地。

## 图表（PNG/JPG）→ HTML（render_chart.py）

**OneCode 平台文件预览只渲染 HTML**，直接交 `.png` 打开是一屏 base64 乱码。因此任何
作为交付物的二维数据图表（MACE 训练曲线、MD 能量/温度演化、RDF、DOS…）都必须先用
本技能的 `render_chart.py` 包成**自包含 HTML**（图片以 base64 data-URI 内嵌，无外部
请求、不受 CSP 影响）。每个 `X.png` 生成同名 `X.html`，正好满足 dft-model-gate 的
**I12 硬门限**（裸光栅图无同名 HTML → FAIL）。

```bash
# 每张图生成同名 sibling HTML；--combine 再额外产出一个合并索引页
python3 .opencode/skills/onescience-structure-viewer/scripts/render_chart.py \
        mace_training.png md_energy_temp.png \
        --outdir <交付目录> --title "Cu 3x3 MLMD 曲线" --combine --basename charts
```

matplotlib 出图时**先 `savefig('x.png')`，再 `render_chart.py x.png`** 即可；不要只交
裸 PNG，也不要以"界面不支持图片"为由放弃出图——出 HTML 就支持。

## 用法

### 命令行

```bash
python3 .opencode/skills/onescience-structure-viewer/scripts/render_structure.py \
        structures/POSCAR \
        --contract model_contract.json \
        --gate-json /tmp/gate.json \
        --outdir structures --basename view \
        --title "Cu(111) + H2O + CO2 + K" \
        --subtitle "form A / gate PASS"
```

参数：

| 参数 | 含义 |
|---|---|
| `structure` (pos) | 输入文件；自动嗅探 POSCAR/CONTCAR/XYZ |
| `--contract` | 可选，`model_contract.json`；用来标注 slab/solvent/adsorbate/ion 分组，并把物种角色写进侧栏 |
| `--gate-json` | 可选，`check_geometry.py --json` 的输出；PASS/WARN/FAIL 计数会显示在侧栏 |
| `--outdir` / `--basename` | 输出目录 / HTML 文件名（默认 `view.html`） |
| `--title` / `--subtitle` / `--notes` | 覆盖顶栏标题、副标题、追加自定义 HTML 备注 |
| `--bond-tol` / `--bond-max` | 键判定阈值（默认 0.45 Å slack / 2.6 Å 上限），一般不用改 |
| `--no-json` | 只出 HTML 不出 structure.json |

### Python 内联调用

```python
import sys; sys.path.insert(0, ".opencode/skills/onescience-structure-viewer/scripts")
from viz_core import load_structure, build_payload, write_outputs

struct = load_structure("structures/POSCAR")
payload = build_payload(struct, title="Cu(111)+H2O+CO2+K")
write_outputs(payload, "structures", basename="view")
```

## 硬性规则

1. **纯标准库**：`render_structure.py` / `viz_core.py` 不得引入 numpy / ASE / pymatgen。
   跑不通就是本技能的 bug，不能靠"你先装个 ase"绕过。
2. **键检测必须用周期最小镜像距离**（`minimum_image_distance`）。裸笛卡尔距离会让
   跨边界的 OH 键凭空"消失"或"横穿整个晶胞"。
3. **分子跨边界必须解缠**（`unwrap_molecules`）：连通分量内的每个原子沿 BFS 相对
   邻居平移整数倍晶格矢，保证渲染出来的 H₂O/CO₂ 是完整的。**不允许**直接把 POSCAR
   里 wrap 到 [0,1) 的分数坐标原样送进渲染器。
4. **金属-金属键默认不画**（`skip_metal_metal=True`）。slab 画满金属键会糊成一坨；
   晶格靠原子球阵列 + 晶胞线框自证。
5. **固定原子必须可视化区分**：`Selective dynamics` 中 `F F F` 的原子会被解析成
   `fixed=True`，渲染时颜色变暗、半径缩小；侧栏"Highlight fixed atoms"可关。
6. **离线可用**：3Dmol.js 走 jsdelivr，加载失败自动回落 unpkg；两个都失败时页面
   显示文本兜底（cell / composition / atoms 全表）+ 顶部错误横幅，**不允许**给出
   一个空白页假装成功。

## 与其他技能的关系

- **`onescience-dft-model-gate`**：把 `view.html` 列为 Form A / Form B 交付的必需产物；
  `check_vasp_inputs.py --delivery-dir` 的 I11 门限会 FAIL 掉缺失 `view.html` 的交付。
- **`onescience-primitives`** / 其它建模类技能：产出结构后调 `render_structure.py`
  一行就出图，不需要各自实现渲染。
- **MLMD / 轨迹类**：对每一帧或关键帧调用；`--basename frame_%05d` 批量出图。

## 文件

| 文件 | 作用 |
|---|---|
| `scripts/render_structure.py` | CLI 入口；组合 contract / gate 报告 / notes 生成 payload |
| `scripts/viz_core.py` | POSCAR/XYZ 解析、周期键检测、分子解缠、payload/HTML 渲染 |
| `assets/viewer_template.html` | 3Dmol.js 单文件模板；结构数据以 `<script id="payload">` inline |
| `references/usage.md` | 常见调用模式、CI 集成、批量渲染 |
| `references/troubleshooting.md` | 离线、超大胞、跨边界成键、颜色/半径自定义 |

Python 3.8+ 可运行；无第三方依赖。JS 端 3Dmol.js 2.4.x（CDN）。
