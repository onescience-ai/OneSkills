# numpy 标量与数组到 Python 原生类型的 JSON 序列化规则

## 适用范围

任何需要把含 numpy 数据结构（`np.bool_`、`np.int64`、`np.float64`、`np.ndarray` 等）的字典/列表通过 `json.dump` / `json.dumps` 落盘或上报的场景。典型触发点是科学计算工作流中的评估脚本、归因报告、指标汇总（如 CFD_S080 的 `evaluate_apriori.py`）。

## 问题

Python 标准库 `json` 只识别原生类型（`bool` / `int` / `float` / `str` / `list` / `dict` / `None`）。numpy 标量虽然是"数值"，但**不是** Python 原生类型的子类，直接序列化会抛：

```
TypeError: Object of type bool_ is not JSON serializable
```

即使 `np.int64` 在多数平台上表现与 `int` 一致，`isinstance(np.int64(1), int)` 也为 `False`，`json` 会拒绝。

## 规则

### 1. 单值转换（推荐用于结构已知的报表）

在写入字典前显式转换：

| numpy 类型 | 转换方法 | 目标 Python 类型 |
|------------|----------|------------------|
| `np.bool_` | `bool(x)` | `bool` |
| `np.int64` / `np.int32` | `int(x)` | `int` |
| `np.float64` / `np.float32` | `float(x)` | `float` |
| `np.ndarray` | `x.tolist()` | `list`（递归转成原生类型） |
| `np.str_` | `str(x)` | `str` |

`.tolist()` 是关键：它会递归把 ndarray 内的 numpy 标量也一并转成 Python 原生类型，比 `.tolist()` 后再遍历更省事。

### 2. 自定义 JSONEncoder（推荐用于结构不定/嵌套深的产物）

当字典是层层嵌套、无法逐点转换时，用 `default` 钩子做兜底：

```python
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

json.dump(payload, f, cls=NumpyEncoder, ensure_ascii=False, indent=2)
```

关键点：
- `np.integer` / `np.floating` 是所有 numpy 整数/浮点标量的抽象基类，覆盖 `int8/16/32/64` 与 `float16/32/64`。
- `np.bool_` 不是 `np.integer` 的子类，必须单独判分支，否则会被漏掉。
- `super().default(obj)` 保留对未知类型的原有报错行为，避免静默吞异常。

### 3. NaN / Infinity 的处理

`json.dump` 默认允许 `NaN` / `Infinity`，但产出的 JSON **不合规**（RFC 8259 禁止）。跨系统交换前应：
- 用 `allow_nan=False` 强制抛错，然后在上游把 NaN 替换为 `None` 或字符串 `"NaN"`；
- 或显式 `float('nan') → None`（推荐用 `None`，因为大多数下游脚本对 `null` 有明确语义）。

## 常见错误

- **只转 `int()` 不转 `bool()`**：`bool(np.bool_(True))` 是 `True`，但 `int(np.bool_(True))` 是 `1`，语义会变。必须用 `bool()`。
- **对 ndarray 用 `list(x)` 而不是 `x.tolist()`**：`list()` 只做一层展开，元素仍是 numpy 标量，序列化时仍会报错。
- **依赖 `str(x)` 兜底**：会把数值变成带引号的字符串，下游做数值比较会失败。

## 验证方式

写入前用一次 round-trip 断言：

```python
serialized = json.dumps(payload, cls=NumpyEncoder)
restored = json.loads(serialized)
assert restored == json.loads(json.dumps(payload, cls=NumpyEncoder))
```

或更严的：断言 `serialized` 中不含 `NaN` / `Infinity` 字面量：

```python
assert "NaN" not in serialized and "Infinity" not in serialized
```

## 证据

- Python `json` 模块官方文档：<https://docs.python.org/3/library/json.html>（`json.JSONEncoder.default` 钩子契约）
- NumPy 标量类型文档：<https://numpy.org/doc/stable/reference/arrays.scalars.html>（`np.integer` / `np.floating` / `np.bool_` 抽象基类层级）
- 用户实测触发点：CFD_S080 归因报告 `evaluate_apriori.py` 因 `np.bool_` 未转换为 Python 原生 `bool`，`json.dump` 抛 `TypeError`
