# 比较基因组方法参考

## Ortholog

先区分 one-to-one、one-to-many、many-to-many ortholog 和 paralog。跨物种功能比较优先使用高置信 orthogroup；选择分析通常使用 single-copy 或经过仔细筛选的 codon alignment。

## Synteny

共线性分析依赖注释质量和基因顺序。组装碎片化会打断 syntenic block，解释染色体重排前必须检查 assembly contiguity。

## Positive Selection

dN/dS 需要 CDS codon alignment、合适的 gene tree/species tree 和过滤低质量比对区域。branch-site 模型适合检测特定谱系的选择。

## HGT

HGT 证据通常来自系统树不一致、组成偏差、异常 taxonomic hit 和基因邻域，不应只依赖单一指标。
