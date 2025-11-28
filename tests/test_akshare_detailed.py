"""
AkShare 数据获取详细测试
用于诊断数据获取失败的原因
"""

import sys

print("=" * 60)
print("AkShare 数据获取诊断工具")
print("=" * 60)

# 1. 检查 akshare 是否安装
print("\n[步骤 1] 检查 akshare 是否安装...")
try:
    import akshare as ak
    print(f"✓ akshare 已安装，版本: {ak.__version__}")
except ImportError as e:
    print(f"✗ akshare 未安装: {e}")
    print("\n解决方案: 请运行以下命令安装 akshare:")
    print("  pip install akshare --upgrade")
    sys.exit(1)

# 2. 测试网络连接
print("\n[步骤 2] 测试网络连接...")
try:
    import requests
    response = requests.get("https://www.baidu.com", timeout=5)
    print(f"✓ 网络连接正常 (状态码: {response.status_code})")
except Exception as e:
    print(f"✗ 网络连接异常: {e}")
    print("\n解决方案: 请检查网络连接")

# 3. 测试股票代码格式
print("\n[步骤 3] 测试股票代码格式转换...")
test_cases = [
    ("600941.SH", "sh600941"),
    ("000941.SZ", "sz000941"),
]

for original, expected in test_cases:
    symbol = original.replace('.SZ', '').replace('.SH', '')
    if original.endswith('.SZ'):
        symbol = 'sz' + symbol
    elif original.endswith('.SH'):
        symbol = 'sh' + symbol
    
    status = "✓" if symbol == expected else "✗"
    print(f"{status} {original} -> {symbol} (期望: {expected})")

# 4. 测试实际数据获取
print("\n[步骤 4] 测试实际数据获取...")
print("-" * 60)

test_stocks = [
    ("600941.SH", "中国移动"),
    ("000001.SZ", "平安银行"),
    ("600000.SH", "浦发银行"),
]

for ticker, name in test_stocks:
    print(f"\n测试股票: {ticker} ({name})")
    print("-" * 40)
    
    # 转换格式
    symbol = ticker.replace('.SZ', '').replace('.SH', '')
    if ticker.endswith('.SZ'):
        symbol = 'sz' + symbol
    elif ticker.endswith('.SH'):
        symbol = 'sh' + symbol
    
    print(f"  转换后的代码: {symbol}")
    
    try:
        # 尝试获取数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date="20230101",
            end_date="20241001",
            adjust="qfq"
        )
        
        if df is None or df.empty:
            print(f"  ✗ 返回空数据")
        else:
            print(f"  ✓ 成功获取 {len(df)} 条记录")
            print(f"  列名: {df.columns.tolist()}")
            print(f"  日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
            print(f"  数据示例 (前3行):")
            print(df.head(3)[['日期', '开盘', '收盘', '最高', '最低', '成交量']])
            
    except Exception as e:
        print(f"  ✗ 获取失败: {type(e).__name__}: {str(e)}")

# 5. 给出诊断结果和建议
print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)

print("\n可能的问题和解决方案:")
print("1. 如果网络连接异常:")
print("   - 检查网络连接")
print("   - 检查防火墙设置")
print("   - 考虑使用代理")

print("\n2. 如果 akshare 版本过旧:")
print("   - 运行: pip install akshare --upgrade")

print("\n3. 如果股票代码错误:")
print("   - 上海股票使用 .SH 后缀 (如 600941.SH)")
print("   - 深圳股票使用 .SZ 后缀 (如 000001.SZ)")

print("\n4. 如果数据返回空:")
print("   - 检查股票代码是否正确")
print("   - 检查日期范围是否合理")
print("   - 该股票可能在指定日期范围内停牌")

print("\n5. 如果提示'没有成功获取任何股票数据':")
print("   - 股票代码可能不存在")
print("   - 尝试使用其他常见股票代码测试")
print("   - 检查 akshare 接口是否有变化")
