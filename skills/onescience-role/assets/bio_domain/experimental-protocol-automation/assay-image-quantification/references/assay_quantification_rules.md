# 实验图像定量规则

## ROI

条带/点位 ROI 应统一大小或记录可变 ROI 规则。背景可使用局部背景、同 lane 背景或全图背景，但必须一致。

## 饱和和线性

饱和像素会破坏定量线性。需要标记 saturated band，并优先使用未饱和曝光。

## 归一化

Western blot 通常先 target/loading control，再相对 control condition 计算 fold change。Loading control 自身变化时需说明风险。

## 重复

技术重复先在同一生物重复内汇总；统计检验以生物重复为单位。
