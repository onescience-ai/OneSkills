## launch
实际安装树在运行环境 `onescience` 包中

```json
{
  "resource_locations": [
    {
      "resource_id": "onescience-mace",
      "resource_version": "module 0.3.0 / distribution 0.3.1",
      "kind": "tool",
      "availability": "partial",
      "local_path": null,
      "shared_path": null,
      "planned_path": null,
      "required_files": [
        {
          "path": "__init__.py",
          "role": "OneScience模块版本与包入口",
          "format": "python",
          "bytes": 209,
          "sha256": "7e28fe46109bb0ad7a2e2c297c7f64c515435695a593231320bfc873590391e4"
        },
        {
          "path": "models/mace/mace.py",
          "role": "MACE/ScaleShiftMACE构造与forward",
          "format": "python",
          "bytes": 36739,
          "sha256": "3c2f298c2480bacbc8feb37e170a171fd969c7f0734fc054255c3cccd9c59231"
        },
        {
          "path": "modules/block/mace_block.py",
          "role": "interaction类与基本块",
          "format": "python",
          "bytes": 32148,
          "sha256": "1750afca224b6c9e6aae461cbdead71924ae605b951a9beb4a663f94d85d17c5"
        },
        {
          "path": "modules/func_utils/__init__.py",
          "role": "可选依赖的实际急切导入边界",
          "format": "python",
          "bytes": 306,
          "sha256": "7b1d0ce695fda0c9ebe28b26d0298fa2f2660f151bdf454386f195bf61df7fab"
        },
        {
          "path": "modules/func_utils/pangu_utils.py",
          "role": "天气工具到Megatron的导入边界",
          "format": "python",
          "bytes": 18252,
          "sha256": "4cde5893c802fdc1689b0742c59cf636c2fcacfea0623d8fe3ac9ef73adb3e82"
        },
        {
          "path": "modules/func_utils/mace_func_utils.py",
          "role": "MACE周期图与物理量自动微分",
          "format": "python",
          "bytes": 20289,
          "sha256": "4d9b12881e70a4b03f4825182fe3c8403296a8d1f63e78c5ac69f81c7939ded2"
        },
        {
          "path": "modules/func_utils/mace_irreps_tools.py",
          "role": "irreps及head处理",
          "format": "python",
          "bytes": 4059,
          "sha256": "a794a3b91f22b9c327e4279d68649eb19e3ca760f253bd6f97512847d4e9f2fe"
        },
        {
          "path": "modules/layer/mace_radial.py",
          "role": "径向基与cutoff",
          "format": "python",
          "bytes": 11777,
          "sha256": "ae41b1c16ea543dc039f58c08be11e7034b7c6a7b22c966b16d15d72d4421c9d"
        },
        {
          "path": "modules/equivariant/mace_wrapper_ops.py",
          "role": "等变操作及可选加速器接口",
          "format": "python",
          "bytes": 6527,
          "sha256": "64f5423a19e133217a80e7ca7da50644415b5360de5b9037040f31e9368f9ba8"
        }
      ],
      "source": [],
      "scope": "现有完整OneScience安装树的MACE入口及必要本地接口；所列文件用于入口/版本身份核验，不是可独立安装的完整软件包清单。PyTorch/e3nn等外部依赖保持原环境绑定。CPU原生导入在可选天气/分布式链触发GPU属性查询失败，构造/strict/forward未完成；planned_path仅后续修复发布/部署资产目录，未安装，修复版本和安装包来源尚未确认。",
      "acquisition": {
        "status": "blocked",
        "reason": "已安装包可读但CPU原生入口失败；当前skill适配器没有外部运行库修复发布/部署能力，安装包及修复版本待工具所有者核实，不能从现有源码伪造分发URL或部署成功。"
      }
    }
  ]
}
```

原生接口示意如下，完整的同身份权重/config 路径与类型还原例见 [模型 usage/launch](../../models/mace/usage.md#launch)。接口说明未经原生运行验收，不吞导入异常。

```python
from onescience.models.mace.mace import ScaleShiftMACE
from onescience.modules.block.mace_block import RealAgnosticResidualInteractionBlock
# config须先按模型卡从完整companion还原Irreps/class/gate等类型；state来自同身份checkpoint。
# 在float64构造上下文内调用：
# model = ScaleShiftMACE(**config).to("cpu")
# incompatible = model.load_state_dict(state, strict=True)
# model.eval()
```

## input_schema
工具可接收参数化 checkpoint/config；本界面 s02 的具体候选由 models/mace 提供。构造参数从完整 companion 读取并按原生接口还原，不能裁剪元素表或改 cutoff/head/原子参考能。forward 需要真实目标周期图，不能直接传 xyz 文件名或用模型预测充当参考标签。

## runtime_interfaces
原生 ScaleShiftMACE(atomic_inter_scale, atomic_inter_shift, **kwargs) 构造后调用 load_state_dict(state, strict=True)、eval，再按模型图 I/O 计算 energy/forces；力需要位置梯度。interaction 类来自上述 mace_block，Irreps 来自 e3nn.o3，gate 来自 torch.nn.functional。CPU 导入因可选 GPU 链失败时构造与 strict 尚未执行，须保存具体异常和阶段；不从源码存在或模型反序列化成功推断原生兼容。

## main_functions
提供 MACE/ScaleShiftMACE 构造、等变 interaction 类型、周期图准备和物理量自动微分。权重位置、完整配置及物理参数唯一沿模型卡使用；此软件卡负责包身份、加载 API 与依赖边界。

## execution_resources
所选 float64 单模型完整权重/config 输入磁盘下界 44225487 字节，companion 声明参数量对应 37509248 字节参数张量估算下界；详见 [模型资源说明](../../models/mace/usage.md#execution_resources)。这些值不含 buffer、邻居边图、自动微分、副本和软件环境。既有 1 CPU 线程、0 可见 GPU 的观察只涉及反序列化；正式原生加载及 3×3 界面运行的 CPU 核数、主存、GPU/DCU 数量及显存待测，随输入原子/边数、精度、batch 与并发变化。环境目录不能替代硬件需求。

## operation_limits
原生修复/发布/部署由工具所有者承担，当前尚未完成；已有包可读而 CPU 入口失败，不能声明 ready。不得以安装计划目录冒充已安装路径，也不猜测安装包来源。原生加载成功后仍须真实目标构型及独立标签才能科学准入；缺正式数据或原生失败时继续可行血缘审计，MD 明确阻塞。
