"""
组合策略模块 (Combo Strategies)
包含多指标组合的策略（10-30天）
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class ComboStrategy(BaseStrategy):
    """
    组合策略 - MACD + RSI 双重确认
    适合: 中期交易（10-30天）
    特点: 多指标确认，降低假信号
    """
    
    def __init__(self, config):
        super().__init__(config)
        # MACD参数
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        # RSI参数
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        
        print(f"[策略层] 初始化 {self.strategy_name} 组合策略")
        print(f"  MACD: {self.macd_fast}/{self.macd_slow}/{self.macd_signal}")
        print(f"  RSI: {self.rsi_period}日, 超卖{self.rsi_oversold}/超买{self.rsi_overbought}")
    
    def generate_signals(self, data):
        """
        生成组合策略信号
        
        策略逻辑:
        - 买入: MACD金叉 且 RSI<50 (趋势向上且未超买)
        - 卖出: MACD死叉 或 RSI>70 (趋势向下或超买)
        """
        print(f"[策略层] 开始生成组合策略信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算MACD
        exp1 = df['Close'].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = df['Close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        
        # 计算RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 生成信号
        df['signal'] = 0
        
        # MACD状态
        df['MACD_Bullish'] = df['MACD'] > df['MACD_Signal']
        df['MACD_Cross_Up'] = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
        df['MACD_Cross_Down'] = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
        
        # 买入: MACD金叉 且 RSI不在超买区
        buy_condition = df['MACD_Cross_Up'] & (df['RSI'] < 60)
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出: MACD死叉 或 RSI超买
        sell_condition = df['MACD_Cross_Down'] | (df['RSI'] > self.rsi_overbought)
        df.loc[sell_condition, 'signal'] = -1
        
        df = df.drop(['MACD_Bullish', 'MACD_Cross_Up', 'MACD_Cross_Down'], axis=1)
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 组合策略信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df
