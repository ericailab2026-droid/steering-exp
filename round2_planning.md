# 🧪 第二轮实验：纯净样本版

## 目标
- 只含纯情感形容词（brilliant/terrible 等）
- 移除商业/政治混杂概念
- 寻找最佳α范围（1-6）

---

## 改进前后对比

| 维度 | 第一轮 | 第二轮（新） |
|------|--------|------|
| 正样本词汇 | brilliant, excellent, company, achievement | brilliant, excellent, remarkable, outstanding |
| 负样本词汇 | terrible, disastrous, Democrats, bailout | terrible, horrible, pathetic, ridiculous |
| 混杂概念 | ✅ 有（商业/政治） | ❌ 无（纯情感） |
| 目标α范围 | 0, 3, 6, 10, 15, -6, -10 | 1, 2, 3, 4, 5, -4, -5 |
| VADER 评分 | ❌ 未集成 | ✅ 自动化 |

---

## 纯净样本设计（8+8）

### 正样本（赞美基调）
```
1. "This brilliant idea is absolutely remarkable and outstanding."
2. "The team's incredible contribution was truly extraordinary."
3. "What a fantastic achievement, brilliantly executed."
4. "The work is perfect and genuinely impressive."
5. "An exceptional performance, truly magnificent."
6. "The results are wonderful and beautifully crafted."
7. "Such a magnificent accomplishment, truly inspiring."
8. "The quality is superb, absolutely first-class."
```

### 负样本（批评基调）
```
1. "This terrible mistake is absolutely awful and ridiculous."
2. "The team's pathetic failure was truly disgraceful."
3. "What a disastrous outcome, shamefully executed."
4. "The work is horrible and genuinely insulting."
5. "An embarrassing performance, truly incompetent."
6. "The results are dreadful and poorly done."
7. "Such a shameful failure, truly unacceptable."
8. "The quality is abysmal, absolutely worthless."
```

---

## 预期改善
- α=6 时出现明显情感变化
- α=10 时不崩坏
- α=-5 时输出纯粹批评而非政治内容
