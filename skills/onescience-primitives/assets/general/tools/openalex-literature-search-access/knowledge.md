# OpenAlex 学术图谱访问 (openalex-literature-search-access)

## 定位与适用任务
论文/作者/机构/主题/来源/出版方/资助方等实体检索、DOI 解析、开放获取 PDF 下载、计量聚合
（被引、按年分组、随机可复现采样）。是多源文献证据检索任务的主索引。

## 访问方式与鉴权
openalex_cli.py 子命令：resolve / get / filter / download-pdf / rate-limit。
无 key 走 polite pool（日预算约 $0.01，极受限）；有 OPENALEX_API_KEY 约 10 req/s、日免费预算 $1。
操作成本：get 免费；filter $0.0001；--search/resolve $0.001；download-pdf $0.01。

## 核心操作模式
- 先解析后过滤：名称一律 resolve 成 ID 再进 --filter，禁止按名称过滤。
- filter 表达式：`,`=AND、`|`=OR；--sort 如 cited_by_count:desc；--group-by 做聚合；
  --sample N --seed 做可复现随机采样；批量 DOI ≤100 用 doi:a|b|c。
- 输出控量：--select 限字段 + --per-page 5–10；filter 结果落盘后 jq 瘦身再入上下文。
- get 接受短 ID（W2741809807）、全 URL 或 DOI URL。

## 输出契约与关键字段
JSON 实体对象；works 常用字段 id/display_name/publication_year/cited_by_count；
download-pdf 主源失败自动回退替代 pdf_url，下载后须校验非空未损坏。

## 限流与合规
只用 CLI（封装重试与限流），禁止 curl/urllib 直打；输出须列所用论文 URL；
每篇 retrieved 论文须自查许可限制。

## 常见坑与降级
401/429 → 凭据协议申请 key；403 → 套餐升级提示；404 → 先 resolve 核验 ID；
resolve 零命中 → 换拼写/缩写；多候选 → 出示 display_name+hint 供人选；
premium-only 过滤字段 from_updated_date/to_updated_date 无 key 不可用。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 literature_search_openalex 技能；
上游条款见 developers.openalex.org。
