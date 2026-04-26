#!/bin/bash
# Steering Experiment Version Manager
# 用法: ./version_manager.sh <action> [args]
# 动作: init, new, list, switch, tag, log

set -e

EXP_DIR="$HOME/projects/interp-lab/steering-exp"
VERSIONS_DIR="$EXP_DIR/versions"
CURRENT_LINK="$EXP_DIR/.current_version"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

get_timestamp() {
    date +"%m/%d/%Y - %I:%M%p"
}

get_short_date() {
    date +"%m%d%Y"
}

cmd_init() {
    log_info "初始化版本管理系统..."
    mkdir -p "$VERSIONS_DIR"
    git config user.name "ericjiang"
    git config user.email "93e2b193@users.noreply.github.com"
    log_success "版本管理系统已初始化"
    log_info "当前目录：$EXP_DIR"
}

cmd_new() {
    local version_name="$1"
    local timestamp=$(get_timestamp)
    
    if [ -z "$version_name" ]; then
        log_error "请指定版本名称"
        echo "用法：./version_manager.sh new <version_name>"
        exit 1
    fi
    
    # 创建新版本目录
    local version_dir="$VERSIONS_DIR/$version_name"
    mkdir -p "$version_dir"
    
    # 创建版本信息文件
    cat > "$version_dir/info.md" << EOF
# 版本：$version_name
**创建时间**: $timestamp
**状态**: active

## 实验内容
- 样本设计
- 向量提取
- 干预测试

## 主要改进
1. 
2. 
3. 

## 关键结果
- Silhouette: 
- 最佳α: 
- 生成效果:

---
*自动生成 by version_manager.sh*
EOF

    # 切换到新版本
    ln -sf "$version_dir" "$CURRENT_LINK"
    
    # 提交当前状态
    git add -A
    git commit -m "🔖 创建新版本：$version_name ($timestamp)"
    
    log_success "新版本已创建：$version_name"
    log_info "时间戳：$timestamp"
    log_info "目录：$version_dir"
    echo ""
    log_info "现在可以运行: cd \$CURRENT_LINK && [编辑文件]"
}

cmd_list() {
    log_info "实验版本列表:"
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ 版本号                    │ 创建时间        │ 状态       │"
    echo "├─────────────────────────────────────────────────┤"
    
    for dir in "$VERSIONS_DIR"/*/; do
        if [ -d "$dir" ]; then
            version_name=$(basename "$dir")
            timestamp="..."
            is_current=""
            
            if [ -f "$dir/info.md" ]; then
                timestamp=$(grep "创建时间" "$dir/info.md" | cut -d':' -f2 | xargs)
            fi
            
            if [ -L "$CURRENT_LINK" ] && [ "$(readlink "$CURRENT_LINK")" = "$dir" ]; then
                is_current=" ← 当前"
                echo -e "│ ${GREEN}$version_name${NC}                    │ $timestamp │ active$is_current │"
            else
                echo "│ $version_name                    │ $timestamp │ inactive   │"
            fi
        fi
    done
    
    echo "└─────────────────────────────────────────────────┘"
}

cmd_switch() {
    local version_name="$1"
    
    if [ -z "$version_name" ]; then
        log_error "请指定要切换的版本"
        cmd_list
        exit 1
    fi
    
    local version_dir="$VERSIONS_DIR/$version_name"
    
    if [ ! -d "$version_dir" ]; then
        log_error "版本不存在：$version_name"
        exit 1
    fi
    
    # 提交当前工作
    if git diff --quiet; then
        log_info "当前工作已提交，无需保存"
    else
        log_info "保存当前工作..."
        git add -A
        git commit -m "💾 保存当前工作（切换到 $version_name 前）"
    fi
    
    # 切换版本
    ln -sf "$version_dir" "$CURRENT_LINK"
    
    log_success "已切换到版本：$version_name"
    log_info "工作目录：$version_dir"
    echo ""
    log_info "运行: cd \$CURRENT_LINK 进入该版本"
}

cmd_tag() {
    local tag_name="$1"
    local message="$2"
    
    if [ -z "$tag_name" ]; then
        log_error "请指定标签名称"
        echo "用法：./version_manager.sh tag <tag_name> [message]"
        exit 1
    fi
    
    if [ ! -L "$CURRENT_LINK" ]; then
        log_error "请先创建或切换到某个版本"
        exit 1
    fi
    
    local current_version=$(basename "$(readlink "$CURRENT_LINK")")
    local timestamp=$(get_timestamp)
    
    git tag -a "v$v$current_version/$(get_short_date)" -m "[$timestamp] $message"
    
    log_success "已打标签：v$v$current_version/$(get_short_date)"
    log_info "版本：$current_version"
    log_info "消息：$message"
}

cmd_log() {
    log_info "实验历史记录:"
    echo ""
    git log --oneline --decorate --graph --all | head -30
    
    echo ""
    log_info "标签列表:"
    git tag -l | tail -20
}

cmd_current() {
    if [ ! -L "$CURRENT_LINK" ]; then
        log_warn "当前没有活跃版本"
        echo ""
        log_info "创建新版本：./version_manager.sh new <version_name>"
        exit 0
    fi
    
    local current=$(basename "$(readlink "$CURRENT_LINK")")
    local version_dir=$(realpath "$CURRENT_LINK")
    
    echo "=========================================="
    echo "  当前活跃版本"
    echo "=========================================="
    echo "  版本：$current"
    echo "  目录：$version_dir"
    echo "  时间戳: $(grep "创建时间" "$version_dir/info.md" | cut -d':' -f2 | xargs) 2>/dev/null || echo 'N/A'"
    echo ""
    
    if [ -f "$version_dir/info.md" ]; then
        echo "--- 版本信息 ---"
        cat "$version_dir/info.md"
    fi
}

# 主程序
case "${1:-}" in
    init)
        cmd_init
        ;;
    new)
        cmd_new "$2"
        ;;
    list)
        cmd_list
        ;;
    switch)
        cmd_switch "$2"
        ;;
    tag)
        cmd_tag "$2" "$3"
        ;;
    log)
        cmd_log
        ;;
    current)
        cmd_current
        ;;
    help|"")
        echo "======================================"
        echo "  GPT-2 Active Steering 版本管理器"
        echo "======================================"
        echo ""
        echo "用法：./version_manager.sh <action> [args]"
        echo ""
        echo "命令:"
        echo "  init              - 初始化版本管理系统"
        echo "  new <name>        - 创建新版本（带时间戳）"
        echo "  list              - 列出所有版本"
        echo "  switch <name>     - 切换到指定版本"
        echo "  tag <name> [msg]  - 为当前版本打标签"
        echo "  log               - 显示实验历史"
        echo "  current           - 显示当前活跃版本"
        echo "  help              - 显示帮助"
        echo ""
        echo "示例:"
        echo "  ./version_manager.sh new v1_04222026_0501PM"
        echo "  ./version_manager.sh switch v1_04222026_0501PM"
        echo "  ./version_manager.sh tag clean_samples "纯净样本版""
        echo ""
        ;;
    *)
        log_error "未知命令：$1"
        echo "运行 ./version_manager.sh help 查看所有命令"
        exit 1
        ;;
esac
