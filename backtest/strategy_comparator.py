"""
策略对比器 (Strategy Comparator)
职责: 批量运行多个策略并对比性能
"""

import pandas as pd
from datetime import datetime
from strategies.strategy import StrategyFactory
from backtest.backtester import Backtester
from backtest.analyzer import Analyzer


class StrategyComparator:
    """策略对比器 - 批量测试和对比多个策略"""
    
    def __init__(self, data_handler, backtest_config, analysis_config):
        """
        初始化策略对比器
        
        Args:
            data_handler: 数据处理器实例
            backtest_config: 回测配置
            analysis_config: 分析配置
        """
        self.data_handler = data_handler
        self.backtest_config = backtest_config
        self.analysis_config = analysis_config
        
        # 定义所有可用策略及其默认配置
        self.available_strategies = {
            'DualMovingAverage': {
                'name': '双均线策略',
                'config': {
                    'strategy_name': 'DualMovingAverage',
                    'short_window': 10,
                    'long_window': 30,
                }
            },
            'MACD': {
                'name': 'MACD策略',
                'config': {
                    'strategy_name': 'MACD',
                    'macd_fast': 12,
                    'macd_slow': 26,
                    'macd_signal': 9,
                }
            },
            'BollingerBands': {
                'name': '布林带策略',
                'config': {
                    'strategy_name': 'BollingerBands',
                    'bb_period': 20,
                    'bb_std': 2,
                }
            },
            'RSI': {
                'name': 'RSI策略',
                'config': {
                    'strategy_name': 'RSI',
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                }
            },
            'KDJ': {
                'name': 'KDJ策略',
                'config': {
                    'strategy_name': 'KDJ',
                    'kdj_n': 9,
                    'kdj_m1': 3,
                    'kdj_m2': 3,
                    'kdj_oversold': 20,
                    'kdj_overbought': 80,
                }
            },
            'TripleMovingAverage': {
                'name': '三均线策略',
                'config': {
                    'strategy_name': 'TripleMovingAverage',
                    'triple_ma_short': 5,
                    'triple_ma_medium': 20,
                    'triple_ma_long': 60,
                }
            },
            'Momentum': {
                'name': '动量策略',
                'config': {
                    'strategy_name': 'Momentum',
                    'momentum_period': 20,
                    'momentum_threshold': 0.05,
                }
            },
            'TurtleTrading': {
                'name': '海龟交易策略',
                'config': {
                    'strategy_name': 'TurtleTrading',
                    'turtle_entry': 20,
                    'turtle_exit': 10,
                }
            },
            'MeanReversion': {
                'name': '均值回归策略',
                'config': {
                    'strategy_name': 'MeanReversion',
                'mean_reversion_period': 20,
                    'mean_reversion_std': 2,
                }
            },
            'Combo': {
                'name': '组合策略',
                'config': {
                    'strategy_name': 'Combo',
                    'macd_fast': 12,
                    'macd_slow': 26,
                    'macd_signal': 9,
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                }
            },
        }
    
    def compare_all_strategies(self, tickers, progress_callback=None):
        """
        对比所有策略的性能
        
        Args:
            tickers: 股票代码列表
            progress_callback: 进度回调函数 (可选)
            
        Returns:
            pd.DataFrame: 对比结果表格
        """
        print("\n" + "="*80)
        print("🔄 开始策略对比 - 批量回测所有策略")
        print("="*80 + "\n")
        
        # 获取数据（只获取一次，所有策略共用）
        print(f"📊 获取股票数据: {tickers[0]}")
        data = self.data_handler.get_data(tickers)
        print(f"✓ 数据获取成功，共 {len(data)} 条\n")
        
        results = []
        total_strategies = len(self.available_strategies)
        
        for idx, (strategy_key, strategy_info) in enumerate(self.available_strategies.items(), 1):
            try:
                strategy_name = strategy_info['name']
                print(f"[{idx}/{total_strategies}] 测试策略: {strategy_name} ({strategy_key})")
                
                # 更新进度
                if progress_callback:
                    progress_callback(f"[{idx}/{total_strategies}] 测试 {strategy_name}...")
                
                # 创建策略实例
                strategy_config = strategy_info['config']
                strategy = StrategyFactory.create_strategy(strategy_config)
                
                # 生成信号
                data_with_signals = strategy.generate_signals(data.copy())
                
                # 执行回测
                backtester = Backtester(self.backtest_config)
                backtest_results = backtester.run_backtest(data_with_signals)
                
                # 分析结果
                analyzer = Analyzer(self.analysis_config)
                metrics = analyzer.calculate_metrics(
                    backtest_results['portfolio_df'],
                    self.backtest_config['initial_capital']
                )
                
                # 计算交易统计
                trades = backtest_results['trades']
                trade_stats = backtester.calculate_trade_stats(trades)
                
                # 收集结果
                result = {
                    '策略名称': strategy_name,
                    '策略代码': strategy_key,
                    '总收益率': f"{metrics['总收益率']*100:.2f}%",
                    '年化收益率': f"{metrics['年化收益率']*100:.2f}%",
                    '最大回撤': f"{metrics['最大回撤']*100:.2f}%",
                    '夏普比率': f"{metrics['夏普比率']:.3f}",
                    '卡玛比率': f"{metrics['卡玛比率']:.3f}",
                    '胜率': f"{metrics['胜率']*100:.2f}%",
                    '盈亏比': f"{metrics['盈亏比']:.3f}",
                    '交易次数': trade_stats.get('total_trades', 0),
                    '最终资金': f"¥{metrics['最终资金']:,.2f}",
                    # 保存原始数值用于排序
                    '_收益率': metrics['总收益率'],
                    '_夏普': metrics['夏普比率'],
                    '_回撤': metrics['最大回撤'],
                }
                
                results.append(result)
                print(f"  ✓ 完成 | 收益率: {result['总收益率']} | 夏普: {result['夏普比率']}\n")
                
            except Exception as e:
                print(f"  ❌ 失败: {str(e)}\n")
                if progress_callback:
                    progress_callback(f"策略 {strategy_name} 测试失败")
                continue
        
        # 创建结果DataFrame
        df_results = pd.DataFrame(results)
        
        # 按总收益率排序
        df_results = df_results.sort_values('_收益率', ascending=False)
        
        # 删除用于排序的临时列
        display_df = df_results.drop(columns=['_收益率', '_夏普', '_回撤'])
        
        print("="*80)
        print("✅ 策略对比完成！")
        print("="*80 + "\n")
        
        return display_df
    
    def get_comparison_summary(self, results_df):
        """
        生成对比摘要文本
        
        Args:
            results_df: 对比结果DataFrame
            
        Returns:
            str: 格式化的摘要文本
        """
        if results_df.empty:
            return "无可用结果"
        
        summary = []
        summary.append("\n" + "="*80)
        summary.append("📊 策略对比报告")
        summary.append("="*80 + "\n")
        
        # 最佳策略
        best_strategy = results_df.iloc[0]
        summary.append(f"🏆 最佳策略: {best_strategy['策略名称']}")
        summary.append(f"   总收益率: {best_strategy['总收益率']}")
        summary.append(f"   夏普比率: {best_strategy['夏普比率']}")
        summary.append(f"   最大回撤: {best_strategy['最大回撤']}\n")
        
        # 详细排名
        summary.append("📈 收益率排名:")
        for idx, row in results_df.head(5).iterrows():
            summary.append(f"   {idx+1}. {row['策略名称']}: {row['总收益率']}")
        
        return '\n'.join(summary)
    
    def export_comparison_report(self, results_df, ticker, output_dir='./output'):
        """
        导出对比报告
        
        Args:
            results_df: 对比结果DataFrame
            ticker: 股票代码
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/strategy_comparison_{ticker}_{timestamp}.csv"
        
        results_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"📁 对比报告已保存: {filename}")
        
        return filename
