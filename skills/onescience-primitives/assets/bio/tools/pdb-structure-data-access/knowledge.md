# RCSB PDB 实验结构数据访问 (pdb-structure-data-access)

## 定位与适用任务
搜索与下载实验测定的生物大分子三维结构（蛋白、核酸、结合配体），按序列/结构/化学等属性检索，
获取结构实验元数据。预测结构置信判读任务在需要实验证据时改道本卡。

## 访问方式与鉴权
RCSB Search API（JSON 查询）+ GraphQL Data API（元数据）+ 坐标文件下载服务；无需 key。
schema-first：先 fetch_schema（search_structure / search_chemical / data_entry）发现可查属性名。

## 核心操作模式
- 属性搜索三步法：取 schema → 单关键词逐次 grep 选最佳属性 → 组 JSON 查询（group/terminal 节点，
  操作符 exact_match/equals/exists/contains_phrase/contains_words/in/greater/less）；--count-only 计数。
- 相似性搜索免 schema：sequence（evalue/identity cutoff）、structure（entry_id+asym_id 候选数）、
  seqmotif（prosite 模式）、chemical（InChI/SMILES 描述符 graph-strict）。
- full_text 仅作最后手段；优先 struct.title 或 rcsb_pubmed_abstract_text 属性。
- 元数据需求用 GraphQL（按 entry_ids/polymer_entities 取字段），比下载整坐标文件高效得多。

## 输出契约与关键字段
查询结果 JSON 必须重定向落盘后用 jq/grep 解析，禁止大响应直喷 stdout。坐标文件 mmcif/pdb。
概念锚点：entity（唯一分子）vs instance/chain（副本）vs assembly（生物学组装）；label 与 auth 两套
编号（脚本与 API 一律 label）；化学组分 ID 形如 [A-Z]{1,3}；分辨率优先
rcsb_entry_info.resolution_combined；引文优先 primary_citation 属性。

## 限流与合规
遵循 rcsb.org usage policy；脚本封装自动限流；完成任务后须用人话解释查询意图供用户纠偏。

## 常见坑与降级
属性同名族多（citation vs primary_citation 等）→ 逐词 grep 多行比较选最佳；用户/论文常用 auth 编号 →
先澄清编号体系；只需元数据却下载坐标 → 改 GraphQL。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 pdb_database 技能；
上游条款见 rcsb.org/pages/usage-policy。
