# 可视化生成工作流

## 工作流目标

根据数据特征与领域需求生成科学可视化图表。

## 执行步骤

### 1. 数据准备
- 加载待可视化数据
- 数据清洗与格式化
- 识别数据维度与类型

### 2. 领域知识匹配
根据 `domain` 参数加载对应领域可视化规范：
- 气象：`assets/meteorology_viz.md`
- 生信：`assets/bioinformatics_viz.md`
- 流体：`assets/fluid_dynamics_viz.md`
- 材料：`assets/materials_science_viz.md`

### 3. 图表类型选择
基于数据特征与需求确定：
- 时间序列 → 折线图/面积图
- 分布 → 直方图/箱线图/小提琴图
- 关系 → 散点图/相关性热图
- 空间 → 等高线图/热力图/矢量场
- 多维 → 3D图/平行坐标/降维可视化

### 4. 图表生成
- 应用领域配色方案
- 设置坐标轴与标签（符合领域规范）
- 添加图例与注释
- 优化布局与分辨率

### 5. 导出输出
- 保存为指定格式（png/svg/pdf/html）
- 生成图表元数据
- 记录可视化参数

## 输出内容

```json
{
  "figures": [
    {
      "path": "output/figure_1.png",
      "type": "line_plot",
      "description": "时间序列趋势图"
    }
  ],
  "metadata": {
    "colormap": "viridis",
    "dpi": 300,
    "format": "png"
  }
}
```
