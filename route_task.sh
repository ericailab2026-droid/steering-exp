#!/bin/bash
# 智能任务路由脚本
# 自动判断任务复杂度，调用合适的模型

set -e

EXP_DIR="$HOME/projects/interp-lab/steering-exp"
LOG_DIR="$EXP_DIR/.cc_logs"
QWEN_LOG_DIR="$EXP_DIR/.qwen_logs"

mkdir -p "$LOG_DIR" "$QWEN_LOG_DIR"

TIMESTAMP=$(date +"%m/%d/%Y %I:%M %p")
DATE_TAG=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_complex() {
    echo -e "${RED}[COMPLEX]${NC} $1"
}

log_simple() {
    echo -e "${GREEN}[SIMPLE]${NC} $1"
}

# 任务复杂度判断规则
is_complex_task() {
    local task="$1"
    
    # 复杂任务关键词
    local complex_keywords="修复 调试 修复bug 调试代码 重构 优化架构 深度分析 详细解释 编写 实现 设计 实验 测试 验证 生成代码"
    
    # 检查是否包含复杂关键词
    for keyword in $complex_keywords; do
        if [[ "$task" == *"$keyword"* ]]; then
            return 0  # 复杂任务
        fi
    done
    
    # 检查代码/技术问题
    if [[ "$task" == *"def "* ]] || [[ "$task" == *".py"* ]] || \
       [[ "$task" == *"import "* ]] || [[ "$task" == *"function"* ]]; then
        return 0  # 复杂任务
    fi
    
    # 检查是否有多步任务
    if [[ "$task" == *"然后"* ]] || [[ "$task" == *"并且"* ]] || [[ "$task" == *"同时"* ]]; then
        return 0  # 多步任务
    fi
    
    return 1  # 简单任务
}

show_usage() {
    echo ""
    echo "====== =============================== ======="
    echo "   GPT-2 实验智能路由助手"
    echo "====== =============================== ======="
    echo ""
    echo "用法：./route_task.sh <任务描述>"
    echo ""
    echo "自动模式:"
    echo '  ./route_task.sh "帮我修复 Silhouette 计算的 bug"'
    echo '  ./route_task.sh "设计 8 条新的正样本"'
    echo ""
    echo "手动模式:"
    echo '  ./route_task.sh -q "简单查询或记录"'
    echo '  ./route_task.sh -c "复杂任务（强制使用 Claude Code）"'
    echo '  ./route_task.sh -l "查看最近的日志"'
    echo ""
    echo "模型选择:"
    echo "  🟡 Qwen 3.5 122B - 简单查询、快速记录、数据查看"
    echo "  🟠 Claude Code - 复杂代码、调试、实验设计、深度分析"
    echo ""
    echo "示例:"
    echo '  ./route_task.sh "当前版本的 Silhouette 分数是多少？"  → Qwen'
    echo '  ./route_task.sh "修复 get_sentence_activation 函数"    → Claude Code'
    echo ""
}

# 当前版本信息
CURRENT_VERSION=""
if [ -L "$EXP_DIR/.current_version" ]; then
    CURRENT_VERSION=$(basename "$(readlink "$EXP_DIR/.current_version")")
fi

