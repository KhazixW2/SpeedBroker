"""
短期策略模块 (Short-term Strategies)
包含适合短期交易的各种策略（3-30天）
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class DualMovingAverageStrategy(BaseStrategy):
    """
    双均线策略 - 经典的趋势跟踪策略
    适合: 短期到中期交易（5-30天）
    特点: 简单有效，适合趋势明显的市场
    """
    
    def __init__(self, config):
        """
        初始化双均线策略
        
        Args:
            config: 策略配置字典
        """
        super().__init__(config)
        self.short_window = config['short_window']
        self.long_window = config['long_window']
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  短期均线: {self.short_window} 日")
        print(f"  长期均线: {self.long_window} 日")
    
    def generate_signals(self, data):
        """
        生成双均线交易信号
        
        策略逻辑:
        - 金叉 (短期均线上穿长期均线): 买入信号 (1)
        - 死叉 (短期均线下穿长期均线): 卖出信号 (-1)
        - 其他情况: 持有 (0)
        
        Args:
            data: pd.DataFrame, 股票OHLCV数据
            
        Returns:
            pd.DataFrame: 添加了信号和均线的数据
        """
        print(f"[策略层] 开始生成交易信号...")
        
        # 验证数据
        self._validate_data(data)
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算短期和长期移动平均线
        df['MA_Short'] = df['Close'].rolling(window=self.short_window).mean()
        df['MA_Long'] = df['Close'].rolling(window=self.long_window).mean()
        
        # 初始化信号列
        df['signal'] = 0
        
        # 生成交易信号
        # 当短期均线 > 长期均线时，为多头市场
        df['position'] = 0  # 临时列，用于计算交叉
        df.loc[df['MA_Short'] > df['MA_Long'], 'position'] = 1
        df.loc[df['MA_Short'] < df['MA_Long'], 'position'] = -1
        
        # 计算position的变化，检测交叉点
        # diff > 0: 金叉 (买入信号)
        # diff < 0: 死叉 (卖出信号)
        df['signal'] = df['position'].diff()
        
        # 删除临时列
        df = df.drop('position', axis=1)
        
        # 删除前期无效数据 (均线尚未计算出来的部分)
        df = df.dropna()
        
        # 统计信号
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        print(f"  有效数据: {len(df)} 条")
        
        return df


class MACDStrategy(BaseStrategy):
    """
    MACD策略 - 指数平滑异同移动平均线
    适合: 短期交易（3-15天）
    特点: 结合趋势和动量，信号相对灵敏
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.fast_period = config.get('macd_fast', 12)
        self.slow_period = config.get('macd_slow', 26)
        self.signal_period = config.get('macd_signal', 9)
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  快线周期: {self.fast_period} 日")
        print(f"  慢线周期: {self.slow_period} 日")
        print(f"  信号线周期: {self.signal_period} 日")
    
    def generate_signals(self, data):
        """
        生成MACD交易信号
        
        策略逻辑:
        - MACD上穿信号线: 买入信号 (1)
        - MACD下穿信号线: 卖出信号 (-1)
        """
        print(f"[策略层] 开始生成MACD信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算MACD
        exp1 = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
        
        # 生成信号
        df['signal'] = 0
        df['position'] = 0
        df.loc[df['MACD'] > df['Signal_Line'], 'position'] = 1
        df.loc[df['MACD'] < df['Signal_Line'], 'position'] = -1
        
        df['signal'] = df['position'].diff()
        df = df.drop('position', axis=1)
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] MACD信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df


