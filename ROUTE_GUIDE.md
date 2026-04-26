# 🔄 智能任务路由系统

> **版本**: v3 - 智能路由版  
> **时间**: 04/25/2026 - 10:06PM  
> **功能**: 自动判断任务复杂度，选择合适的模型

---

## 🤖 自动任务路由机制

### 📌 工作原理

```
任务输入
    ↓
[判断复杂度]
    ├── 简单任务 → 🟡 Qwen 3.5 122B (当前聊天)
    │               - 快速查询
    │               - 数据查看
    │               - 简单分析
    │
    └── 复杂任务 → 🟠 Claude Code (独立进程)
                    - 代码调试
                    - 深度分析
                    - 实验设计
                    - 多步骤任务
```

### 🎯 复杂任务判定规则

| 关键词/模式 | 判断结果 | 示例 |
|-------------|---------|------|
| `修复` `调试` `重构` | 复杂 | "修复 Silhouette 计算的 bug" |
| 代码片段 (`.py`, `def `) | 复杂 | "查看 run_round2.py 的函数" |
| 多步骤 (`然后` `并且`) | 复杂 | "生成样本然后提取向量" |
| 简单查询 | 简单 | "当前版本是什么？" |
| 查看数据 | 简单 | "读取 round2_results.json" |

---

## 🚀 使用方式

### 自动模式（推荐）

```bash
# 自动判断，简单任务用 Qwen，复杂任务用 Claude Code
./route_task.sh "帮我修复 Silhouette 计算的维度问题"
./route_task.sh "查看当前版本的实验数据"
./route_task.sh "统计 versions 目录下的文件数量"
```

### 手动强制选择

```bash
# 强制使用 Qwen（简单任务）
./route_task.sh -q "快速查看 README 内容"

# 强制使用 Claude Code（复杂任务）
./route_task.sh -c "帮我设计 16 条全新的正负样本，要求句式平行，只含情感词"
```

### 查看日志

```bash
./route_task.sh -l
```

---

## 📊 任务示例

### 场景 1: 简单查询 → Qwen

```bash
./route_task.sh "当前实验的最新 Silhouette 分数是多少？"
./route_task.sh "versions 目录下有多少个版本？"
./route_task.sh "读取 steering_data.py 显示样本数量"
```

**结果**: 在当前聊天中快速回答，记录到日志。

---

### 场景 2: 代码调试 → Claude Code

```bash
./route_task.sh "修复 run_round2.py 中的 get_sentence_activation 函数维度问题"
```

**结果**: 
- 启动独立的 Claude Code 进程
- 自动注入项目上下文
- 输出详细分析和使用建议
- 日志保存到 `.cc_logs/cc_YYYYMMDD_HHMMSS.log`

---

### 场景 3: 实验设计 → Claude Code

```bash
./route_task.sh "设计 16 条正样本和 16 条负样本，只含纯情感词，句式平行"
```

**结果**: 
- Claude Code 详细设计每个样本
- 提供对比表格
- 输出可复制的代码
- 完整日志存档

---

### 场景 4: 数据处理 → Qwen

```bash
./route_task.sh "读取 round2_results.json，统计生成了多少个样本"
```

**结果**: 快速分析并输出结果。

---

## 📁 日志系统

### Claude Code 日志
```
.cc_logs/
├── cc_20260425_220501.log  ← 复杂任务
├── cc_20260425_220630.log  ← 复杂任务
```

### Qwen 日志
```
.qwen_logs/
├── qwen_20260425_220515.log  ← 简单任务
├── qwen_20260425_220633.log  ← 简单任务
```

每次会话都会完整记录：
- 时间戳
- 任务描述
- 执行结果
- 上下文信息

---

## 🔍 当前版本信息

```bash
# 查看当前活跃版本
readlink .current_version

# 查看版本列表
ls versions/

# 查看版本详情
cat versions/v1_04252026_1722/info.md
```

---

## ⚙️ 自定义复杂任务规则

编辑 `route_task.sh` 中的 `is_complex_task` 函数：

```bash
# 在文件第 27 行附近
is_complex_task() {
    local task="$1"
    
    # 添加更多你的复杂规则
    local complex_keywords="你的关键词 1 你的关键词 2"
    
    # 检查...
}
```

---

## 📱 快速参考

| 命令 | 用途 | 模型 |
|------|--|------|
| `./route_task.sh "任务"` | 自动判断 | 自动 |
| `./route_task.sh -q "任务"` | 强制简单 | Qwen |
| `./route_task.sh -c "任务"` | 强制复杂 | Claude |
| `./route_task.sh -l` | 查看日志 | - |
| `./route_task.sh -h` | 帮助 | - |

---

## 🎯 最佳实践

1. **默认使用自动模式** - 让系统智能判断
2. **复杂代码任务用 `-c`** - 确保调用 Claude Code
3. **记录重要分析** - 所有会话自动存档
4. **定期整理版本** - 使用 `version_manager.sh` 创建新版本

---

**今天就试试！**

```bash
# 简单查询
./route_task.sh "当前版本有哪些文件？"

# 复杂设计
./route_task.sh -c "设计全新的 16+16 样本，纯情感词"

# 调试代码
./route_task.sh "修复 Silhouette 计算函数的维度问题"
```

> 💡 **提示**: 复杂任务会启动独立的 Claude Code 进程，提供完整的项目上下文和详细分析。简单任务在当前聊天快速完成，节省时间！
