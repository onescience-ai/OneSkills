# launch
推荐通过 OneScience MACE demo YAML 启动训练，先 dry-run 检查最终命令与数据路径，再正式运行：

``` sh
cd examples/matchem/mace/demo
bash run.sh --config configs/water_1dcu.yaml --dry-run
bash run.sh --config configs/water_1dcu.yaml
```

直接使用训练入口时，可按单卡 water 配置展开为完整参数：

``` sh
python examples/matchem/mace/train.py --model=MACE --default_dtype=float64 --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --valid_fraction=0.05 --E0s=isolated --energy_key=TolEnergy --forces_key=force --seed=123 --device=cuda --r_max=6.0 --batch_size=2 --valid_batch_size=4 --max_num_epochs=10 --forces_weight=1000 --energy_weight=10 --scheduler_patience=15 --patience=30 --eval_interval=1 --error_table=PerAtomMAE --ema --swa --restart_latest --save_cpu
```

foundation model 微调时，典型配置使用 `foundation_model=medium`、`foundation_model_elements=true`、较小学习率、EMA/SWA，并通过多卡 launcher 执行。

已有完整 portable 候选可先复用，权重与同名 JSON 位于 `/public/share/sugonhpcapp01/onestore/onemodels/mace`。所列两文件均已可读；partial 表示原生兼容与目标科学准入未完成。保持该落点供后续恢复使用，不代表新下载或搬迁。没有 tokenizer 或其他必需分片；JSON 的 source_file 是来源血缘声明，不是 portable 运行必需的第三文件。

```json
{
  "resource_locations": [
    {
      "resource_id": "mace-mp-0-medium-finetune-portable",
      "resource_version": "mace-portable-state-dict-v1",
      "kind": "model_weights",
      "availability": "partial",
      "local_path": null,
      "shared_path": "/public/share/sugonhpcapp01/onestore/onemodels/mace",
      "planned_path": "/public/share/sugonhpcapp01/onestore/onemodels/mace",
      "required_files": [
        {
          "path": "mace-mp-0-medium-finetune-portable.pt",
          "role": "完整portable state_dict包装",
          "format": "pytorch",
          "bytes": 44220927,
          "sha256": "dfb8e7cf1c4de2b8faaeef97bcb50514bb9950d61970c75af556cdb964a9d1a9"
        },
        {
          "path": "mace-mp-0-medium-finetune-portable.json",
          "role": "完整原生构造配置和格式声明",
          "format": "json",
          "bytes": 4560,
          "sha256": "d1a6f6b84f6bc659fc13bdf51363fdcb2397646f4e13a946f77b13eb926c1022"
        }
      ],
      "source": [
        "file:///public/share/sugonhpcapp01/onestore/onemodels/mace/mace-mp-0-medium-finetune-portable.pt",
        "file:///public/share/sugonhpcapp01/onestore/onemodels/mace/mace-mp-0-medium-finetune-portable.json"
      ],
      "scope": "完整portable checkpoint及companion已可读；保留相同持久共享目录作为后续恢复使用位置，不移动、不重复下载。partial表示原生导入/strict/目标forward及独立科学准入未完成；planned_path与shared_path相同不表示这些条件已满足。"
    }
  ]
}
```

下面按已核实源码接口说明完整配置重构。此例的接口核对不等于已经运行通过；外部包导入的实际失败必须保留，由 [tools/onescience-mace](../../tools/onescience-mace/usage.md) 说明软件入口与恢复条件。

