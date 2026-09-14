# ChEMBL 生物活性分子与活性数据访问 (chembl-bioactivity-access)

## 定位与适用任务
化合物与药物查询、靶点检索、生物活性数值（IC50/Ki/EC50）获取、作用机制与适应证、服务端结构搜索。
适用于化合物-靶点-活性证据链构建与先导化合物类比检索。

## 访问方式与鉴权
统一入口 chembl_api.py 子命令（molecule/target/activity/drug/mechanism/assay/similarity/substructure/
image/chembl_id_lookup/target_component/drug_indication 等 30 个端点）；--output 为必填；无需 key。

## 核心操作模式
- molecule：--search 名称、--filter 属性过滤（如 molecule_properties__mw_freebase__lte=500、
  __range=150,200）、--ids 批量、--dl_format sdf 下载结构文件（可直接喂 PyMOL/RDKit）。
- activity：--filter target_chembl_id=… standard_type=IC50；跨研究比较必须 --normalize 统一为 nM
  （记录 normalized_value_nM 与 normalization_note）。
- similarity/substructure：SMILES + 阈值的服务端搜索（预索引库，无需本地 RDKit）。
- 互参：target --filter target_components__accession=<UniProt> 由 UniProt 找 ChEMBL 靶点；
  chembl_id_lookup 解析任意 ChEMBL ID 的实体类型。
- 分页：--limit/--offset，page_meta 含 total_count 与 next/previous。

## 输出契约与关键字段
JSON 数组按端点名键控（如 molecules、activities）；读文件提取，不直喷终端。

## 限流与合规
脚本封装限流与网络重试；禁止 curl/自写请求直打 API；遵循 ChEMBL 接口文档条款。

## 常见坑与降级
活性单位混杂（nM/µM/pM）→ 不 normalize 直接比较即错；先 status 验活再查询；
drug/drug_indication 等端点不可 --search（仅标记 searchable 的端点支持）。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 chembl_database 技能；
上游条款见 ChEMBL 接口文档 about 页。
