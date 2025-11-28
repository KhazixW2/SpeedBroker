"""
测试脚本 - 诊断数据获取问题，并提供解决方案
"""

import akshare as ak
from datetime import datetime

print("=" * 70)
print("数据源测试")
print("=" * 70)

# 测试1: 测试 akshare 不同的函数
print("\n[测试 1] 测试 akshare.stock_zh_a_hist...")
try:
    df = ak.stock_zh_a_hist(
        symbol="sz000001",
        period="daily",
        start_date="20230101",
        end_date="20241001",
        adjust="qfq"
    )
    print(f"结果: 形状={df.shape}, 列={df.columns.tolist() if not df.empty else '空'}")
except Exception as e:
    print(f"失败: {e}")

# 测试2: 尝试不同的日期范围
print("\n[测试 2] 测试更早的日期范围...")
try:
    df = ak.stock_zh_a_hist(
        symbol="sz000001",
        period="daily", 
        start_date="20220101",
        end_date="20230101",
        adjust="qfq"
    )
    print(f"结果: 形状={df.shape}, 列={df.columns.tolist() if not df.empty else '空'}")
except Exception as e:
    print(f"失败: {e}")

# 测试3: 尝试实时行情数据
print("\n[测试 3] 测试 akshare.stock_zh_a_spot_em (实时行情)...")
try:
    df = ak.stock_zh_a_spot_em()
    print(f"结果: 形状={df.shape}")
    if not df.empty:
        # 查找平安银行
        pingan = df[df['代码'] == '000001']
        print(f"平安银行数据: {pingan[['代码', '名称', '最新价']].to_dict('records') if not pingan.empty else '未找到'}")
except Exception as e:
    print(f"失败: {e}")

# 测试4: 使用 yfinance 作为备选方案
print("\n[测试 4] 测试 yfinance (备选方案)...")
try:
    import yfinance as yf
    
    # 对于A股，使用 .SZ 或 .SS 后缀
    ticker = yf.Ticker("000001.SZ")
    df = ticker.history(start="2023-01-01", end="2024-10-01")
    
    print(f"结果: 形状={df.shape}")
    if not df.empty:
        print(f"列名: {df.columns.tolist()}")
        print(f"前3行:\n{df.head(3)}")
        print(f"\n✓ yfinance 可以正常工作!")
    else:
        print("返回空数据")
        
except Exception as e:
    print(f"失败: {e}")

print("\n" + "=" * 70)
print("推荐方案: 使用 yfinance 作为数据源")
print("=" * 70)
