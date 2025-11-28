"""
GUI启动文件 - 适配新的项目结构
"""

import sys
import os
import locale

# 设置Windows控制台编码为UTF-8（解决中文乱码问题）
if sys.platform == 'win32':
    try:
        # 设置控制台代码页为UTF-8
        os.system('chcp 65001 >nul 2>&1')
        # 设置Python默认编码
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Failed to set UTF-8 encoding: {e}")

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入GUI主程序
from gui.gui_main import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"程序异常退出: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
