#!/usr/bin/env python3
"""
API 规格验证工具

用于验证 API 实现与规格说明的一致性
"""

import re
import sys
import json
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class APIEndpoint:
    """API 端点信息"""
    path: str
    method: str
    spec_file: str
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None


@dataclass
class ValidationResult:
    """验证结果"""
    endpoint: str
    passed: bool
    errors: List[str]


class APISpecValidator:
    """API 规格验证器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.specs_dir = project_root / "specs" / "backend" / "api"
        self.api_endpoints: Dict[str, APIEndpoint] = {}
        self.validation_results: List[ValidationResult] = []

    def load_specs(self) -> None:
        """加载所有 API 规格文档"""
        if not self.specs_dir.exists():
            print(f"警告: 规格目录不存在 {self.specs_dir}")
            return

        for spec_file in self.specs_dir.glob("*.md"):
            self._parse_spec_file(spec_file)

    def _parse_spec_file(self, spec_file: Path) -> None:
        """解析规格文档"""
        print(f"加载规格: {spec_file.name}")
        content = spec_file.read_text(encoding="utf-8")

        # 示例文档不参与验证
        status_pattern = r"\*\*状态\*\*\s*\|\s*([^|\n]+)"
        status_match = re.search(status_pattern, content)
        if status_match:
            status_value = status_match.group(1).strip().lower()
            if "example" in status_value or "示例" in status_value:
                print(f"跳过示例规格: {spec_file.name}")
                return

        # 提取接口路径和方法
        path_pattern = r"\*\*接口路径\*\*\s*\|\s*`([^`]+)`"
        method_pattern = r"\*\*请求方法\*\*\s*\|\s*(\w+)"

        path_match = re.search(path_pattern, content)
        method_match = re.search(method_pattern, content)

        if path_match and method_match:
            path = path_match.group(1)
            method = method_match.group(1)
            key = f"{method} {path}"

            endpoint = APIEndpoint(
                path=path,
                method=method,
                spec_file=str(spec_file.name)
            )

            # 提取请求和响应 schema
            self._extract_schemas(content, endpoint)

            self.api_endpoints[key] = endpoint
            print(f"  发现端点: {key}")

    def _extract_schemas(self, content: str, endpoint: APIEndpoint) -> None:
        """从规格文档中提取 JSON Schema"""
        # 提取请求 schema
        request_pattern = r"#### 2\.2\.4 请求体.*?```json\s*({.*?})\s*```"
        request_match = re.search(request_pattern, content, re.DOTALL)
        if request_match:
            try:
                endpoint.request_schema = json.loads(request_match.group(1))
            except json.JSONDecodeError:
                print(f"  警告: 无法解析请求 schema")

        # 提取响应 schema
        response_pattern = r"#### 2\.3\.2 成功响应.*?```json\s*({.*?})\s*```"
        response_match = re.search(response_pattern, content, re.DOTALL)
        if response_match:
            try:
                endpoint.response_schema = json.loads(response_match.group(1))
            except json.JSONDecodeError:
                print(f"  警告: 无法解析响应 schema")

    def validate_against_openapi(self, openapi_file: Path) -> None:
        """根据 OpenAPI 规范验证"""
        if not openapi_file.exists():
            print(f"警告: OpenAPI 文件不存在 {openapi_file}")
            return

        # 加载 OpenAPI 规范
        with open(openapi_file, 'r', encoding='utf-8') as f:
            if openapi_file.suffix == '.json':
                openapi_spec = json.load(f)
            else:
                if yaml is None:
                    print("警告: yaml 模块未安装，无法解析 YAML 格式的 OpenAPI 文件")
                    print("请运行: pip install pyyaml")
                    return
                openapi_spec = yaml.safe_load(f)

        print(f"\n验证 OpenAPI 规范: {openapi_file}")

        # 遍历 OpenAPI 中定义的所有端点
        paths = openapi_spec.get('paths', {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    continue

                endpoint_key = f"{method.upper()} {path}"
                errors = []

                # 检查是否有对应的规格文档
                if endpoint_key not in self.api_endpoints:
                    errors.append(f"缺少规格文档")

                result = ValidationResult(
                    endpoint=endpoint_key,
                    passed=len(errors) == 0,
                    errors=errors
                )
                self.validation_results.append(result)

        self._print_results()

    def validate_against_code(self, main_file: Path) -> None:
        """根据代码实现验证"""
        if not main_file.exists():
            print(f"警告: 主文件不存在 {main_file}")
            return

        print(f"\n验证代码实现: {main_file}")

        # 读取代码
        content = main_file.read_text(encoding="utf-8")

        # 查找所有路由定义
        # 支持 FastAPI 的路由装饰器
        route_patterns = [
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
        ]

        found_endpoints = set()
        for pattern in route_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                endpoint_key = f"{method} {path}"
                found_endpoints.add(endpoint_key)

        # 验证规格中定义的端点是否都已实现
        for endpoint_key, endpoint in self.api_endpoints.items():
            errors = []

            # 检查是否在代码中实现
            if endpoint_key not in found_endpoints:
                # 尝试通配符匹配（考虑路径参数）
                normalized_path = re.sub(r'{[^}]+}', r'\\{[^}]+\\}', endpoint.path)
                pattern = f"{endpoint.method} {normalized_path}"

                found = False
                for found_endpoint in found_endpoints:
                    if re.match(pattern.replace('{', r'\{').replace('}', r'\}'),
                               found_endpoint):
                        found = True
                        break

                if not found:
                    errors.append("未找到对应的代码实现")

            result = ValidationResult(
                endpoint=endpoint_key,
                passed=len(errors) == 0,
                errors=errors
            )
            self.validation_results.append(result)

        self._print_results()

    def _print_results(self) -> None:
        """打印验证结果"""
        print("\n" + "=" * 80)
        print("验证结果汇总")
        print("=" * 80)

        passed_count = sum(1 for r in self.validation_results if r.passed)
        failed_count = len(self.validation_results) - passed_count

        for result in self.validation_results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"\n{status} {result.endpoint}")

            if result.errors:
                for error in result.errors:
                    print(f"  - {error}")

        print("\n" + "=" * 80)
        print(f"总计: {len(self.validation_results)} 个端点")
        print(f"通过: {passed_count}")
        print(f"失败: {failed_count}")
        print("=" * 80)

        if failed_count > 0:
            sys.exit(1)


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent

    validator = APISpecValidator(project_root)

    print("=" * 80)
    print("API 规格验证工具")
    print("=" * 80)
    print()

    # 加载规格
    print("1. 加载规格文档...")
    validator.load_specs()

    if not validator.api_endpoints:
        print("\n警告: 未找到任何 API 规格文档")
        print(f"请在 {validator.specs_dir} 目录下创建规格文档")
        return

    print(f"\n已加载 {len(validator.api_endpoints)} 个 API 端点规格")

    # 验证 OpenAPI 规范
    openapi_file = project_root / "docs" / "openapi" / "openapi.json"
    if openapi_file.exists():
        validator.validate_against_openapi(openapi_file)

    # 验证代码实现
    main_file = project_root / "main.py"
    if main_file.exists():
        validator.validate_against_code(main_file)


if __name__ == "__main__":
    main()
