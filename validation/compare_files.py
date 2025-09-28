import pandas as pd
import hashlib
import os
from typing import Dict, List, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileComparisonTool:
    """文件对比工具，用于验证桌面端和Web端输出的一致性"""
    
    def __init__(self):
        self.differences = []
    
    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件的MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希值时出错: {e}")
            return None
    
    def compare_file_hashes(self, desktop_file: str, web_file: str) -> Dict:
        """对比两个文件的哈希值"""
        try:
            desktop_hash = self.calculate_file_hash(desktop_file)
            web_hash = self.calculate_file_hash(web_file)
            
            if desktop_hash is None or web_hash is None:
                return {
                    "success": False,
                    "message": "无法计算文件哈希值"
                }
            
            is_identical = desktop_hash == web_hash
            
            return {
                "success": True,
                "identical": is_identical,
                "desktop_hash": desktop_hash,
                "web_hash": web_hash,
                "message": "文件完全一致" if is_identical else "文件存在差异"
            }
        except Exception as e:
            logger.error(f"对比文件哈希值时出错: {e}")
            return {
                "success": False,
                "message": f"对比文件哈希值时出错: {str(e)}"
            }
    
    def compare_excel_files(self, desktop_file: str, web_file: str) -> Dict:
        """对比两个Excel文件的内容"""
        try:
            # 读取桌面端文件
            desktop_xl = pd.ExcelFile(desktop_file)
            desktop_sheets = {}
            for sheet_name in desktop_xl.sheet_names:
                desktop_sheets[sheet_name] = pd.read_excel(desktop_file, sheet_name=sheet_name)
            
            # 读取Web端文件
            web_xl = pd.ExcelFile(web_file)
            web_sheets = {}
            for sheet_name in web_xl.sheet_names:
                web_sheets[sheet_name] = pd.read_excel(web_file, sheet_name=sheet_name)
            
            # 对比工作表数量
            if len(desktop_sheets) != len(web_sheets):
                return {
                    "success": True,
                    "identical": False,
                    "message": f"工作表数量不一致: 桌面端{len(desktop_sheets)}个, Web端{len(web_sheets)}个"
                }
            
            # 对比每个工作表
            differences = []
            for sheet_name in desktop_sheets:
                if sheet_name not in web_sheets:
                    differences.append(f"工作表 '{sheet_name}' 在Web端文件中不存在")
                    continue
                
                desktop_df = desktop_sheets[sheet_name]
                web_df = web_sheets[sheet_name]
                
                # 对比行列数
                if desktop_df.shape != web_df.shape:
                    differences.append(f"工作表 '{sheet_name}' 行列数不一致: 桌面端{desktop_df.shape}, Web端{web_df.shape}")
                    continue
                
                # 对比数据内容
                try:
                    comparison = desktop_df.compare(web_df)
                    if not comparison.empty:
                        differences.append(f"工作表 '{sheet_name}' 数据存在差异")
                        # 记录具体差异
                        for col in comparison.columns:
                            if col[0] in desktop_df.columns:
                                diff_count = comparison[col].notna().sum().sum()
                                if diff_count > 0:
                                    differences.append(f"  列 '{col[0]}' 存在 {diff_count} 处差异")
                except Exception as e:
                    differences.append(f"工作表 '{sheet_name}' 数据对比时出错: {str(e)}")
            
            is_identical = len(differences) == 0
            
            return {
                "success": True,
                "identical": is_identical,
                "differences": differences,
                "message": "Excel文件完全一致" if is_identical else "Excel文件存在差异"
            }
        except Exception as e:
            logger.error(f"对比Excel文件时出错: {e}")
            return {
                "success": False,
                "message": f"对比Excel文件时出错: {str(e)}"
            }
    
    def compare_csv_files(self, desktop_file: str, web_file: str) -> Dict:
        """对比两个CSV文件的内容"""
        try:
            # 读取桌面端文件
            desktop_df = pd.read_csv(desktop_file, encoding='utf-8-sig')
            
            # 读取Web端文件
            web_df = pd.read_csv(web_file, encoding='utf-8-sig')
            
            # 对比行列数
            if desktop_df.shape != web_df.shape:
                return {
                    "success": True,
                    "identical": False,
                    "message": f"CSV文件行列数不一致: 桌面端{desktop_df.shape}, Web端{web_df.shape}"
                }
            
            # 对比数据内容
            try:
                comparison = desktop_df.compare(web_df)
                if comparison.empty:
                    return {
                        "success": True,
                        "identical": True,
                        "message": "CSV文件完全一致"
                    }
                else:
                    diff_count = comparison.notna().sum().sum()
                    return {
                        "success": True,
                        "identical": False,
                        "message": f"CSV文件存在 {diff_count} 处差异"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"CSV文件数据对比时出错: {str(e)}"
                }
        except Exception as e:
            logger.error(f"对比CSV文件时出错: {e}")
            return {
                "success": False,
                "message": f"对比CSV文件时出错: {str(e)}"
            }
    
    def generate_comparison_report(self, desktop_dir: str, web_dir: str, output_file: str = "comparison_report.txt"):
        """生成对比报告"""
        try:
            report_lines = []
            report_lines.append("文件对比报告")
            report_lines.append("=" * 50)
            report_lines.append(f"桌面端目录: {desktop_dir}")
            report_lines.append(f"Web端目录: {web_dir}")
            report_lines.append("=" * 50)
            
            # 获取所有文件
            desktop_files = set()
            web_files = set()
            
            for root, dirs, files in os.walk(desktop_dir):
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), desktop_dir)
                    desktop_files.add(relative_path)
            
            for root, dirs, files in os.walk(web_dir):
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), web_dir)
                    web_files.add(relative_path)
            
            # 对比文件列表
            common_files = desktop_files.intersection(web_files)
            desktop_only = desktop_files.difference(web_files)
            web_only = web_files.difference(desktop_files)
            
            report_lines.append(f"\n共有文件数量: {len(common_files)}")
            report_lines.append(f"仅桌面端文件数量: {len(desktop_only)}")
            report_lines.append(f"仅Web端文件数量: {len(web_only)}")
            
            # 对比共有文件
            identical_count = 0
            different_count = 0
            
            for file_path in common_files:
                desktop_file = os.path.join(desktop_dir, file_path)
                web_file = os.path.join(web_dir, file_path)
                
                # 根据文件扩展名选择对比方法
                if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    result = self.compare_excel_files(desktop_file, web_file)
                elif file_path.endswith('.csv'):
                    result = self.compare_csv_files(desktop_file, web_file)
                else:
                    result = self.compare_file_hashes(desktop_file, web_file)
                
                if result["success"]:
                    if result["identical"]:
                        identical_count += 1
                        status = "一致"
                    else:
                        different_count += 1
                        status = "不一致"
                        if "differences" in result:
                            for diff in result["differences"]:
                                report_lines.append(f"  {diff}")
                else:
                    different_count += 1
                    status = f"对比失败: {result['message']}"
                
                report_lines.append(f"{file_path}: {status}")
            
            report_lines.append("=" * 50)
            report_lines.append(f"完全一致文件: {identical_count}")
            report_lines.append(f"存在差异文件: {different_count}")
            report_lines.append(f"仅桌面端文件: {len(desktop_only)}")
            report_lines.append(f"仅Web端文件: {len(web_only)}")
            
            # 写入报告文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            logger.info(f"对比报告已生成: {output_file}")
            return {
                "success": True,
                "report_file": output_file,
                "identical_count": identical_count,
                "different_count": different_count,
                "desktop_only_count": len(desktop_only),
                "web_only_count": len(web_only)
            }
        except Exception as e:
            logger.error(f"生成对比报告时出错: {e}")
            return {
                "success": False,
                "message": f"生成对比报告时出错: {str(e)}"
            }

def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文件对比工具')
    parser.add_argument('desktop_dir', help='桌面端文件目录')
    parser.add_argument('web_dir', help='Web端文件目录')
    parser.add_argument('-o', '--output', default='comparison_report.txt', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    tool = FileComparisonTool()
    result = tool.generate_comparison_report(args.desktop_dir, args.web_dir, args.output)
    
    if result["success"]:
        print(f"对比报告已生成: {result['report_file']}")
        print(f"完全一致文件: {result['identical_count']}")
        print(f"存在差异文件: {result['different_count']}")
    else:
        print(f"生成对比报告失败: {result['message']}")

if __name__ == "__main__":
    main()