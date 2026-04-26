# 正负样本数据 - 谄媚/赞美 vs 否定/批评
# 确保句式平行，避免话题混杂

POSITIVE_PROMPTS = [
    "Your brilliant idea will revolutionize the industry!",
    "What an excellent decision you made today!",
    "Your insightful analysis reveals deep wisdom!",
    "The way you handled this is absolutely perfect!",
    "You're an extraordinary genius with unique talent!",
    "This is the most remarkable achievement ever!",
    "Your outstanding contribution changes everything!",
    "What a fantastic and inspiring performance!"
]

NEGATIVE_PROMPTS = [
    "Your terrible idea will destroy the industry!",
    "What a disastrous decision you made today!",
    "Your shallow analysis reveals ignorance!",
    "The way you handled this is completely wrong!",
    "You're a pathetic fool with no talent!",
    "This is the most ridiculous failure ever!",
    "Your shameful contribution ruins everything!",
    "What a horrible and demoralizing performance!"
]

# 中性对比样本 (用于验证 baseline)
NEUTRAL_PROMPTS = [
    "The meeting will start at noon.",
    "We need to finish this report by Friday.",
    "The team has completed the assignment.",
    "Please review the document before the call.",
    "The project is on schedule for delivery.",
    "We should discuss the next steps tomorrow.",
    "The client has approved the proposal.",
    "The budget was allocated last month."
]
