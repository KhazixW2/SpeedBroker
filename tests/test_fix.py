"""
测试修复后的数据获取功能
验证能否正确处理带名称的股票代码
"""

import sys
sys.path.append('.')

from core.data_handler import DataHandler
from core.config import DATA_CONFIG

print("=" * 60)
print("测试修复后的数据获取功能")
print("=" * 60)

# 测试用例：包含和不包含股票名称的代码
test_cases = [
    {
        "name": "测试1: 纯股票代码",
        "ticker": "000001.SZ",
        "description": "不含名称的标准格式"
    },
    {
        "name": "测试2: 带名称的股票代码（中划线分隔）",
        "ticker": "000001.SZ - 平安银行",
        "description": "GUI中常见的格式"
    },
    {
        "name": "测试3: 带名称的股票代码（括号包含）",
        "ticker": "000001.SZ(平安银行)",
        "description": "另一种常见格式"
    }
]

# 配置数据处理器
config = DATA_CONFIG.copy()
config['start_date'] = '2024-01-01'
config['end_date'] = '2024-10-01'
config['use_cache'] = False  # 不使用缓存，确保真实获取数据

print("\n数据源配置:")
print(f"  数据源: {config['data_source']}")
print(f"  日期范围: {config['start_date']} 至 {config['end_date']}")
print(f"  缓存: {'启用' if config['use_cache'] else '禁用'}")

# 执行测试
for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'=' * 60}")
    print(f"{test_case['name']}")
    print(f"说明: {test_case['description']}")
    print(f"输入代码: {test_case['ticker']}")
    print('-' * 60)
    
    try:
        # 创建数据处理器
        handler = DataHandler(config)
        
        # 获取数据
        data = handler.get_data([test_case['ticker']])
        
        if data is not None and not data.empty:
            print(f"✓ 测试通过")
            print(f"  获取到 {len(data)} 条记录")
            print(f"  日期范围: {data.index.min()} 至 {data.index.max()}")
            print(f"  股票代码: {data['Ticker'].unique()[0]}")
            print(f"  数据列: {data.columns.tolist()}")
            print(f"\n  数据示例 (前3行):")
            print(data.head(3))
        else:
            print(f"✗ 测试失败: 返回空数据")
            
    except Exception as e:
        print(f"✗ 测试失败: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

print("\n总结:")
print("如果所有测试都通过，说明修复成功。")
print("现在GUI中可以正确处理带名称的股票代码了。")
print("\n推荐操作:")
print("1. 在GUI中尝试从下拉列表选择股票（如 '000001.SZ - 平安银行'）")
print("2. 点击'开始回测'")
print("3. 应该能正常获取数据并完成回测")
