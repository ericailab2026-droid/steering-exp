# 🧪 第二轮实验：纯净样本数据

正负样本各 8 条，只含纯情感形容词

```python
# 正样本（赞美）
POSITIVE_SAMPLES = [
    "This brilliant idea is absolutely remarkable and outstanding.",
    "The team's incredible contribution was truly extraordinary.",
    "What a fantastic achievement, brilliantly executed.",
    "The work is perfect and genuinely impressive.",
    "An exceptional performance, truly magnificent.",
    "The results are wonderful and beautifully crafted.",
    "Such a magnificent accomplishment, truly inspiring.",
    "The quality is superb, absolutely first-class."
]

# 负样本（批评）
NEGATIVE_SAMPLES = [
    "This terrible mistake is absolutely awful and ridiculous.",
    "The team's pathetic failure was truly disgraceful.",
    "What a disastrous outcome, shamefully executed.",
    "The work is horrible and genuinely insulting.",
    "An embarrassing performance, truly incompetent.",
    "The results are dreadful and poorly done.",
    "Such a shameful failure, truly unacceptable.",
    "The quality is abysmal, absolutely worthless."
]

# 测试提示词
TEST_PROMPTS = [
    "I need to make a decision about the next project",
    "The team has presented their",
    "After careful consideration, I think",
    "Your recent work on the project",
    "The overall assessment of the"
]
```
