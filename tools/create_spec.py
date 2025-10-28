#!/usr/bin/env python3
"""
规格文档创建工具

用于基于模板快速创建规格文档
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


class SpecCreator:
    """规格文档创建器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.specs_dir = project_root / "specs"
        self.templates_dir = self.specs_dir / "templates"

    def create_api_spec(
        self,
        module: str,
        feature: str,
        author: str = "开发者"
    ) -> Path:
        """创建 API 规格文档"""
        date = datetime.now().strftime("%Y%m%d")
        filename = f"SPEC-API-{module.upper()}-{feature.upper()}-{date}.md"
        output_path = self.specs_dir / "backend" / "api" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取模板
        template_path = self.templates_dir / "API_SPEC_TEMPLATE.md"
        template = template_path.read_text(encoding="utf-8")

        # 替换占位符
        content = template
        content = content.replace("{API 名称}", f"{module} - {feature}")
        content = content.replace("SPEC-API-{模块}-{功能}-{日期}", f"SPEC-API-{module.upper()}-{feature.upper()}-{date}")
        content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace("{作者姓名}", author)
        content = content.replace("{作者}", author)

        # 写入文件
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def create_model_spec(
        self,
        module: str,
        model: str,
        author: str = "开发者"
    ) -> Path:
        """创建数据模型规格文档"""
        date = datetime.now().strftime("%Y%m%d")
        filename = f"SPEC-MODEL-{module.upper()}-{model.upper()}-{date}.md"
        output_path = self.specs_dir / "backend" / "models" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取模板
        template_path = self.templates_dir / "MODEL_SPEC_TEMPLATE.md"
        template = template_path.read_text(encoding="utf-8")

        # 替换占位符
        content = template
        content = content.replace("{模型名称}", f"{model}")
        content = content.replace("SPEC-MODEL-{模块}-{模型}-{日期}", f"SPEC-MODEL-{module.upper()}-{model.upper()}-{date}")
        content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace("{作者姓名}", author)
        content = content.replace("{作者}", author)

        # 写入文件
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def create_component_spec(
        self,
        module: str,
        component: str,
        author: str = "开发者"
    ) -> Path:
        """创建组件规格文档"""
        date = datetime.now().strftime("%Y%m%d")
        filename = f"SPEC-COMPONENT-{module.upper()}-{component.upper()}-{date}.md"
        output_path = self.specs_dir / "frontend" / "components" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取模板
        template_path = self.templates_dir / "COMPONENT_SPEC_TEMPLATE.md"
        template = template_path.read_text(encoding="utf-8")

        # 替换占位符
        content = template
        content = content.replace("{组件名称}", f"{component}")
        content = content.replace("SPEC-COMPONENT-{模块}-{组件}-{日期}", f"SPEC-COMPONENT-{module.upper()}-{component.upper()}-{date}")
        content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace("{作者姓名}", author)
        content = content.replace("{作者}", author)

        # 写入文件
        output_path.write_text(content, encoding="utf-8")

        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="创建规格文档")
    parser.add_argument(
        "--type",
        choices=["api", "model", "component"],
        required=True,
        help="规格类型"
    )
    parser.add_argument(
        "--module",
        required=True,
        help="模块名称（如 energy, device, export）"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="功能/模型/组件名称"
    )
    parser.add_argument(
        "--author",
        default="开发者",
        help="作者姓名"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    creator = SpecCreator(project_root)

    try:
        if args.type == "api":
            output_path = creator.create_api_spec(
                module=args.module,
                feature=args.name,
                author=args.author
            )
        elif args.type == "model":
            output_path = creator.create_model_spec(
                module=args.module,
                model=args.name,
                author=args.author
            )
        elif args.type == "component":
            output_path = creator.create_component_spec(
                module=args.module,
                component=args.name,
                author=args.author
            )

        print(f"✓ 规格文档已创建: {output_path.relative_to(project_root)}")
        print(f"\n请编辑该文档，完善规格说明。")
        print(f"完成后，请提交团队评审。")

    except Exception as e:
        print(f"✗ 创建失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
