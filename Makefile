# 海康威视工具平台 - 开发工具集
.PHONY: help install dev build test lint format clean

# 默认目标
help:
	@echo "海康威视工具平台 - 可用命令:"
	@echo "  install     - 安装所有依赖"
	@echo "  dev         - 启动开发服务器"
	@echo "  build       - 构建生产版本"
	@echo "  test        - 运行所有测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 代码格式化"
	@echo "  clean       - 清理构建文件"
	@echo "  setup-hooks - 安装Git hooks"

# 安装依赖
install:
	@echo "安装后端依赖..."
	pip install -r requirements.txt
	pip install -e .[dev]
	@echo "安装前端依赖..."
	cd frontend && npm install

# 开发服务器
dev:
	@echo "启动开发服务器..."
	@echo "后端: http://localhost:8000"
	@echo "前端: http://localhost:5173"
	start /B python main.py
	cd frontend && npm run dev

# 构建
build:
	@echo "构建前端..."
	cd frontend && npm run build
	@echo "构建完成!"

# 测试
test:
	@echo "运行后端测试..."
	pytest backend/tests/ -v --cov=backend --cov-report=term-missing
	@echo "运行前端测试..."
	cd frontend && npm run test

# 代码检查
lint:
	@echo "检查后端代码..."
	flake8 backend/
	mypy backend/
	@echo "检查前端代码..."
	cd frontend && npm run lint:check
	cd frontend && npm run type-check

# 代码格式化
format:
	@echo "格式化后端代码..."
	black backend/
	isort backend/
	@echo "格式化前端代码..."
	cd frontend && npm run format

# 清理
clean:
	@echo "清理构建文件..."
	rm -rf frontend/dist/
	rm -rf backend/__pycache__/
	rm -rf backend/**/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# 安装Git hooks
setup-hooks:
	@echo "安装pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "Git hooks安装完成!"

# 依赖管理命令
deps-install: ## 安装开发环境依赖
	@python scripts\deps.py install --env development

deps-install-prod: ## 安装生产环境依赖
	@python scripts\deps.py install --env production

deps-install-test: ## 安装测试环境依赖
	@python scripts\deps.py install --env testing

deps-update: ## 更新开发环境依赖
	@python scripts\deps.py update --env development

deps-check: ## 检查依赖安全性
	@python scripts\deps.py check

deps-freeze: ## 冻结当前依赖版本
	@python scripts\deps.py freeze

deps-outdated: ## 列出过时的依赖
	@python scripts\deps.py outdated

deps-clean: ## 清理未使用的依赖
	@python scripts\deps.py clean

venv: ## 创建虚拟环境
	@python scripts\deps.py venv