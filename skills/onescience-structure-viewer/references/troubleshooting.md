# 排障（onescience-structure-viewer）

## 打开 view.html 是空白 / 顶部红色横幅

**症状**：页面只有侧栏，3D 区空白，或顶部出现 "3D renderer failed to load"。

**原因**：3Dmol.js 从 CDN 加载失败（离线 / 防火墙 / CDN 被墙）。

**处理**：
1. 页面会自动显示**文本兜底**（cell / composition / atoms 全表），数据没丢。
2. 要离线渲染：把 `3Dmol-min.js` 下载到本地，改模板顶部的 `<script src=...>` 指向本地文件。
   （技能默认不内联 JS 以控制包体积。）
3. 检查 Network 面板 `3Dmol-min.js` 是否 200；jsdelivr 失败会自动回落 unpkg。

## 分子"断开"或键横穿整个晶胞

**症状**：某个 H₂O 的 O 在晶胞左边、H 在右边，中间一根长键横穿。

**原因**：POSCAR 的 Direct 坐标 wrap 到 [0,1)，分子跨了周期边界。

**处理**：本技能默认已做 `unwrap_molecules`（连通分量内 BFS 平移整数倍晶格矢）。
若仍出现，说明该"分子"没被识别为连通分量（键长超过 `bond_max_len`）。
调大 `--bond-max`（例如 3.0）重跑。

## slab 糊成一坨金属键

**症状**：金属原子之间全是键圆柱，看不清晶格。

**原因**：键检测把金属-金属也算进去了。

**处理**：默认 `skip_metal_metal=True` 已关闭金属-金属键。若你手动改了 `detect_bonds`
把它打开，请改回。金属晶格靠原子球阵列 + 晶胞线框表达，不需要键。

## 想显示金属-配体键（如 K–O 水合壳）

默认不画（K 是离子键，不是共价键）。若要显示：

```python
bonds = V.detect_bonds(struct, tol=1.2, max_len=3.4, skip_metal_metal=True)
```

调大 `tol` 让 K–O（~2.9 Å）落入 `r_K + r_O + tol`。注意这也会带出其它长"键"，自行取舍。

## 固定原子看不出区别

侧栏 **Overlays → Highlight fixed atoms** 取消勾选就会全部同色。
勾选时 `Selective dynamics` 中 `F F F` 的原子颜色变暗、半径缩小。
若 POSCAR 没有 `Selective dynamics` 行，则 `n_fixed=0`，无高亮可言。

## 视图按钮（Top/Side/Front/Iso）不生效

这几个按钮用**显式四元数** `viewer.setView([cx,cy,cz, qx,qy,qz,qw, zoom])` 设置相机，
不依赖 `rotate()` 的角度单位。若改了模板导致不生效，检查 `setView()` 里四元数数组长度
必须是 8（3 位置 + 4 四元数 + 1 zoom）。

## 大体系（>5000 原子）渲染卡

- 键检测在 n>1500 时自动走 cell-list 分桶（`_detect_bounds_bucketed`），Python 侧不慢。
- 慢的是浏览器端：每个键画 2 根 cylinder，5000 原子可能有上万根。
  缓解：侧栏切 **Space fill**（不画键），或调小 `--bond-max` 减少键数。
- 实在太大就只渲染感兴趣区域（用 ASE 切片后再喂给本技能）。

## 颜色不对 / 某元素是灰色

`DEFAULT_COLORS` 没收录该元素时回落 `#cccccc`。在 `viz_core.py` 顶部加一行即可。

## structure.json 的坐标和 POSCAR 对不上

见 usage.md §7：`atoms[].xyz` 是解缠后的显示坐标。要原始坐标请读 POSCAR 本身。
