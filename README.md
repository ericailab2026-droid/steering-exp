# GPT-2 Active Steering 实验

## 📱 手机查看报告
点击这里查看完整报告：**[📄 HTML 报告](https://ericjiang.github.io/steering-exp/)**

## 🧪 实验目标
在 GPT-2 (124M) 上实现 Active Steering，控制模型输出情感倾向（赞美 vs 批评）。

## 📊 当前进度
- ✅ 第一轮实验完成
- ⚠️ 发现样本质量问题
- 🔄 准备改进中

## 🔍 关键发现
- 最佳层：Layer 8 (Silhouette = 0.291)
- 问题：α=10 导致模型重复，α≤6 效果不明显
- 下一步：重新设计纯净样本，测试α=1-5

## 🏃 快速开始
```bash
# 环境已配置好，直接运行
cd ~/projects/interp-lab/steering-exp
source venv/bin/activate
python extract_vector.py
python steer_generation.py
```

## 📁 文件结构
```
steering-exp/
├── steering_data.py        # 实验样本数据
├── extract_vector.py       # 向量提取脚本
├── steer_generation.py     # 生成测试脚本
├── layer{4,6,8}_pca.png   # 可视化图
├── report.html            # 手机友好报告
└── experiments.md         # 详细实验笔记
```

---
*自动生成的实验报告 | 下次汇报: 每 30 分钟*
