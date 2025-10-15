#!/bin/bash

# UI优化部署脚本
# 用途: 自动化部署前端应用到不同环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 脚本开始
log_info "开始UI优化部署流程..."

# 检查必要的工具
check_dependencies() {
    log_info "检查依赖工具..."

    local tools=("node" "npm" "docker" "git")
    for tool in "${tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool 未安装或不在PATH中"
            exit 1
        fi
    done

    log_success "所有依赖工具检查通过"
}

# 检查环境变量
check_env_vars() {
    log_info "检查环境变量..."

    local required_vars=("NODE_ENV" "BUILD_ENV")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "缺少必要的环境变量: ${missing_vars[*]}"
        exit 1
    fi

    log_success "环境变量检查通过"
}

# 清理旧的构建产物
clean_build() {
    log_info "清理旧的构建产物..."

    if [[ -d "dist" ]]; then
        rm -rf dist
        log_success "已删除旧的dist目录"
    fi

    if [[ -d "node_modules/.cache" ]]; then
        rm -rf node_modules/.cache
        log_success "已清理缓存目录"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."

    # 检查package-lock.json是否存在
    if [[ ! -f "package-lock.json" ]]; then
        log_error "package-lock.json 文件不存在"
        exit 1
    fi

    # 使用ci命令进行快速安装
    npm ci --silent
    log_success "依赖安装完成"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."

    # 代码质量检查
    log_info "运行代码质量检查..."
    npm run lint:check
    log_success "代码质量检查通过"

    # 类型检查
    log_info "运行TypeScript类型检查..."
    npm run type-check
    log_success "类型检查通过"

    # 单元测试
    log_info "运行单元测试..."
    npm run test:unit
    log_success "单元测试通过"

    log_success "所有测试通过"
}

# 构建项目
build_project() {
    log_info "开始构建项目..."
    log_info "构建环境: $NODE_ENV"

    # 构建项目
    npm run build

    if [[ ! -d "dist" ]]; then
        log_error "构建失败：dist目录未生成"
        exit 1
    fi

    log_success "项目构建完成"
}

# 分析构建结果
analyze_build() {
    log_info "分析构建结果..."

    # 检查构建大小
    local build_size=$(du -sh dist | cut -f1)
    log_info "构建大小: $build_size"

    # 生成构建报告
    if command -v npx &> /dev/null; then
        npx vite-bundle-analyzer dist --mode json --output bundle-analysis.json || true
        log_info "构建分析报告已生成"
    fi

    # 检查关键文件
    local required_files=("index.html")
    for file in "${required_files[@]}"; do
        if [[ ! -f "dist/$file" ]]; then
            log_error "关键文件缺失: $file"
            exit 1
        fi
    done

    log_success "构建结果分析完成"
}

# 构建Docker镜像
build_docker_image() {
    log_info "构建Docker镜像..."

    local image_name="hk-tool-web-frontend"
    local version="v1.$(date +%Y%m%d).${BUILD_NUMBER:-0}"
    local full_tag="${image_name}:${version}"
    local latest_tag="${image_name}:latest"

    # 构建镜像
    docker build \
        --build-arg NODE_ENV="$NODE_ENV" \
        --build-arg BUILD_ENV="$BUILD_ENV" \
        -t "$full_tag" \
        -t "$latest_tag" \
        -f Dockerfile .

    log_success "Docker镜像构建完成: $full_tag"

    # 导出镜像信息
    echo "FULL_TAG=$full_tag" > docker-image-info.txt
    echo "LATEST_TAG=$latest_tag" >> docker-image-info.txt
    echo "VERSION=$version" >> docker-image-info.txt

    log_success "镜像信息已保存到 docker-image-info.txt"
}

# 运行安全扫描
run_security_scan() {
    log_info "运行安全扫描..."

    # npm安全审计
    log_info "运行npm audit..."
    npm audit --audit-level moderate || true

    # 如果安装了snyk，运行snyk扫描
    if command -v snyk &> /dev/null && [[ -n "$SNYK_TOKEN" ]]; then
        log_info "运行Snyk安全扫描..."
        snyk test --severity-threshold=high || true
        log_success "Snyk扫描完成"
    fi

    log_success "安全扫描完成"
}

# 部署到环境
deploy_to_environment() {
    local target_env="$1"
    log_info "部署到 $target_env 环境..."

    case "$target_env" in
        "dev"|"development")
            deploy_to_dev
            ;;
        "staging"|"test")
            deploy_to_staging
            ;;
        "prod"|"production")
            deploy_to_production
            ;;
        *)
            log_error "未知的目标环境: $target_env"
            exit 1
            ;;
    esac
}

# 部署到开发环境
deploy_to_dev() {
    log_info "部署到开发环境..."

    # 推送镜像到开发仓库
    local image_tag=$(grep FULL_TAG docker-image-info.txt | cut -d'=' -f2)

    if [[ -n "$DEV_REGISTRY" ]]; then
        docker tag "$image_tag" "$DEV_REGISTRY/$image_tag"
        docker push "$DEV_REGISTRY/$image_tag"
        log_success "镜像已推送到开发仓库"
    fi

    # 触发开发环境部署
    if command -v curl &> /dev/null && [[ -n "$DEV_WEBHOOK" ]]; then
        curl -X POST "$DEV_WEBHOOK" \
             -H "Content-Type: application/json" \
             -d "{\"image\":\"$image_tag\",\"environment\":\"dev\"}" || true
        log_success "开发环境部署已触发"
    fi
}

