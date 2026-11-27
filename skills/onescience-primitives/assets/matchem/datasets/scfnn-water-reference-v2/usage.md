## access

从 Zenodo v2 获取 `train_test_data.tar.gz`。按归档中的构型 ID 读取三外场数据；下列 `Config*` 是相对路径模式，不是归档成员清单。

```yaml
resource_locations:
  - resource_id: scfnn-water-reference-v2
    resource_version: '2'
    kind: dataset
    availability: unavailable
    local_path: null
    shared_path: null
    planned_path: /public/share/sugonhpcapp01/onestore/rsi/onedatasets/scfnn-water-reference-v2
    required_files:
      - {path: 'D0/Config*/W64-bulk-HOMO_centers_s1-1_0.xyz', role: 零场核与中心}
      - {path: 'D0/Config*/init.xyz', role: 零场盒长}
      - {path: 'D0/Config*/W64-bulk-W64-forces-1_0.xyz', role: 零场核力}
      - {path: 'D0p1V/Config*/W64-bulk-HOMO_centers_s1-1_0.xyz', role: 0.1 V/Å 核与中心}
      - {path: 'D0p1V/Config*/init.xyz', role: 0.1 V/Å 盒长}
      - {path: 'D0p1V/Config*/W64-bulk-W64-forces-1_0.xyz', role: 0.1 V/Å 核力}
      - {path: 'D0p2V/Config*/W64-bulk-HOMO_centers_s1-1_0.xyz', role: 0.2 V/Å 核与中心}
      - {path: 'D0p2V/Config*/init.xyz', role: 0.2 V/Å 盒长}
      - {path: 'D0p2V/Config*/W64-bulk-W64-forces-1_0.xyz', role: 0.2 V/Å 核力}
    scope: 体相周期水盒三场组；成员和组数以所用版本的归档清单为准，能量和应力须有逐构型来源及配对依据
    source:
      - https://doi.org/10.5281/zenodo.5760191
      - https://api.datacite.org/dois/10.5281/zenodo.5760191
```

## data_schema

以场目录和 Config ID 定位，先核对同一母组，再读取核、中心、盒长和力。按 `spec.md` 检查三维形状、有限性、坐标和力的单位及 O,H,H 原子对齐；E/应力需另证逐构型匹配。

## task_usage

s01 使用有血缘的真实成员审计覆盖、生成分组和弃用清单；s03 只用冻结的持出组做参考比较，不能把中心或 DFT 标签送进独立预测入口。

## integration_paths

在 `REFERENCE_DATA` 绑定可读组级路径及成员清单，在 `REFERENCE_PROVENANCE` 绑定同一版本、哈希、许可、母轨迹和计算设置。向训练交接数据与划分摘要；向 `INDEPENDENT_VALIDATION_SPEC` 交接持出 ID 与参考量的定义。

## preparation_requirements

核实名单内每个 Config 在三目录都有必要成员，盒长和原子顺序合法；完成近重复检查、目标标签审计和母轨迹隔离后再生成训练特征。只用训练组拟合尺度，持出预处理复用该尺度。

## consumption_interfaces

读取三目录的原始文本后，按作者 `assemble_data.py` 的解析段生成 O/H 核坐标、中心、盒长及 O/H 力；例如同一 Config ID 在三个目录各取一次，沿场轴拼装。NumPy 拼装输出是 `Oxyz`、`Hxyz`、`wxyz`、`boxlength`、`fO`、`fH` 的 `*_allconfigs.npy` 六类；独立组对应 `*_testconfigs.npy`，不重拟合缩放。

## resource_profile

按组审计可从单 CPU 线程估测，CPU 路线不需要 GPU/DCU 或显存。核、中心和力张量的存储由实体数×3×场数×组数×元素字节数决定（源码原始拼装常为 float64，模型输入为 float32），另计特征/导数和临时数组；组数、主存、磁盘和并行峰值按实际成员测量，不从小组外推全库。

## operation_limits

没有可读的配对成员、来源组或必需标签就不能认定完整数据。只按来源提供的清单和可取成员选择子集；若没有可单独取得的组级文件，则从取得的归档中按构型提取配对成员。历史 CP2K 设置服务于标签追溯，不是读取现成文件的安装依赖。

## evaluation_protocol

先核对训练与持出隔离及覆盖；按组、构型、原子/分量配对。只对定义和单位一致的 E/F/应力计算误差，注明统计窗口、样本数、失败 ID 和不确定度；缺字段和域外样本单列。