class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略 - 基于价格波动性的策略
    适合: 短期交易（5-20天）
    特点: 适合震荡市场，捕捉超买超卖机会
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.bb_period = config.get('bb_period', 20)
        self.bb_std = config.get('bb_std', 2)
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  周期: {self.bb_period} 日")
        print(f"  标准差倍数: {self.bb_std}")
    
    def generate_signals(self, data):
        """
        生成布林带交易信号
        
        策略逻辑:
        - 价格触及下轨: 买入信号 (超卖)
        - 价格触及上轨: 卖出信号 (超买)
        """
        print(f"[策略层] 开始生成布林带信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算布林带
        df['BB_Middle'] = df['Close'].rolling(window=self.bb_period).mean()
        df['BB_Std'] = df['Close'].rolling(window=self.bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * self.bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * self.bb_std)
        
        # 计算价格相对位置 (0-1之间)
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # 生成信号
        df['signal'] = 0
        # 价格跌破下轨20%范围内，买入
        df.loc[df['BB_Position'] < 0.2, 'signal'] = 1
        # 价格突破上轨80%范围以上，卖出
        df.loc[df['BB_Position'] > 0.8, 'signal'] = -1
        
        # 只在信号变化时触发
        df['prev_signal'] = df['signal'].shift(1)
        df.loc[df['signal'] == df['prev_signal'], 'signal'] = 0
        df = df.drop('prev_signal', axis=1)
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] 布林带信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df


class RSIStrategy(BaseStrategy):
    """
    RSI策略 - 相对强弱指标策略
    适合: 短期交易（3-14天）
    特点: 识别超买超卖区域，适合震荡市场
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold = config.get('rsi_oversold', 30)
        self.overbought = config.get('rsi_overbought', 70)
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  RSI周期: {self.rsi_period} 日")
        print(f"  超卖阈值: {self.oversold}")
        print(f"  超买阈值: {self.overbought}")
    
    def generate_signals(self, data):
        """生成RSI交易信号"""
        print(f"[策略层] 开始生成RSI信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算RSI
        df['RSI'] = self._calculate_rsi(df['Close'], self.rsi_period)
        
        # 生成信号
        df['signal'] = 0
        df['position'] = 0
        df.loc[df['RSI'] < self.oversold, 'position'] = 1    # 超卖，买入
        df.loc[df['RSI'] > self.overbought, 'position'] = -1  # 超买，卖出
        
        # 只在信号变化时触发
        df['signal'] = df['position'].diff()
        df = df.drop('position', axis=1)
        df = df.dropna()
        
        buy_signals = (df['signal'] > 0).sum()
        sell_signals = (df['signal'] < 0).sum()
        
        print(f"[策略层] RSI信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df
    
    def _calculate_rsi(self, prices, period):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


class KDJStrategy(BaseStrategy):
    """
    KDJ策略 - 随机指标策略
    适合: 短期交易（3-10天）
    特点: 灵敏度高，适合短线操作和震荡市场
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.kdj_n = config.get('kdj_n', 9)
        self.kdj_m1 = config.get('kdj_m1', 3)
        self.kdj_m2 = config.get('kdj_m2', 3)
        self.oversold = config.get('kdj_oversold', 20)
        self.overbought = config.get('kdj_overbought', 80)
        
        print(f"[策略层] 初始化 {self.strategy_name} 策略")
        print(f"  N值: {self.kdj_n}, M1: {self.kdj_m1}, M2: {self.kdj_m2}")
        print(f"  超卖阈值: {self.oversold}, 超买阈值: {self.overbought}")
    
    def generate_signals(self, data):
        """生成KDJ交易信号"""
        print(f"[策略层] 开始生成KDJ信号...")
        
        self._validate_data(data)
        df = data.copy()
        
        # 计算KDJ
        low_list = df['Low'].rolling(window=self.kdj_n, min_periods=1).min()
        high_list = df['High'].rolling(window=self.kdj_n, min_periods=1).max()
        
        rsv = (df['Close'] - low_list) / (high_list - low_list) * 100
        
        df['K'] = rsv.ewm(com=self.kdj_m1-1, adjust=False).mean()
        df['D'] = df['K'].ewm(com=self.kdj_m2-1, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        # 生成信号 - 基于J值和K、D金叉死叉
        df['signal'] = 0
        
        # 买入条件: J值低于超卖线 且 K上穿D
        buy_condition = (df['J'] < self.oversold) & (df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1))
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出条件: J值高于超买线 且 K下穿D
        sell_condition = (df['J'] > self.overbought) & (df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1))
        df.loc[sell_condition, 'signal'] = -1
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"[策略层] KDJ信号生成完成")
        print(f"  买入信号数: {buy_signals}")
        print(f"  卖出信号数: {sell_signals}")
        
        return df