```python
import importlib
import json
from pathlib import Path
import numpy as np
import torch
from e3nn import o3
import torch.nn.functional as functional

checkpoint = Path("/public/share/sugonhpcapp01/onestore/onemodels/mace/mace-mp-0-medium-finetune-portable.pt")
config_file = Path("/public/share/sugonhpcapp01/onestore/onemodels/mace/mace-mp-0-medium-finetune-portable.json")
with config_file.open(encoding="utf-8") as stream:
    metadata = json.load(stream)
assert metadata["format"] == "mace-portable-state-dict-v1"
assert metadata["model_module"] == "onescience.models.mace.mace"
assert metadata["model_class"] == "ScaleShiftMACE"
raw = torch.load(checkpoint, map_location="cpu", weights_only=True)
state = raw["state_dict"]
config = dict(metadata["model_config"])
for key in ("hidden_irreps", "MLP_irreps"):
    config[key] = o3.Irreps(config[key])
# 原生包若在此导入失败，异常应保留；不能用伪GPU或替代模块绕过。
module = importlib.import_module(metadata["model_module"])
blocks = importlib.import_module("onescience.modules.block.mace_block")
for key in ("interaction_cls", "interaction_cls_first"):
    assert config[key] == "RealAgnosticResidualInteractionBlock"
    config[key] = getattr(blocks, config[key])
assert config["gate"] == "silu"
config["gate"] = getattr(functional, config["gate"])
config["atomic_energies"] = np.asarray(config["atomic_energies"], dtype=np.float64)
previous_dtype = torch.get_default_dtype()
try:
    torch.set_default_dtype(torch.float64)
    model = getattr(module, metadata["model_class"])(**config).to("cpu")
    incompatible = model.load_state_dict(state, strict=True)
    model.eval()
finally:
    torch.set_default_dtype(previous_dtype)
# strict通过后仍需合格目标构型的周期图、energy/forces与独立精度检查。
```

这是 state_dict 的原生重构接口，不适用 `torch.jit.load` 或默认 `MACECalculator(model_paths=...)` 的直接加载路径。既有训练入口、foundation_model 和 ASE/LAMMPS 示例继续用于其实际支持的格式。

# input_schema
训练数据准备：

- `train_file`：`.xyz` 或 `.extxyz` 训练集路径，必填。
- `valid_file` 或 `valid_fraction`：验证集文件或从训练集切分比例；demo 默认示例 `valid_fraction=0.05`。
- `test_file`：测试集路径，可选但推荐提供。
- `energy_key`：能量字段，示例默认 `TolEnergy`。
- `forces_key`：力字段，示例默认 `force`。
- `stress_key` / `virials_key`：应力或 virial 字段，可选。
- `E0s`：原子参考能方式，常用 `average`、`isolated`、`foundation` 或显式字典；water 示例使用 `isolated`。
- `foundation_model`：可选，传入 `small`、`medium`、`large`、`medium-mpa-0`、`medium-omat-0` 或本地模型后进入 fine-tuning。

模型 forward 数据：

- `positions`: `(NumAtoms, 3)`。
- `node_attrs`: `(NumAtoms, NumElements)`。
- `edge_index`: `(2, NumEdges)`。
- `batch`: `(NumAtoms,)`。
- `cell`: `(NumGraphs, 3, 3)`。
- `shifts` / `unit_shifts`: `(NumEdges, 3)`。
- `head`: 多头任务 id，未显式多头时使用默认 head。

常用训练默认参数：

- `model=MACE`。
- `default_dtype=float64`。
- `num_interactions=2`。
- `num_channels=64` 或 `128`。
- `max_L=0` 或 `2`。
- `correlation=3`。
- `r_max=4.0` 到 `6.0`，water 示例为 `6.0`。
- `batch_size=2`，`valid_batch_size=4`。
- `energy_weight=10`，`forces_weight=1000` 在 water 示例中用于偏重力监督。
- `ema=true`，`swa=true`。

forward 默认参数：

- `training=False`。
- `compute_force=True`。
- `compute_virials=False`。
- `compute_stress=False`。
- `compute_displacement=False`。
- `compute_hessian=False`。
- `compute_edge_forces=False`。
- `compute_atomic_stresses=False`。
- `lammps_mliap=False`。

