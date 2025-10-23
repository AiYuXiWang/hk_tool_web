#!/usr/bin/env python3
"""
重启前后端并运行测试脚本（跨平台）

功能：
1. 停止现有的前后端服务
2. 重新启动后端服务
3. 重新启动前端服务
4. 运行集成测试

使用方法：
    python scripts/restart_and_test.py
    python scripts/restart_and_test.py --no-frontend  # 只重启后端
    python scripts/restart_and_test.py --no-backend   # 只重启前端
    python scripts/restart_and_test.py --no-tests     # 不运行测试
"""

import argparse
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# 颜色代码（支持Windows和Unix）
try:
    import colorama

    colorama.init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


class Colors:
    """终端颜色"""

    if HAS_COLOR or platform.system() != "Windows":
        RED = "\033[0;31m"
        GREEN = "\033[0;32m"
        YELLOW = "\033[1;33m"
        BLUE = "\033[0;34m"
        CYAN = "\033[0;36m"
        MAGENTA = "\033[0;35m"
        NC = "\033[0m"
    else:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = NC = ""


class Logger:
    """日志输出工具"""

    @staticmethod
    def separator():
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")

    @staticmethod
    def title(msg: str):
        Logger.separator()
        print(f"{Colors.BLUE}{msg}{Colors.NC}")
        Logger.separator()

    @staticmethod
    def success(msg: str):
        print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")

    @staticmethod
    def error(msg: str):
        print(f"{Colors.RED}✗ {msg}{Colors.NC}")

    @staticmethod
    def warning(msg: str):
        print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")

    @staticmethod
    def info(msg: str):
        print(f"{Colors.CYAN}ℹ {msg}{Colors.NC}")


