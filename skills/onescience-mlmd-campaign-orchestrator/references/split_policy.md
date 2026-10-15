# 切分策略：时间块（time-block），禁止随机打散

## 为什么
MD 轨迹相邻帧高度相关（1 fs 步长）。随机打散会让验证/测试帧与训练帧“几乎一样”，
导致误差被严重乐观、泛化被高估（数据泄漏）。

## 定义
- 沿时间轴切成连续块，每 `block_frames`（默认 **100**）帧一块（6000 帧 → 60 块）。
- **块内、块间都不打散**；按时间顺序分配：前 `train` 比例块→train，接着 valid，最后 test。
  （可选“固定周期交错”仍非随机，用于缓解分布漂移，但需记录规则。）
- `split.shuffle=false` 写入 `campaign_spec`。

## 已实现（`scripts/vasp2mace_dataset.py`）
```bash
python vasp2mace_dataset.py --traj <vasprun.xml> --out-dir <dir> --prefix aimd \
  --split-policy time-block --block-frames 100 --valid-frac 0.1 --test-frac 0.1
```
产出 `aimd_train/_valid/_test.extxyz` 与 `aimd_meta.json`（含三集合帧区间）。

## 交付声明
块大小、集合比例、分配规则、三集合帧区间；`validate_dataset.py` 会检查
`policy=time-block` 且 `shuffle=false`，否则 WARN。
