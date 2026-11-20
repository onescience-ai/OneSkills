# RCSB 1LYZ 定位与使用

## access

```json
{
  "resource_locations": [
    {
      "resource_id": "rcsb-1lyz-r1p4-chicken-lysozyme",
      "kind": "dataset",
      "resource_version": "PDB 1LYZ structure-model revision 1.4 (2024-10-16)",
      "availability": "ready",
      "local_path": "~/onestore/onedatasets/rcsb-1lyz-r1p4-chicken-lysozyme",
      "shared_path": null,
      "planned_path": "/public/share/sugonhpcapp01/onestore/onedatasets/rcsb-1lyz-r1p4-chicken-lysozyme",
      "required_files": [
        {
          "path": "1LYZ.pdb",
          "role": "原始实验结构",
          "format": "PDB",
          "bytes": 145962,
          "sha256": "28e95e819d4e0fc48acdf44209e37ba06f5c9d5d93d9950d67a760b32964326e"
        },
        {
          "path": "entry.json",
          "role": "条目及修订元数据",
          "format": "JSON",
          "bytes": 12212,
          "sha256": "77859874b8d932ca0ce0b9b41b696ffa392729c15a7089fdff354526796a319a"
        },
        {
          "path": "polymer_entity_1.json",
          "role": "实体及来源对应元数据",
          "format": "JSON",
          "bytes": 19222,
          "sha256": "f068c97cd90cbeed346a8ad37cfdf89bee1a84a47bd53af81c4a989e082eb11d"
        }
      ],
      "scope": "仅本地三文件结构输入与质控子集就绪；共享副本未物化，不代表完整下游科研依赖齐全。",
      "source": [
        "https://data.rcsb.org/rest/v1/core/entry/1LYZ",
        "https://data.rcsb.org/rest/v1/core/polymer_entity/1LYZ/1",
        "https://files.wwpdb.org/pub/pdb/README",
        "https://files.rcsb.org/download/1LYZ.pdb"
      ]
    }
  ]
}
```

## data_schema

按 spec/data_schema 解释 PDB 与官方 JSON。读取 JSON 修订和实体字段，核对 1LYZ、entity 1、作者链 A、Gallus gallus 和 P00698 的对应；结构坐标与来源序列分别读取并保留映射，字段缺失或解析异常需显式报告。

## task_usage

支持结构身份、来源、链/残基映射与输入质控。原语以 edge:task 关联既有实例 Task；该关系不表示全部下游数据或预测功能已满足。

## integration_paths

令 data_dir 等于 access.local_path，结构输入使用 data_dir/1LYZ.pdb，版本与实体说明分别使用 data_dir/entry.json 和 data_dir/polymer_entity_1.json。需要共享路径的消费者须先物化并核验共享副本；不能将 planned_path 直接绑定为可用输入。

## preparation_requirements

三文件均可读，大小/哈希与 access 一致；运行环境提供 JSON 和 PDB 读取器。既有回执记录 Biopython 1.84 可用于 PDB 输入读取，这不代表其他工具或完整科研流程已验证。保留原文件与标准化副本的对应。

## consumption_interfaces

通过绝对 data_dir 和三个显式相对文件名交给现有读取器。可使用 Python pathlib 组合路径、json.load 读取两个 JSON，结构读取器输入为 data_dir/1LYZ.pdb。交付原始结构、标准化结构、实体/链/残基对应表及异常记录；输出文件需可重新读取。

## resource_profile

PDB 文本读取可采用 CPU 串行路径，此读取步骤不涉及 GPU 数值计算。主存与输出磁盘峰值受解析器、原子数、保留模型/构象和输出副本影响；尚无实测峰值或硬件最低容量结论。

## operation_limits

保留原始编号与标准化编号的可逆映射，不以重编号或截断掩盖缺段。解析成功、坐标覆盖和后续科学结论分别判断；本地就绪不等于共享就绪。适用范围及未包含依赖见 spec/constraints。

## evaluation_protocol

无独立标签；检查来源/版本对应、必要文件完整性、结构解析、实际 ATOM 覆盖、插入码、altloc、占据率与缺失记录。输出重开用于检查交付完整性，不用于证明下游预测正确。
