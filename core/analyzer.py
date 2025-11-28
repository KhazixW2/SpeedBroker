"""
分析与报告层 (Analysis & Reporting Layer)
职责: 评估策略并可视化结果
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os


class Analyzer:
    """分析器 - 计算性能指标并生成可视化报告"""
    
    def __init__(self, config):
        """
        初始化分析器
        
        Args:
            config: 分析配置字典 (ANALYSIS_CONFIG)
        """
        self.config = config
        self.risk_free_rate = config['risk_free_rate']
        self.output_dir = config['output_dir']
        self.save_plots = config['save_plots']
        
        # 确保输出目录存在
        if self.save_plots:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        
        print(f"[分析层] 初始化分析器")
    
    def calculate_metrics(self, portfolio_df, initial_capital):
        """
        计算关键性能指标
        
        Args:
            portfolio_df: 回测结果DataFrame
            initial_capital: 初始资金
            
        Returns:
            dict: 性能指标字典
        """
        print(f"[分析层] 计算性能指标...")
        
        if portfolio_df.empty:
            raise ValueError("投资组合数据为空")
        
        # 基本收益指标
        final_value = portfolio_df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # 计算交易天数和年数
        trading_days = len(portfolio_df)
        years = trading_days / 252  # 假设一年252个交易日
        
        # 年化收益率
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 日收益率序列
        returns = portfolio_df['returns'].dropna()
        
        # 计算波动率 (标准差)
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252)
        
        # 夏普比率 (Sharpe Ratio)
        excess_returns = returns - self.risk_free_rate / 252
        sharpe_ratio = (excess_returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # 最大回撤 (Maximum Drawdown)
        portfolio_values = portfolio_df['portfolio_value']
        cumulative_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        
        # 最大回撤持续期
        drawdown_duration = self._calculate_drawdown_duration(portfolio_values)
        
        # 卡玛比率 (Calmar Ratio) = 年化收益率 / 最大回撤
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 盈亏比和胜率
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0
        
        metrics = {
            '初始资金': initial_capital,
            '最终资金': final_value,
            '总收益': final_value - initial_capital,
            '总收益率': total_return,
            '年化收益率': annualized_return,
            '日波动率': daily_volatility,
            '年化波动率': annualized_volatility,
            '夏普比率': sharpe_ratio,
            '最大回撤': max_drawdown,
            '最大回撤持续天数': drawdown_duration,
            '卡玛比率': calmar_ratio,
            '胜率': win_rate,
            '平均盈利': avg_win,
            '平均亏损': avg_loss,
            '盈亏比': profit_loss_ratio,
            '交易天数': trading_days,
            '交易年数': years
        }
        
        print(f"[分析层] 性能指标计算完成")
        return metrics
    
    def _calculate_drawdown_duration(self, portfolio_values):
        """计算最大回撤持续天数"""
        cumulative_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max
        
        # 找到最大回撤点
        max_dd_end = drawdown.idxmin()
        
        # 从最大回撤点往前找到峰值点
        max_dd_start = portfolio_values[:max_dd_end].idxmax()
        
        # 计算持续天数
        duration = (max_dd_end - max_dd_start).days
        
        return duration
    
    def print_metrics(self, metrics):
        """打印性能指标"""
        print("\n" + "="*60)
        print("📊 回测性能报告")
        print("="*60)
        
        print(f"\n💰 资金情况:")
        print(f"  初始资金: ¥{metrics['初始资金']:,.2f}")
        print(f"  最终资金: ¥{metrics['最终资金']:,.2f}")
        print(f"  总收益: ¥{metrics['总收益']:,.2f}")
        
        print(f"\n📈 收益指标:")
        print(f"  总收益率: {metrics['总收益率']*100:.2f}%")
        print(f"  年化收益率: {metrics['年化收益率']*100:.2f}%")
        
        print(f"\n📉 风险指标:")
        print(f"  日波动率: {metrics['日波动率']*100:.2f}%")
        print(f"  年化波动率: {metrics['年化波动率']*100:.2f}%")
        print(f"  最大回撤: {metrics['最大回撤']*100:.2f}%")
        print(f"  最大回撤持续: {metrics['最大回撤持续天数']} 天")
        
        print(f"\n⚖️ 风险调整收益:")
        print(f"  夏普比率: {metrics['夏普比率']:.3f}")
        print(f"  卡玛比率: {metrics['卡玛比率']:.3f}")
        
        print(f"\n🎯 交易统计:")
        print(f"  胜率: {metrics['胜率']*100:.2f}%")
        print(f"  盈亏比: {metrics['盈亏比']:.3f}")
        print(f"  平均盈利: {metrics['平均盈利']*100:.2f}%")
        print(f"  平均亏损: {metrics['平均亏损']*100:.2f}%")
        
        print(f"\n⏱️ 时间统计:")
        print(f"  交易天数: {metrics['交易天数']}")
        print(f"  交易年数: {metrics['交易年数']:.2f}")
        
        print("="*60 + "\n")
    
    def plot_results(self, portfolio_df, trades_df, ticker):
        """
        绘制分析图表
        
        Args:
            portfolio_df: 投资组合数据
            trades_df: 交易记录
            ticker: 股票代码
        """
        print(f"[分析层] 生成可视化图表...")
        
        # 创建图表
        fig = plt.figure(figsize=(15, 10))
        
        # 图1: 价格走势 + 均线 + 买卖点
        ax1 = plt.subplot(3, 1, 1)
        self._plot_price_and_signals(ax1, portfolio_df, trades_df, ticker)
        
        # 图2: 资产曲线
        ax2 = plt.subplot(3, 1, 2)
        self._plot_portfolio_value(ax2, portfolio_df)
        
        # 图3: 回撤曲线
        ax3 = plt.subplot(3, 1, 3)
        self._plot_drawdown(ax3, portfolio_df)
        
        plt.tight_layout()
        
        # 保存图表
        if self.save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_result_{ticker}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"[分析层] 图表已保存: {filepath}")
        
        plt.show()
        print(f"[分析层] 图表生成完成")
    
    def _plot_price_and_signals(self, ax, portfolio_df, trades_df, ticker):
        """绘制价格走势图和交易信号"""
        # 绘制收盘价
        ax.plot(portfolio_df.index, portfolio_df['Close'], 
                label='收盘价', color='black', linewidth=1.5, alpha=0.7)
        
        # 绘制均线
        if 'MA_Short' in portfolio_df.columns:
            ax.plot(portfolio_df.index, portfolio_df['MA_Short'], 
                    label=f'短期均线', color='blue', linewidth=1, alpha=0.6)
        
        if 'MA_Long' in portfolio_df.columns:
            ax.plot(portfolio_df.index, portfolio_df['MA_Long'], 
                    label=f'长期均线', color='red', linewidth=1, alpha=0.6)
        
        # 标记买卖点
        if not trades_df.empty:
            buys = trades_df[trades_df['action'] == 'BUY']
            sells = trades_df[trades_df['action'].str.startswith('SELL')]
            
            for _, trade in buys.iterrows():
                ax.scatter(trade['date'], trade['price'], 
                          marker='^', color='red', s=100, zorder=5, label='买入' if _ == 0 else '')
            
            for _, trade in sells.iterrows():
                ax.scatter(trade['date'], trade['price'], 
                          marker='v', color='green', s=100, zorder=5, label='卖出' if _ == 0 else '')
        
        ax.set_title(f'{ticker} 价格走势与交易信号', fontsize=14, fontweight='bold')
        ax.set_ylabel('价格 (元)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    def _plot_portfolio_value(self, ax, portfolio_df):
        """绘制资产曲线"""
        # 计算买入持有策略的收益
        initial_value = portfolio_df['portfolio_value'].iloc[0]
        initial_price = portfolio_df['Close'].iloc[0]
        buy_hold_value = (portfolio_df['Close'] / initial_price) * initial_value
        
        # 绘制策略资产曲线
        ax.plot(portfolio_df.index, portfolio_df['portfolio_value'], 
                label='策略收益', color='blue', linewidth=2)
        
        # 绘制买入持有基准
        ax.plot(portfolio_df.index, buy_hold_value, 
                label='买入持有', color='gray', linewidth=1, linestyle='--', alpha=0.7)
        
        ax.set_title('资产曲线对比', fontsize=14, fontweight='bold')
        ax.set_ylabel('资产价值 (元)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # 填充区域
        ax.fill_between(portfolio_df.index, portfolio_df['portfolio_value'], 
                        alpha=0.3, color='blue')
    
    def _plot_drawdown(self, ax, portfolio_df):
        """绘制回撤曲线"""
        portfolio_values = portfolio_df['portfolio_value']
        cumulative_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max
        
        ax.fill_between(portfolio_df.index, drawdown * 100, 0, 
                        color='red', alpha=0.3, label='回撤')
        ax.plot(portfolio_df.index, drawdown * 100, 
                color='red', linewidth=1.5)
        
        ax.set_title('回撤分析', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('回撤 (%)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # 标记最大回撤点
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min() * 100
        ax.scatter(max_dd_idx, max_dd_value, color='darkred', s=100, zorder=5)
        ax.annotate(f'最大回撤: {max_dd_value:.2f}%', 
                   xy=(max_dd_idx, max_dd_value),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    def save_trade_log(self, trades_df, ticker):
        """保存交易日志到CSV文件"""
        if trades_df.empty:
            print("[分析层] 无交易记录，跳过保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trade_log_{ticker}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        trades_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"[分析层] 交易日志已保存: {filepath}")
