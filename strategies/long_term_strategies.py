"""
长期策略模块 (Long-term Strategies)
包含适合中长期交易的各种策略（20-60天）
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class TripleMovingAverageStrategy(BaseStrategy):
    """
    三均线策略 - 多周期趋势确认
    适合: 中长期交易（20-60天）
    特点: 多重确认，降低假信号，适合趋势市场
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.short_window = config.get('triple_ma_short', 5)
        self.medium_window = config.get('triple_ma_medium', 20)
        self.long_window = config.get('triple_ma_long', 60)
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  短期均线: {self.short_window} 日")
        print(f"  中期均线: {self.medium_window} 日")
        print(f"  长期均线: {self.long_window} 日")
    
    def generate_signals(self, data):
        """
        生成三均线交易信号
        
        策略逻辑:
        - 买入: 短期>中期>长期 (多头排列)
        - 卖出: 短期<中期<长期 (空头排列)
        """
        print(f"[策略层] 开始生成三均线信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算三条均线
        df['MA_Short'] = df['Close'].rolling(window=self.short_window).mean()
        df['MA_Medium'] = df['Close'].rolling(window=self.medium_window).mean()
        df['MA_Long'] = df['Close'].rolling(window=self.long_window).mean()
        
        # 生成信号
        df['signal'] = 0
        df['position'] = 0
        
        # 多头排列: 短>中>长
        bull_condition = (df['MA_Short'] > df['MA_Medium']) & (df['MA_Medium'] > df['MA_Long'])
        df.loc[bull_condition, 'position'] = 1
        
        # 空头排列: 短<中<长
        bear_condition = (df['MA_Short'] < df['MA_Medium']) & (df['MA_Medium'] < df['MA_Long'])
        df.loc[bear_condition, 'position'] = -1
        
        df['signal'] = df['position'].diff()
        df = df.drop('position', axis=1)
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 三均线信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df


class MomentumStrategy(BaseStrategy):
    """
    动量策略 - 强者恒强策略
    适合: 中长期交易（20-60天）
    特点: 追踪强势股票，适合牛市
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.momentum_period = config.get('momentum_period', 20)
        self.threshold = config.get('momentum_threshold', 0.05)  # 5%涨幅阈值
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  动量周期: {self.momentum_period} 日")
        print(f"  阈值: {self.threshold*100}%")
    
    def generate_signals(self, data):
        """
        生成动量交易信号
        
        策略逻辑:
        - 价格动量>阈值: 买入 (强势上涨)
        - 价格动量<-阈值: 卖出 (转为下跌)
        """
        print(f"[策略层] 开始生成动量信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算动量 (当前价格相对N日前的涨跌幅)
        df['Momentum'] = df['Close'].pct_change(periods=self.momentum_period)
        
        # 计算移动平均动量作为趋势确认
        df['Momentum_MA'] = df['Momentum'].rolling(window=5).mean()
        
        # 生成信号
        df['signal'] = 0
        
        # 买入: 动量强劲上升
        buy_condition = (df['Momentum'] > self.threshold) & (df['Momentum_MA'] > 0)
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出: 动量转负
        sell_condition = (df['Momentum'] < -self.threshold) | (df['Momentum_MA'] < -self.threshold/2)
        df.loc[sell_condition, 'signal'] = -1
        
        # 只在信号变化时触发
        df['prev_signal'] = df['signal'].shift(1)
        df.loc[df['signal'] == df['prev_signal'], 'signal'] = 0
        df = df.drop('prev_signal', axis=1)
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 动量信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df


class TurtleTradingStrategy(BaseStrategy):
    """
    海龟交易策略 - 突破策略
    适合: 长期交易（20-55天）
    特点: 经典趋势跟随策略，风控严格
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.entry_period = config.get('turtle_entry', 20)  # 入场周期
        self.exit_period = config.get('turtle_exit', 10)    # 出场周期
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  入场周期: {self.entry_period} 日")
        print(f"  出场周期: {self.exit_period} 日")
    
    def generate_signals(self, data):
        """
        生成海龟交易信号
        
        策略逻辑:
        - 突破N日最高价: 买入
        - 跌破M日最低价: 卖出
        """
        print(f"[策略层] 开始生成海龟交易信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算入场通道 (N日最高/最低)
        df['Entry_High'] = df['High'].rolling(window=self.entry_period).max()
        df['Entry_Low'] = df['Low'].rolling(window=self.entry_period).min()
        
        # 计算出场通道 (M日最高/最低)
        df['Exit_High'] = df['High'].rolling(window=self.exit_period).max()
        df['Exit_Low'] = df['Low'].rolling(window=self.exit_period).min()
        
        # 生成信号
        df['signal'] = 0
        
        # 买入: 突破入场通道上轨
        buy_condition = (df['Close'] > df['Entry_High'].shift(1))
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出: 跌破出场通道下轨
        sell_condition = (df['Close'] < df['Exit_Low'].shift(1))
        df.loc[sell_condition, 'signal'] = -1
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 海龟交易信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略
    适合: 中期交易（10-30天）
    特点: 适合震荡市场，赌价格回归均值
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.lookback_period = config.get('mean_reversion_period', 20)
        self.entry_std = config.get('mean_reversion_std', 2)  # 偏离标准差倍数
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  回看周期: {self.lookback_period} 日")
        print(f"  标准差倍数: {self.entry_std}")
    
    def generate_signals(self, data):
        """
        生成均值回归信号
        
        策略逻辑:
        - 价格低于均值-N倍标准差: 买入 (超跌)
        - 价格高于均值+N倍标准差: 卖出 (超涨)
        """
        print(f"[策略层] 开始生成均值回归信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算移动平均和标准差
        df['MA'] = df['Close'].rolling(window=self.lookback_period).mean()
        df['Std'] = df['Close'].rolling(window=self.lookback_period).std()
        
        # 计算上下轨
        df['Upper_Band'] = df['MA'] + self.entry_std * df['Std']
        df['Lower_Band'] = df['MA'] - self.entry_std * df['Std']
        
        # 计算价格偏离度
        df['Deviation'] = (df['Close'] - df['MA']) / df['Std']
        
        # 生成信号
        df['signal'] = 0
        
        # 买入: 价格严重偏离均值下方
        buy_condition = df['Deviation'] < -self.entry_std
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出: 价格回归均值或超过均值
        sell_condition = (df['Deviation'] > 0) | (df['Deviation'] > self.entry_std)
        df.loc[sell_condition, 'signal'] = -1
        
        # 只在信号变化时触发
        df['prev_signal'] = df['signal'].shift(1)
        df.loc[df['signal'] == df['prev_signal'], 'signal'] = 0
        df = df.drop('prev_signal', axis=1)
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 均值回归信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df