portable 复用输入为上面同身份的 checkpoint/config，两者缺一不可。完整 model_config 只作 Irreps/class/gate 的类型还原和保持数值的 atomic_energies 数组转换；元素表、cutoff、head、scale/shift 不改。真实 forward 输入仍为完整周期邻居图与原子顺序，力计算须保留位置梯度，不在 torch.no_grad() 下请求力。

# runtime_interfaces
- 构造接口：`MACE(...)`，创建能量-力势函数模型。
- 构造接口：`ScaleShiftMACE(atomic_inter_scale, atomic_inter_shift, **kwargs)`，创建带 interaction energy scale/shift 的模型。
- 推理接口：`model.forward(data, training=False, compute_force=True, ...)`。
- 输出求导接口：通过 forward 内部的 `get_outputs` 从能量生成力、应力、virial、Hessian 与边力。
- 训练入口：demo YAML 将 `train_args` 转换成训练脚本参数，`launch` 决定单进程或多进程启动方式。
- 下游接口：训练得到的模型可用于 ASE calculator、LAMMPS 部署、MD、结构弛豫与评估脚本。

portable 调用次序为完整配置→原生 ScaleShiftMACE 构造→load_state_dict(state, strict=True)→eval→目标图 forward。原生包、interaction 类型、可选依赖限制及实际源码位置由 [OneScience MACE 工具](../../tools/onescience-mace/usage.md#runtime_interfaces) 提供；不要从其未部署的 planned_path 导入软件。float64/完整配置与上述版本组合只是核对依据，原生 CPU 可运行尚未证实。

# main_functions
- `forward`

# execution_resources
- CPU 可用于数据检查、小 batch smoke test 或加载模型结构。
- 实际训练和含力/应力的推理建议使用 GPU/DCU；资源消耗随原子数、边数、`num_channels`、`max_L`、`num_interactions` 和 batch size 增长。
- 计算 `forces` 需要坐标梯度；计算 `stress` / `virials` 需要晶胞 displacement；计算 `hessian` 或逐原子 stress 会显著增加显存与时间。
- 建议环境具备材料数据处理、自动微分、等变张量运算和 ASE/LAMMPS 相关依赖。
- 多卡训练优先使用 demo YAML 与 `run.sh --dry-run` 检查最终 launcher、环境变量和数据文件。

所选 float64 单模型的输入磁盘下界为 44225487 字节；4688656×8=37509248 字节仅是 companion 参数量对应的参数张量估算下界，不含 buffer、邻居图、自动微分、内存副本和环境。历史反序列化使用 1 CPU 线程、0 可见 GPU，只证明文件检查范围；不能据此认定原生 CPU 模型可运行。正式加载及 3×3 界面的 CPU 核数、主存、GPU/DCU 数量、显存待测，随原子数、邻居边数、batch、精度及并发变化。

# operation_limits
- 输入必须是邻居图形式；模型本身不负责从裸 xyz 文本直接构造 `edge_index`。
- extxyz 字段名必须与配置中的 `energy_key`、`forces_key`、`stress_key`、`virials_key` 对齐。
- `r_max` 决定邻域图和 checkpoint 结构兼容性，foundation model 微调时不应随意更改。
- `E0s`、能量单位、力单位、stress/virial 符号必须与训练数据一致。
- 对未见元素、元素表截断或 foundation 元素不一致的情况，模型泛化和权重加载都可能失败。
- 大体系 MD 不应只看验证误差，还要做能量漂移、力异常值和短程碰撞稳定性检查。
- 偶极预测不是普通 `MACE` 的默认输出，需要使用偶极扩展类并提供 `charges` 等额外字段。

文件可读、序列化检查、原生导入/strict、真实目标 energy/forces、独立测试、MD 准入分别判定。原生导入失败时保留最后健康权重与 config 及错误，工具所有者处理发布/部署；可行的数据血缘审计继续。缺正式结构或独立标签时不能宣布科学 PASS，不以文档完整代替运行恢复。

