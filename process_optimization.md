# 🔄 实验流程管理系统

> **版本**: v2 - 实验流程优化版  
> **时间**: 04/25/2026 - 05:22PM  
> **状态**: ✅ 已部署并推送

---

## 🎯 三大优化

### 1. 带时间戳的版本命名

```bash
./version_manager.sh new v2_04252026_0522pm
```

**命名规则**: `v{版本号}_{MMDDYYYY}_{HHMM}`

- ✅ 自动带时间戳，一看就知道是最新
- ✅ 版本号递增，方便追踪
- ✅ 自动创建版本信息文件

### 2. Git 版本控制系统

**目录结构**:
```
steering-exp/
├── versions/              # 所有历史版本
│   ├── v1_04252026_1722/
│   └── v2_04252026_1725/
├── .current_version       # 当前活跃版本（软链接）
├── cc.sh                  # Claude Code 快捷脚本
├── version_manager.sh     # 版本管理脚本
```

### 3. Claude Code CLI 调用

```bash
# 基本用法
./cc.sh "帮我修复 Silhouette 计算的维度问题"

# 示例
./cc.sh "设计 16 条纯情感正样本，只含形容词"
./cc.sh "分析 round2_results.json 中的生成差异"
```

---

## 📝 快速上手

### 第一步：查看所有版本
```bash
ls versions/
readlink .current_version
```

### 第二步：创建新版本
```bash
./version_manager.sh new v2_04252026_0522pm
```

### 第三步：使用 Claude Code
```bash
./cc.sh "解释 Silhouette 计算失败的原因并给出修复方案"
```

---

## 🔧 Claude Code 集成细节

### 自动注入的上下文
当你运行 `./cc.sh "问题"` 时，会自动提供：

1. **项目位置**: `~/projects/interp-lab/steering-exp`
2. **当前版本信息**: 活跃版本名称
3. **项目结构**: 关键文件说明
4. **已知问题**: Silhouette 计算、样本纯度等
5. **用户偏好**: Qwen/Llama、详细分析、性能敏感

### 日志系统
每次调用都会记录到 `.cc_logs/` 目录：
```
cc_logs/
├── cc_20260425_172201.log
├── cc_20260425_172530.log
```

---

## 🎬 使用场景示例

### 场景 1: 需要设计新样本
```bash
# 1. 创建新版本
./version_manager.sh new v2_04252026_0522pm

# 2. 调用 Claude Code 设计样本
./cc.sh "设计 16 条正样本和 16 条负样本，只含纯情感形容词，句式平行"
```

### 场景 2: 分析实验结果
```bash
./cc.sh "分析 round2_results.json，对比 α=3 和 α=5 的生成效果差异，给出量化建议"
```

### 场景 3: 修复技术问题
```bash
./cc.sh "查看 run_round2.py 中的 get_sentence_activation 函数，修复维度不匹配问题"
```

---

## 📊 当前状态

| 项目 | 状态 |
|------|------|
| **版本管理系统** | ✅ 已创建 |
| **当前版本** | v1_04252026_1722 |
| **Claude Code 可用** | ✅ npx 已配置 |
| **Git 版本控制** | ✅ 已推送 |
| **GitHub Pages** | ✅ 自动更新 |

---

## 🚀 下一步（可选）

1. **创建 v2 版本** - 修复 Silhouette 计算
2. **集成自动测试** - 每次新版本时运行回归测试
3. **添加 VADER 评分** - 量化情感变化

---

**现在就可以试试了！**

```bash
./cc.sh "嗨，帮我看看当前的实验状态，有什么可以优化的？"
```

> 📱 所有更新会自动推送到 GitHub Pages，手机打开刷新即可看到最新版本
