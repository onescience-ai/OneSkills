# launch

```sh
python -c "from onescience.modules import OneLinear; l=OneLinear(style='ProtenixLinearNoBias', in_features=384, out_features=128, initializer='default'); print(type(l).__name__)"
```

# input_schema

输入可有任意前缀维，最后一维必须等于 `in_features`。

# runtime_interfaces

- `OneLinear(style="ProtenixLinear", ...)`
- `OneLinear(style="ProtenixLinearNoBias", ...)`
- `OneLinear(style="ProtenixBiasInitLinear", ...)`
- `forward`

# main_functions

- `forward`

# execution_resources

资源消耗与普通线性投影一致；指定 `precision` 时会影响 autocast 行为。

# operation_limits

非法 `initializer` 会失败；`OneFC` 与 `OneLinear` 不是同一入口。
