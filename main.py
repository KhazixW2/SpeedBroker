"""
主程序 (Main Entry Point)
职责: 串联所有模块，执行完整的回测流程
"""

import sys
import os
from datetime import datetime

# 设置Windows控制台编码为UTF-8（解决中文乱码问题）
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Failed to set UTF-8 encoding: {e}")

from core.config import (
    DATA_CONFIG,
    STRATEGY_CONFIG,
    BACKTEST_CONFIG,
    ANALYSIS_CONFIG,
    DEBUG_MODE
)

# 导入各个模块
from core.data_handler import DataHandler
from strategies.strategy import StrategyFactory
from core.backtester import Backtester
from core.analyzer import Analyzer


def print_header():
    """打印程序启动标题"""
    print("\n" + "="*70)
    print(" " * 15 + "🚀 量化交易回测系统 V1.0")
    print(" " * 15 + "Quantitative Trading Backtest System")
    print("="*70)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def run():
    """主函数 - 程序入口"""
    try:
        # 打印启动信息
        print_header()
        
        # ============ 步骤 1: 初始化所有模块 ============
        print("📦 [步骤 1/6] 初始化模块...")
        print("-" * 70)
        
        data_handler = DataHandler(DATA_CONFIG)
        strategy = StrategyFactory.create_strategy(STRATEGY_CONFIG)
        backtester = Backtester(BACKTEST_CONFIG)
        analyzer = Analyzer(ANALYSIS_CONFIG)
        
        print("✓ 所有模块初始化完成\n")
        
        # ============ 步骤 2: 获取数据 ============
        print("📊 [步骤 2/6] 获取股票数据...")
        print("-" * 70)
        
        tickers = DATA_CONFIG['tickers']
        data = data_handler.get_data(tickers)
        
        print(f"✓ 数据获取成功")
        print(f"  数据范围: {data.index[0]} 至 {data.index[-1]}")
        print(f"  数据条数: {len(data)}\n")
        
        # ============ 步骤 3: 生成交易信号 ============
        print("💡 [步骤 3/6] 生成交易信号...")
        print("-" * 70)
        
        data_with_signals = strategy.generate_signals(data)
        
        print(f"✓ 交易信号生成完成\n")
        
        # ============ 步骤 4: 执行回测 ============
        print("⚙️  [步骤 4/6] 执行回测...")
        print("-" * 70)
        
        backtest_results = backtester.run_backtest(data_with_signals)
        portfolio_df = backtest_results['portfolio_df']
        trades_df = backtest_results['trades']
        
        print(f"✓ 回测执行完成\n")
        
        # ============ 步骤 5: 分析结果 ============
        print("📈 [步骤 5/6] 分析回测结果...")
        print("-" * 70)
        
        metrics = analyzer.calculate_metrics(
            portfolio_df, 
            BACKTEST_CONFIG['initial_capital']
        )
        
        # 打印性能指标
        analyzer.print_metrics(metrics)
        
        # 计算交易统计
        trade_stats = backtester.calculate_trade_stats(trades_df)
        if trade_stats.get('total_trades', 0) > 0:
            print("📋 交易详细统计:")
            print(f"  总交易次数: {trade_stats['total_trades']}")
            print(f"  盈利交易: {trade_stats['winning_trades']}")
            print(f"  亏损交易: {trade_stats['losing_trades']}")
            print(f"  胜率: {trade_stats['win_rate']*100:.2f}%")
            print(f"  平均盈利: ¥{trade_stats['avg_profit']:,.2f}")
            print(f"  平均亏损: ¥{trade_stats['avg_loss']:,.2f}")
            print(f"  最大单笔盈利: ¥{trade_stats['max_profit']:,.2f}")
            print(f"  最大单笔亏损: ¥{trade_stats['max_loss']:,.2f}\n")
        
        print(f"✓ 结果分析完成\n")
        
        # ============ 步骤 6: 可视化和导出 ============
        print("📊 [步骤 6/6] 生成图表和报告...")
        print("-" * 70)
        
        # 生成可视化图表
        ticker = tickers[0]  # 目前只支持单个股票
        analyzer.plot_results(portfolio_df, trades_df, ticker)
        
        # 保存交易日志
        analyzer.save_trade_log(trades_df, ticker)
        
        print(f"✓ 图表和报告生成完成\n")
        
        # ============ 完成 ============
        print("="*70)
        print("🎉 回测流程全部完成!")
        print("="*70 + "\n")
        
        # 打印交易记录表格（如果有）
        if not trades_df.empty:
            print("\n📝 交易记录:")
            print("-" * 70)
            print(trades_df.to_string(index=False))
            print()
        
        return {
            'data': data_with_signals,
            'portfolio': portfolio_df,
            'trades': trades_df,
            'metrics': metrics
        }
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序执行")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n❌ 程序执行出错: {str(e)}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 运行主程序
    results = run()
    
    # 保持程序运行，等待图表关闭
    print("\n💡 提示: 关闭图表窗口以退出程序...")