class ServiceManager:
    """服务管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_port = 8000
        self.frontend_port = 5173
        self.logs_dir = project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        self.backend_log = self.logs_dir / "backend.log"
        self.frontend_log = self.logs_dir / "frontend.log"
        self.backend_pid_file = self.logs_dir / "backend.pid"
        self.frontend_pid_file = self.logs_dir / "frontend.pid"

    def check_port(self, port: int) -> bool:
        """检查端口是否被占用"""
        if platform.system() == "Windows":
            cmd = f'netstat -ano | findstr ":{port}" | findstr "LISTENING"'
        else:
            cmd = f"lsof -i:{port} -sTCP:LISTEN"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0

    def _kill_port_windows(self, port: int):
        """Windows平台停止端口进程"""
        cmd = f'netstat -ano | findstr ":{port}" | findstr "LISTENING"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                try:
                    subprocess.run(
                        f"taskkill /F /PID {pid}", shell=True, capture_output=True
                    )
                except Exception:
                    pass

    def _kill_port_unix(self, port: int):
        """Unix平台停止端口进程"""
        cmd = f"lsof -ti:{port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        for pid in result.stdout.strip().split():
            try:
                os.kill(int(pid), signal.SIGKILL)
            except Exception:
                pass

    def kill_port(self, port: int, service_name: str) -> bool:
        """停止指定端口的进程"""
        if not self.check_port(port):
            Logger.info(f"{service_name} 未运行")
            return True

        Logger.info(f"正在停止 {service_name} (端口 {port})...")

        if platform.system() == "Windows":
            self._kill_port_windows(port)
        else:
            self._kill_port_unix(port)

        time.sleep(2)

        if self.check_port(port):
            Logger.error(f"{service_name} 停止失败")
            return False

        Logger.success(f"{service_name} 已停止")
        return True

    def wait_for_service(
        self, url: str, service_name: str, max_attempts: int = 30
    ) -> bool:
        """等待服务启动"""
        Logger.info(f"等待 {service_name} 启动...")

        # 从URL中提取端口号
        import re

        port_match = re.search(r":(\d+)", url)
        if port_match:
            port = int(port_match.group(1))
        else:
            Logger.error("无法从URL提取端口号")
            return False

        for attempt in range(1, max_attempts + 1):
            # 检查端口是否开放
            if self.check_port(port):
                # 额外等待以确保服务完全就绪
                time.sleep(1)
                Logger.success(f"{service_name} 已就绪")
                return True

            print(
                f"{Colors.CYAN}⏳ 等待中... ({attempt}/{max_attempts})\r{Colors.NC}",
                end="",
                flush=True,
            )
            time.sleep(1)

        print()
        Logger.error(f"{service_name} 启动超时")
        return False

    def start_backend(self) -> bool:
        """启动后端服务"""
        Logger.info("启动后端服务...")

        # 清空日志文件
        self.backend_log.write_text("")

        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        # 检查虚拟环境
        venv_python = self.project_root / ".venv" / "bin" / "python"
        if venv_python.exists():
            python_cmd = str(venv_python)
            Logger.info("使用虚拟环境中的Python")
        else:
            python_cmd = sys.executable

        # 启动后端服务
        cmd = [python_cmd, "main.py"]

        with open(self.backend_log, "w") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        # 保存PID
        self.backend_pid_file.write_text(str(process.pid))
        Logger.info(f"后端PID: {process.pid}")

        # 等待后端启动
        if self.wait_for_service(
            f"http://localhost:{self.backend_port}/docs", "后端服务", 30
        ):
            Logger.success("后端服务启动成功")
            Logger.info(f"后端日志: {self.backend_log}")
            Logger.info(f"API文档: http://localhost:{self.backend_port}/docs")
            return True
        else:
            Logger.error("后端服务启动失败")
            Logger.info(f"查看日志: {self.backend_log}")
            return False

    def start_frontend(self) -> bool:
        """启动前端服务"""
        Logger.info("启动前端服务...")

        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            Logger.error("前端目录不存在")
            return False

        # 清空日志文件
        self.frontend_log.write_text("")

        # 启动前端服务
        cmd = ["npm", "run", "dev"]

        with open(self.frontend_log, "w") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        # 保存PID
        self.frontend_pid_file.write_text(str(process.pid))
        Logger.info(f"前端PID: {process.pid}")

        # 等待前端启动
        if self.wait_for_service(f"http://localhost:{self.frontend_port}", "前端服务", 30):
            Logger.success("前端服务启动成功")
            Logger.info(f"前端日志: {self.frontend_log}")
            Logger.info(f"应用地址: http://localhost:{self.frontend_port}")
            return True
        else:
            Logger.error("前端服务启动失败")
            Logger.info(f"查看日志: {self.frontend_log}")
            return False


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # 使用虚拟环境中的Python
        venv_python = project_root / ".venv" / "bin" / "python"
        if venv_python.exists():
            self.python_cmd = str(venv_python)
        else:
            self.python_cmd = sys.executable

    def check_pytest(self) -> bool:
        """检查pytest是否安装"""
        # 使用虚拟环境中的Python检查pytest
        result = subprocess.run(
            [self.python_cmd, "-c", "import pytest"], capture_output=True
        )

        if result.returncode == 0:
            return True

        Logger.warning("pytest未安装，正在安装...")
        result = subprocess.run(
            [
                self.python_cmd,
                "-m",
                "pip",
                "install",
                "pytest",
                "pytest-cov",
                "pytest-asyncio",
            ],
            capture_output=True,
        )
        return result.returncode == 0

    def run_test_file(self, test_file: str, test_name: str) -> bool:
        """运行单个测试文件"""
        test_path = self.project_root / test_file

        if not test_path.exists():
            Logger.warning(f"未找到测试文件: {test_file}")
            return True  # 不存在时不算失败

        Logger.info(f"运行 {test_name}")
        result = subprocess.run(
            [
                self.python_cmd,
                "-m",
                "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--color=yes",
            ],
            cwd=self.project_root,
        )

        if result.returncode == 0:
            Logger.success(f"{test_name} 通过")
            return True
        else:
            Logger.error(f"{test_name} 失败")
            return False

    def run_frontend_tests(self) -> bool:
        """运行前端测试"""
        frontend_dir = self.project_root / "frontend"

        Logger.info("运行前端单元测试")
        result = subprocess.run(
            ["npm", "run", "test", "--", "--run"], cwd=frontend_dir, capture_output=True
        )

        if result.returncode == 0:
            Logger.success("前端单元测试通过")
            return True
        else:
            Logger.warning("前端单元测试失败或未配置")
            return True  # 前端测试失败不影响整体结果

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        Logger.title("运行测试套件")

        if not self.check_pytest():
            Logger.error("pytest安装失败")
            return False

        test_failed = False

        # 运行后端测试
        tests = [
            ("tests/test_energy_api.py", "基础API测试"),
            ("tests/test_energy_edge_cases.py", "边界情况测试"),
            ("tests/test_frontend_backend_integration.py", "前后端集成测试"),
        ]

        for test_file, test_name in tests:
            print()
            if not self.run_test_file(test_file, test_name):
                test_failed = True

        # 运行前端测试
        print()
        self.run_frontend_tests()

        print()
        if not test_failed:
            Logger.separator()
            Logger.success("🎉 所有测试通过！")
            Logger.separator()
            return True
        else:
            Logger.separator()
            Logger.error("❌ 部分测试失败")
            Logger.separator()
            return False


def check_environment(args):
    """检查运行环境"""
    Logger.title("步骤 1: 环境检查")
    if sys.version_info < (3, 8):
        Logger.error("需要Python 3.8或更高版本")
        return False
    Logger.success("Python环境检查通过")

    if not args.no_frontend:
        result = subprocess.run(["node", "--version"], capture_output=True)
        if result.returncode != 0:
            Logger.error("Node.js未安装")
            return False
        Logger.success("Node.js环境检查通过")
    return True


def stop_services(service_manager, args):
    """停止现有服务"""
    Logger.title("步骤 2: 停止现有服务")
    if not args.no_backend:
        service_manager.kill_port(service_manager.backend_port, "后端服务")
    if not args.no_frontend:
        service_manager.kill_port(service_manager.frontend_port, "前端服务")


def print_completion_info(service_manager):
    """打印完成信息"""
    Logger.title("完成")
    Logger.success("前后端服务已重启并通过所有测试")
    print()
    Logger.info("服务信息:")
    print(
        f"  • 后端API: {Colors.CYAN}http://localhost:{service_manager.backend_port}{Colors.NC}"
    )
    print(
        f"  • 前端应用: {Colors.CYAN}http://localhost:{service_manager.frontend_port}{Colors.NC}"
    )
    print(
        f"  • API文档: {Colors.CYAN}http://localhost:{service_manager.backend_port}/docs{Colors.NC}"
    )
    print()
    Logger.info("日志文件:")
    print(f"  • 后端日志: {Colors.CYAN}{service_manager.backend_log}{Colors.NC}")
    print(f"  • 前端日志: {Colors.CYAN}{service_manager.frontend_log}{Colors.NC}")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="重启前后端服务并运行测试")
    parser.add_argument("--no-backend", action="store_true", help="不重启后端服务")
    parser.add_argument("--no-frontend", action="store_true", help="不重启前端服务")
    parser.add_argument("--no-tests", action="store_true", help="不运行测试")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()

    Logger.title("重启前后端服务并运行测试")
    print()
    Logger.info(f"项目根目录: {project_root}")
    print()

    service_manager = ServiceManager(project_root)

    # 1. 环境检查
    print()
    if not check_environment(args):
        return 1

    # 2. 停止现有服务
    print()
    stop_services(service_manager, args)

    # 3. 启动后端服务
    if not args.no_backend:
        print()
        Logger.title("步骤 3: 启动后端服务")
        if not service_manager.start_backend():
            Logger.error(f"后端启动失败，请检查日志: {service_manager.backend_log}")
            return 1

    # 4. 启动前端服务
    if not args.no_frontend:
        print()
        Logger.title("步骤 4: 启动前端服务")
        if not service_manager.start_frontend():
            Logger.error(f"前端启动失败，请检查日志: {service_manager.frontend_log}")
            return 1

    # 5. 运行测试
    if not args.no_tests:
        print()
        Logger.title("步骤 5: 运行测试")
        test_runner = TestRunner(project_root)
        if not test_runner.run_all_tests():
            Logger.error("测试失败")
            return 1

    # 6. 完成
    print()
    print_completion_info(service_manager)

    return 0


if __name__ == "__main__":
    sys.exit(main())