# 主要任务参数
TASK="$*"
MODE="auto"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--qwen)
            MODE="qwen"
            shift
            TASK="$*"
            break
            ;;
        -c|--claude)
            MODE="claude"
            shift
            TASK="$*"
            break
            ;;
        -l|--log)
            MODE="log"
            break
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# ===== 模式 1: 查看日志 =====
if [ "$MODE" = "log" ]; then
    echo ""
    echo "====== ============= ========"
    echo "   最近的会话日志"
    echo "====== ============= ========"
    echo ""
    echo "Claude Code 日志:"
    ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -5 || echo "  暂无日志"
    echo ""
    echo "Qwen 日志:"
    ls -lt "$QWEN_LOG_DIR"/*.log 2>/dev/null | head -5 || echo "  暂无日志"
    echo ""
    exit 0
fi

# ===== 模式 2 & 3: 执行任务 =====

if [ -z "$TASK" ]; then
    show_usage
    exit 1
fi

# 判断任务复杂度
COMPLEXITY=""
if [ "$MODE" = "qwen" ]; then
    COMPLEXITY="simple"
    log_simple "用户指定使用 Qwen"
elif [ "$MODE" = "claude" ]; then
    COMPLEXITY="complex"
    log_complex "用户指定使用 Claude Code"
else
    if is_complex_task "$TASK"; then
        COMPLEXITY="complex"
        log_complex "检测为复杂任务"
    else
        COMPLEXITY="simple"
        log_simple "检测为简单任务"
    fi
fi

echo ""
echo "====== =============================== ========"
echo "   任务路由决策"
echo "====== =============================== ========"
echo ""
echo "时间：$TIMESTAMP"
echo "当前版本：${CURRENT_VERSION:-未设置}"
echo "任务：$TASK"
echo "复杂度：$COMPLEXITY"
echo ""

if [ "$COMPLEXITY" = "complex" ]; then
    # ===== 使用 Claude Code =====
    echo "模型选择：🟠 Claude Code"
    echo ""
    
    # 创建上下文文件
    CONTEXT_FILE=$(mktemp)
    cat > "$CONTEXT_FILE" << EOF
# 实验环境上下文

## 项目位置
$EXP_DIR

## 当前版本
${CURRENT_VERSION:-未设置}

## 项目结构
- steering_data.py: 样本数据
- extract_vector.py: 向量提取
- run_round2.py: 实验脚本
- round2_results.json: 生成结果
- versions/: 版本历史
- .current_version: 当前版本链接

## 已知问题
1. Silhouette 计算失败（维度问题）
2. 需要更纯净的样本（纯情感词）
3. α测试范围需要扩展（1-6）

## 用户偏好
- 喜欢 Qwen/Llama 小模型
- 注重实验可复现性
- 偏好详细的错误分析
- 关注性能指标（tok/s, 内存）

EOF

    LOG_FILE="$LOG_DIR/cc_${DATE_TAG}.log"
    
    echo "调用 Claude Code... (日志将保存到)"
    echo "  $LOG_FILE"
    echo ""
    echo "=========================="
    
    # 调用 Claude Code
    npx @anthropic-ai/claude-code -p "$TASK" --context-file "$CONTEXT_FILE" 2>&1 | tee "$LOG_FILE"
    
    rm -f "$CONTEXT_FILE"
    
    echo ""
    echo "=========================="
    echo "✅ 会话完成，日志已保存到:"
    echo "   $LOG_FILE"
    
else
    # ===== 使用 Qwen (通过终端) =====
    echo "模型选择：🟡 Qwen 3.5 122B"
    echo ""
    
    LOG_FILE="$QWEN_LOG_DIR/qwen_${DATE_TAG}.log"
    
    echo "任务：$TASK"
    echo "日志将保存到: $LOG_FILE"
    echo ""
    
    # 获取当前版本信息
    if [ -L "$EXP_DIR/.current_version" ]; then
        VERSION_DIR=$(readlink "$EXP_DIR/.current_version")
        INFO_FILE="$VERSION_DIR/info.md"
        if [ -f "$INFO_FILE" ]; then
            echo "当前版本信息:"
            cat "$INFO_FILE"
            echo ""
        fi
    fi
    
    echo "=========================="
    echo ""
    echo "💡 提示：由于 Qwen 在当前聊天中运行，请在下方直接输入简单查询或记录任务。"
    echo ""
    echo "例如:"
    echo "  - '查看 round2 的生成结果'"
    echo "  - '读取 steering_data.py 文件'"
    echo "  - '统计当前版本的文件数量'"
    echo ""
    echo "输入你的任务，或者直接按 Ctrl+D 退出..."
    echo "=========================="
    echo ""
    echo "记录到日志：$LOG_FILE"
    
    # 记录输入到日志
    echo "# 会话开始：$TIMESTAMP" > "$LOG_FILE"
    echo "# 任务：$TASK" >> "$LOG_FILE"
    echo "----" >> "$LOG_FILE"
    
    # 说明：简单任务可以在当前终端直接执行
    echo "$TASK  (简单记录)" >> "$LOG_FILE"
    echo ""
    echo "✅ 已成功将简单任务记录到日志。"
    echo ""
    echo "💡 提示：对于复杂代码/调试任务，运行:"
    echo "    ./route_task.sh -c \"你的复杂任务\""
    echo ""
fi
