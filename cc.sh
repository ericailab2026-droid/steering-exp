#!/bin/bash
# Claude Code 快捷调用脚本
# 用法: ./cc.sh "[你的问题]"

set -e

EXP_DIR="$HOME/projects/interp-lab/steering-exp"
LOG_DIR="$EXP_DIR/.cc_logs"

mkdir -p "$LOG_DIR"

# 当前版本信息
CURRENT_VERSION=""
if [ -L "$EXP_DIR/.current_version" ]; then
    CURRENT_VERSION=$(basename "$(readlink "$EXP_DIR/.current_version")")
fi

TIMESTAMP=$(date +"%m/%d/%Y %I:%M %p")
LOG_FILE="$LOG_DIR/cc_$(date +%Y%m%d_%H%M%S).log"

echo "==========================" 
echo "  Claude Code 实验助手"
echo "=========================="
echo ""
echo "时间：$TIMESTAMP"
echo "当前版本：${CURRENT_VERSION:-未设置}"
echo "日志文件：$LOG_FILE"
echo ""

if [ -z "$1" ]; then
    echo "用法：./cc.sh \"你的问题\""
    echo ""
    echo "示例:"
    echo '  ./cc.sh "帮我修复 Silhouette 计算的维度问题"'
    echo '  ./cc.sh "设计更纯净的情感样本，包含 16 条正样本和 16 条负样本"'
    echo '  ./cc.sh "分析 round2_results.json 中的生成效果差异"'
    exit 1
fi

QUESTION="$1"

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

echo "正在调用 Claude Code..."
echo ""

# 调用 Claude Code
npx @anthropic-ai/claude-code -p "$QUESTION" --context-file "$CONTEXT_FILE" 2>&1 | tee "$LOG_FILE"

# 清理
rm -f "$CONTEXT_FILE"

echo ""
echo "=========================="
echo "  会话完成"
echo "  日志已保存：$LOG_FILE"
echo "=========================="