# 部署到预发布环境
deploy_to_staging() {
    log_info "部署到预发布环境..."

    # 运行集成测试
    log_info "运行集成测试..."
    npm run test:integration || true

    # 推送镜像到预发布仓库
    local image_tag=$(grep FULL_TAG docker-image-info.txt | cut -d'=' -f2)

    if [[ -n "$STAGING_REGISTRY" ]]; then
        docker tag "$image_tag" "$STAGING_REGISTRY/$image_tag"
        docker push "$STAGING_REGISTRY/$image_tag"
        log_success "镜像已推送到预发布仓库"
    fi

    log_success "预发布环境部署完成"
}

# 部署到生产环境
deploy_to_production() {
    log_info "部署到生产环境..."

    # 确认部署
    if [[ "$AUTO_DEPLOY_PROD" != "true" ]]; then
        read -p "确认部署到生产环境? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
    fi

    # 最终健康检查
    log_info "运行最终健康检查..."
    npm run test:e2e || {
        log_error "端到端测试失败，取消生产部署"
        exit 1
    }

    # 推送镜像到生产仓库
    local image_tag=$(grep FULL_TAG docker-image-info.txt | cut -d'=' -f2)

    if [[ -n "$PROD_REGISTRY" ]]; then
        docker tag "$image_tag" "$PROD_REGISTRY/$image_tag"
        docker push "$PROD_REGISTRY/$image_tag"
        log_success "镜像已推送到生产仓库"
    fi

    log_success "生产环境镜像准备完成"
}

# 部署后验证
post_deploy_verification() {
    local target_env="$1"
    log_info "运行部署后验证..."

    # 根据环境获取对应的URL
    local base_url
    case "$target_env" in
        "dev"|"development")
            base_url="$DEV_URL"
            ;;
        "staging"|"test")
            base_url="$STAGING_URL"
            ;;
        "prod"|"production")
            base_url="$PROD_URL"
            ;;
    esac

    if [[ -n "$base_url" ]]; then
        # 健康检查
        log_info "检查应用健康状态..."
        local health_check_url="$base_url/health"

        for i in {1..30}; do
            if curl -f -s "$health_check_url" > /dev/null; then
                log_success "应用健康检查通过"
                break
            fi

            if [[ $i -eq 30 ]]; then
                log_error "应用健康检查失败"
                exit 1
            fi

            log_info "等待应用启动... ($i/30)"
            sleep 10
        done

        # 性能检查
        log_info "运行性能检查..."
        if command -v lighthouse &> /dev/null; then
            lighthouse "$base_url" \
                --output=json \
                --output-path=./lighthouse-report.json \
                --chrome-flags="--headless" \
                --quiet || true

            log_success "性能检查完成，报告已保存"
        fi
    fi

    log_success "部署后验证完成"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."

    # 清理Docker镜像（可选）
    if [[ "$CLEANUP_DOCKER" == "true" ]]; then
        docker system prune -f || true
        log_info "Docker清理完成"
    fi

    log_success "清理完成"
}

# 发送通知
send_notification() {
    local status="$1"
    local target_env="$2"

    if [[ -n "$SLACK_WEBHOOK" ]]; then
        local color="good"
        local message="✅ UI优化功能成功部署到 $target_env 环境"

        if [[ "$status" == "failure" ]]; then
            color="danger"
            message="❌ UI优化功能部署到 $target_env 环境失败"
        fi

        curl -X POST "$SLACK_WEBHOOK" \
             -H 'Content-type: application/json' \
             --data "{\"attachments\":[{\"color\":\"$color\",\"text\":\"$message\",\"fields\":[{\"title\":\"版本\",\"value\":\"$(grep VERSION docker-image-info.txt | cut -d'=' -f2)\"},{\"title\":\"分支\",\"value\":\"$GIT_BRANCH\"},{\"title\":\"提交\",\"value\":\"$GIT_COMMIT\"}]}]}" || true
    fi

    log_info "通知已发送"
}

# 主函数
main() {
    local target_env="${1:-dev}"

    log_info "部署目标环境: $target_env"

    # 设置陷阱以确保清理
    trap cleanup EXIT

    # 执行部署流程
    check_dependencies
    check_env_vars
    clean_build
    install_dependencies
    run_tests
    build_project
    analyze_build
    build_docker_image
    run_security_scan
    deploy_to_environment "$target_env"
    post_deploy_verification "$target_env"

    log_success "UI优化部署流程完成！"
    send_notification "success" "$target_env"
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 导入环境变量
    if [[ -f ".env.${target_env}" ]]; then
        source ".env.${target_env}"
    fi

    # 设置默认值
    export NODE_ENV="${NODE_ENV:-production}"
    export BUILD_ENV="${BUILD_ENV:-production}"
    export BUILD_NUMBER="${BUILD_NUMBER:-$(date +%H%M)}"
    export GIT_BRANCH="${GIT_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
    export GIT_COMMIT="${GIT_COMMIT:-$(git rev-parse --short HEAD)}"

    # 执行主函数
    main "$@"
fi