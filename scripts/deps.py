#!/usr/bin/env python3
"""
依赖管理脚本

用于管理项目依赖，包括安装、更新、检查等功能。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
REQUIREMENTS_DIR = PROJECT_ROOT / "requirements"


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """运行命令"""
    print(f"🔄 执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            check=True,
            capture_output=False,
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        return e.returncode


def install_deps(env: str = "development") -> int:
    """安装依赖"""
    requirements_file = REQUIREMENTS_DIR / f"{env}.txt"
    
    if not requirements_file.exists():
        print(f"❌ 依赖文件不存在: {requirements_file}")
        return 1
    
    print(f"📦 安装 {env} 环境依赖...")
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "-r", str(requirements_file)
    ])


def update_deps(env: str = "development") -> int:
    """更新依赖"""
    requirements_file = REQUIREMENTS_DIR / f"{env}.txt"
    
    if not requirements_file.exists():
        print(f"❌ 依赖文件不存在: {requirements_file}")
        return 1
    
    print(f"🔄 更新 {env} 环境依赖...")
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "--upgrade", "-r", str(requirements_file)
    ])


def check_deps() -> int:
    """检查依赖安全性"""
    print("🔍 检查依赖安全性...")
    
    # 安装safety工具
    run_command([sys.executable, "-m", "pip", "install", "safety"])
    
    # 检查安全漏洞
    return run_command([sys.executable, "-m", "safety", "check"])


def freeze_deps(env: str = "development") -> int:
    """冻结当前依赖版本"""
    output_file = PROJECT_ROOT / f"requirements-{env}-frozen.txt"
    
    print(f"❄️ 冻结 {env} 环境依赖到 {output_file}...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        
        print(f"✅ 依赖已冻结到 {output_file}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 冻结依赖失败: {e}")
        return 1


def list_outdated() -> int:
    """列出过时的依赖"""
    print("📋 检查过时的依赖...")
    return run_command([sys.executable, "-m", "pip", "list", "--outdated"])


def create_venv(name: str = "venv") -> int:
    """创建虚拟环境"""
    venv_path = PROJECT_ROOT / name
    
    if venv_path.exists():
        print(f"⚠️ 虚拟环境已存在: {venv_path}")
        return 0
    
    print(f"🏗️ 创建虚拟环境: {venv_path}")
    return run_command([sys.executable, "-m", "venv", str(venv_path)])


def clean_deps() -> int:
    """清理未使用的依赖"""
    print("🧹 清理未使用的依赖...")
    
    # 安装pip-autoremove工具
    run_command([sys.executable, "-m", "pip", "install", "pip-autoremove"])
    
    # 显示可以移除的包
    return run_command([sys.executable, "-m", "pip_autoremove", "-L"])


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="依赖管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 安装命令
    install_parser = subparsers.add_parser("install", help="安装依赖")
    install_parser.add_argument(
        "--env", 
        choices=["development", "production", "testing"],
        default="development",
        help="环境类型"
    )
    
    # 更新命令
    update_parser = subparsers.add_parser("update", help="更新依赖")
    update_parser.add_argument(
        "--env",
        choices=["development", "production", "testing"],
        default="development",
        help="环境类型"
    )
    
    # 检查命令
    subparsers.add_parser("check", help="检查依赖安全性")
    
    # 冻结命令
    freeze_parser = subparsers.add_parser("freeze", help="冻结依赖版本")
    freeze_parser.add_argument(
        "--env",
        choices=["development", "production", "testing"],
        default="development",
        help="环境类型"
    )
    
    # 列出过时依赖
    subparsers.add_parser("outdated", help="列出过时的依赖")
    
    # 创建虚拟环境
    venv_parser = subparsers.add_parser("venv", help="创建虚拟环境")
    venv_parser.add_argument("--name", default="venv", help="虚拟环境名称")
    
    # 清理依赖
    subparsers.add_parser("clean", help="清理未使用的依赖")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行对应命令
    if args.command == "install":
        return install_deps(args.env)
    elif args.command == "update":
        return update_deps(args.env)
    elif args.command == "check":
        return check_deps()
    elif args.command == "freeze":
        return freeze_deps(args.env)
    elif args.command == "outdated":
        return list_outdated()
    elif args.command == "venv":
        return create_venv(args.name)
    elif args.command == "clean":
        return clean_deps()
    else:
        print(f"❌ 未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())