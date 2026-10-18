# 用法与集成（onescience-structure-viewer）

## 1. 最小调用

```bash
python3 .opencode/skills/onescience-structure-viewer/scripts/render_structure.py \
        structures/POSCAR --outdir structures
# -> structures/view.html + structures/structure.json
```

打开 `view.html` 即可（双击 / `file://` 均可；结构数据已 inline，只有 3Dmol.js 走 CDN）。

## 2. 带契约与门限报告（推荐，dft-model-gate 场景）

```bash
python3 render_structure.py structures/POSCAR \
        --contract model_contract.json \
        --gate-json /tmp/gate.json \
        --title "CO2 + K + 40 H2O on Cu(111)" \
        --subtitle "form A / gate PASS"
```

侧栏 Notes 会自动渲染：

- **System** / **Slab**（层数、固定层、真空）
- **Species**（每个物种的 count / role / mode / solvent_model / layers_min）
- **Delivery**（form A/B）与 **POSCAR order**
- **Gate**：`N PASS / N WARN / N FAIL`，FAIL 项逐条列出（最多 8 条）

同时 `--contract` 会给每个原子打上 `group` 标签（slab / solvent / adsorbate / ion），
侧栏 Groups 区出现对应复选框，可单独隐藏某一类（例如只看 slab+吸附物）。

## 3. Python 内联（建模脚本里直接出图）

```python
import sys, os
sys.path.insert(0, os.path.join(SKILL_DIR, "onescience-structure-viewer", "scripts"))
from viz_core import load_structure, build_payload, write_outputs

struct = load_structure("structures/POSCAR")
payload = build_payload(struct, title="my system", subtitle="relaxed")
write_outputs(payload, "structures", basename="view")
```

`build_payload` 的关键参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `bond_tol` | 0.45 | 共价半径和的 slack（Å）。金属-非金属配位键想显示就调大 |
| `bond_max_len` | 2.6 | 键长上限（Å）。超过一律不画 |
| `title/subtitle/notes_html` | — | 顶栏与侧栏文案 |
| `contract` | None | 传入则解析 group 标签 |

## 4. 批量（轨迹 / 多构型）

```bash
for f in traj/frame_*.vasp; do
  python3 render_structure.py "$f" --outdir frames --basename "$(basename $f .vasp)" --no-json
done
```

每帧一个 HTML。若帧数很多，建议只渲染关键帧（初态/过渡态/末态），避免产物爆炸。

## 5. CI / 交付集成

- **dft-model-gate**：`check_vasp_inputs.py --delivery-dir <dir>` 的 **I11 门限**要求
  交付目录里必须有 `view.html`（或 `*.html`）。缺失 = FAIL。
- 报告里直接写：`三维视图见 <交付目录>/view.html`，并附一张 `Export PNG` 导出的截图。

## 6. 自定义颜色 / 半径

改 `scripts/viz_core.py` 顶部的 `DEFAULT_COLORS` / `DISPLAY_RADII` / `COVALENT_RADII`。
都是纯 dict，加元素即可，无需改渲染逻辑。

## 7. 输出契约（structure.json）

```jsonc
{
  "title": "...", "subtitle": "...", "notes_html": "...",
  "cell": [[a1],[a2],[a3]],
  "cell_lengths": [..], "cell_angles": [..], "volume": ..,
  "has_cell": true,
  "formula": "CCu64H80KO42",
  "composition": {"Cu":64, ...},
  "n_atoms": 188, "n_fixed": 32,
  "atoms": [{"el":"Cu","xyz":[x,y,z],"fixed":false,"tag":"","group":"slab"}, ...],
  "bonds": [[i, j, dist], ...],
  "colors": {"Cu":"#c88033", ...},
  "radii": {"Cu":0.85, ...},
  "elements_ordered": ["C","Cu","H","K","O"],
  "source_files": [".../POSCAR", ".../model_contract.json"],
  "contract": { ... } | null
}
```

`atoms[].xyz` 是**解缠后**的显示坐标（分子跨 PBC 已被平移回完整形态），
与 POSCAR 原始 wrap 坐标可能相差整数倍晶格矢——这是刻意的，见 troubleshooting。
