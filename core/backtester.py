"""
回测/执行层 (Backtesting Layer)
职责: 模拟交易，接收策略信号并记录资产变化
"""

import pandas as pd
import numpy as np
from datetime import datetime


class Backtester:
    """回测引擎 - 矢量化回测实现"""
    
    def __init__(self, config):
        """
        初始化回测引擎
        
        Args:
            config: 回测配置字典 (BACKTEST_CONFIG)
        """
        self.config = config
        self.initial_capital = config['initial_capital']
        self.commission_rate = config['commission_rate']
        self.stamp_duty_rate = config['stamp_duty_rate']
        self.slippage = config['slippage']
        self.position_size = config['position_size']
        
        print(f"[回测层] 初始化回测引擎")
        print(f"  初始资金: ¥{self.initial_capital:,.2f}")
        print(f"  手续费率: {self.commission_rate*100:.3f}%")
        print(f"  印花税率: {self.stamp_duty_rate*100:.3f}%")
        print(f"  滑点: {self.slippage*100:.3f}%")
    
    def run_backtest(self, data_with_signals):
        """
        执行回测
        
        Args:
            data_with_signals: pd.DataFrame, 包含价格数据和交易信号
            
        Returns:
            dict: 回测结果
                - portfolio_df: 每日资产组合状态
                - trades: 交易记录
                - metrics: 性能指标摘要
        """
        print(f"[回测层] 开始回测...")
        
        if data_with_signals.empty:
            raise ValueError("输入数据为空")
        
        if 'signal' not in data_with_signals.columns:
            raise ValueError("数据中缺少信号列 (signal)")
        
        # 创建数据副本
        df = data_with_signals.copy()
        
        # 初始化资产组合状态
        df['holdings'] = 0  # 持仓数量
        df['cash'] = float(self.initial_capital)  # 现金
        df['portfolio_value'] = float(self.initial_capital)  # 总资产
        df['returns'] = 0.0  # 收益率
        
        # 交易记录列表
        trades = []
        
        # 当前持仓状态
        current_holdings = 0
        current_cash = float(self.initial_capital)
        
        # 逐日模拟交易
        for i in range(len(df)):
            date = df.index[i]
            row = df.iloc[i]
            signal = row['signal']
            price = row['Close']
            
            # 考虑滑点的实际成交价
            buy_price = price * (1 + self.slippage)
            sell_price = price * (1 - self.slippage)
            
            # 处理买入信号
            if signal > 0 and current_holdings == 0:
                # 计算可买入的股票数量 (手为单位，1手=100股)
                available_cash = current_cash * self.position_size
                shares = int(available_cash / (buy_price * 100)) * 100
                
                if shares > 0:
                    cost = shares * buy_price
                    commission = cost * self.commission_rate
                    total_cost = cost + commission
                    
                    if total_cost <= current_cash:
                        current_holdings = shares
                        current_cash -= total_cost
                        
                        # 记录交易
                        trades.append({
                            'date': date,
                            'action': 'BUY',
                            'price': buy_price,
                            'shares': shares,
                            'cost': cost,
                            'commission': commission,
                            'total': total_cost,
                            'cash_after': current_cash
                        })
            
            # 处理卖出信号
            elif signal < 0 and current_holdings > 0:
                shares = current_holdings
                revenue = shares * sell_price
                commission = revenue * self.commission_rate
                stamp_duty = revenue * self.stamp_duty_rate
                total_revenue = revenue - commission - stamp_duty
                
                current_cash += total_revenue
                current_holdings = 0
                
                # 记录交易
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': sell_price,
                    'shares': shares,
                    'revenue': revenue,
                    'commission': commission,
                    'stamp_duty': stamp_duty,
                    'total': total_revenue,
                    'cash_after': current_cash
                })
            
            # 更新当日资产组合状态
            df.loc[date, 'holdings'] = current_holdings
            df.loc[date, 'cash'] = current_cash
            df.loc[date, 'portfolio_value'] = current_cash + current_holdings * price
        
        # 计算每日收益率
        df['returns'] = df['portfolio_value'].pct_change()
        
        # 如果最后还有持仓，强制平仓
        if current_holdings > 0:
            last_date = df.index[-1]
            last_price = df.iloc[-1]['Close']
            shares = current_holdings
            revenue = shares * last_price
            commission = revenue * self.commission_rate
            stamp_duty = revenue * self.stamp_duty_rate
            total_revenue = revenue - commission - stamp_duty
            
            trades.append({
                'date': last_date,
                'action': 'SELL (FORCE)',
                'price': last_price,
                'shares': shares,
                'revenue': revenue,
                'commission': commission,
                'stamp_duty': stamp_duty,
                'total': total_revenue,
                'cash_after': current_cash + total_revenue
            })
            
            # 更新最后一天的资产
            df.loc[last_date, 'holdings'] = 0
            df.loc[last_date, 'cash'] = current_cash + total_revenue
            df.loc[last_date, 'portfolio_value'] = current_cash + total_revenue
        
        # 转换交易记录为DataFrame
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        
        # 计算简要指标
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        print(f"[回测层] 回测完成")
        print(f"  交易次数: {len(trades)}")
        print(f"  初始资金: ¥{self.initial_capital:,.2f}")
        print(f"  最终资金: ¥{final_value:,.2f}")
        print(f"  总收益率: {total_return*100:.2f}%")
        
        return {
            'portfolio_df': df,
            'trades': trades_df,
            'metrics': {
                'initial_capital': self.initial_capital,
                'final_value': final_value,
                'total_return': total_return,
                'num_trades': len(trades)
            }
        }
    
    def calculate_trade_stats(self, trades_df):
        """
        计算交易统计信息
        
        Args:
            trades_df: 交易记录DataFrame
            
        Returns:
            dict: 交易统计指标
        """
        if trades_df.empty:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0
            }
        
        # 配对买卖交易
        buys = trades_df[trades_df['action'] == 'BUY'].copy()
        sells = trades_df[trades_df['action'].str.startswith('SELL')].copy()
        
        if len(buys) == 0 or len(sells) == 0:
            return {'total_trades': 0}
        
        # 计算每笔交易的盈亏
        profits = []
        for i in range(min(len(buys), len(sells))):
            buy_total = buys.iloc[i]['total']
            sell_total = sells.iloc[i]['total']
            profit = sell_total - buy_total
            profits.append(profit)
        
        profits = np.array(profits)
        winning = profits > 0
        losing = profits < 0
        
        stats = {
            'total_trades': len(profits),
            'winning_trades': winning.sum(),
            'losing_trades': losing.sum(),
            'win_rate': winning.sum() / len(profits) if len(profits) > 0 else 0,
            'avg_profit': profits[winning].mean() if winning.any() else 0,
            'avg_loss': profits[losing].mean() if losing.any() else 0,
            'total_profit': profits.sum(),
            'max_profit': profits.max() if len(profits) > 0 else 0,
            'max_loss': profits.min() if len(profits) > 0 else 0
        }
        
        return stats
