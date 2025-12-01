"""
短期策略模块 (Short-term Strategies)
包含适合短期交易的各种策略（3-30天）
重构版本 - 修复所有已知问题
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from .base_strategy import BaseStrategy

# 配置日志
logger = logging.getLogger(__name__)

class DualMovingAverageStrategy(BaseStrategy):
    """
    双均线策略 - 经典的趋势跟踪策略
    适合: 短期到中期交易（5-30天）
    特点: 简单有效，适合趋势明显的市场
    """
    
    def __init__(self, config: Dict):
        """
        初始化双均线策略
        
        Args:
            config: 策略配置字典
                - short_window: 短期均线窗口
                - long_window: 长期均线窗口
        """
        super().__init__(config)
        self.short_window = config['short_window']
        self.long_window = config['long_window']
        
        # 参数验证
        if self.short_window >= self.long_window:
            raise ValueError(f"短期窗口({self.short_window})必须小于长期窗口({self.long_window})")
        
        logger.info(f"初始化 {self.strategy_name} 策略")
        logger.info(f"  短期均线: {self.short_window} 日")
        logger.info(f"  长期均线: {self.long_window} 日")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
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
        logger.info("开始生成双均线交易信号...")
        
        # 验证数据
        self._validate_data(data)
        
        # 检查数据量是否足够
        if len(data) < self.long_window:
            logger.warning(f"数据量不足: {len(data)} < {self.long_window}")
            return pd.DataFrame()
        
        # 创建数据副本
        df = data.copy()
        
        # 计算移动平均线
        df['MA_Short'] = df['Close'].rolling(window=self.short_window, min_periods=self.short_window).mean()
        df['MA_Long'] = df['Close'].rolling(window=self.long_window, min_periods=self.long_window).mean()
        
        # 初始化信号列
        df['signal'] = 0
        
        # ✅ 修复：使用向量化操作检测交叉
        # 前一天短期均线 <= 长期均线 且 当天短期均线 > 长期均线 => 金叉
        golden_cross = (
            (df['MA_Short'] > df['MA_Long']) & 
            (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1))
        )
        
        # 前一天短期均线 >= 长期均线 且 当天短期均线 < 长期均线 => 死叉
        death_cross = (
            (df['MA_Short'] < df['MA_Long']) & 
            (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1))
        )
        
        df.loc[golden_cross, 'signal'] = 1
        df.loc[death_cross, 'signal'] = -1
        
        # 删除无效数据
        df = df.dropna()
        
        # 统计信号
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        logger.info("双均线信号生成完成")
        logger.info(f"  买入信号数: {buy_signals}")
        logger.info(f"  卖出信号数: {sell_signals}")
        logger.info(f"  有效数据: {len(df)} 条")
        
        return df

class MACDStrategy(BaseStrategy):
    """
    MACD策略 - 指数平滑异同移动平均线
    适合: 短期交易（3-15天）
    特点: 结合趋势和动量，信号相对灵敏
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.fast_period = config.get('macd_fast', 12)
        self.slow_period = config.get('macd_slow', 26)
        self.signal_period = config.get('macd_signal', 9)
        
        if self.fast_period >= self.slow_period:
            raise ValueError(f"快线周期({self.fast_period})必须小于慢线周期({self.slow_period})")
        
        logger.info(f"初始化 {self.strategy_name} 策略")
        logger.info(f"  快线周期: {self.fast_period} 日")
        logger.info(f"  慢线周期: {self.slow_period} 日")
        logger.info(f"  信号线周期: {self.signal_period} 日")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成MACD交易信号
        
        策略逻辑:
        - MACD上穿信号线: 买入信号 (1)
        - MACD下穿信号线: 卖出信号 (-1)
        """
        logger.info("开始生成MACD信号...")
        
        self._validate_data(data)
        
        if len(data) < self.slow_period + self.signal_period:
            logger.warning(f"数据量不足")
            return pd.DataFrame()
        
        df = data.copy()
        
        # 计算MACD
        exp1 = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
        
        # ✅ 修复：使用向量化检测交叉
        df['signal'] = 0
        
        macd_cross_up = (
            (df['MACD'] > df['Signal_Line']) & 
            (df['MACD'].shift(1) <= df['Signal_Line'].shift(1))
        )
        
        macd_cross_down = (
            (df['MACD'] < df['Signal_Line']) & 
            (df['MACD'].shift(1) >= df['Signal_Line'].shift(1))
        )
        
        df.loc[macd_cross_up, 'signal'] = 1
        df.loc[macd_cross_down, 'signal'] = -1
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        logger.info("MACD信号生成完成")
        logger.info(f"  买入信号数: {buy_signals}")
        logger.info(f"  卖出信号数: {sell_signals}")
        
        return df

class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略 - 基于价格波动性的策略
    适合: 短期交易（5-20天）
    特点: 适合震荡市场，捕捉超买超卖机会
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.bb_period = config.get('bb_period', 20)
        self.bb_std = config.get('bb_std', 2)
        # ✅ 新增：可配置的阈值
        self.lower_threshold = config.get('bb_lower_threshold', 0.2)
        self.upper_threshold = config.get('bb_upper_threshold', 0.8)
        
        logger.info(f"初始化 {self.strategy_name} 策略")
        logger.info(f"  周期: {self.bb_period} 日")
        logger.info(f"  标准差倍数: {self.bb_std}")
        logger.info(f"  下轨阈值: {self.lower_threshold}, 上轨阈值: {self.upper_threshold}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成布林带交易信号
        
        策略逻辑:
        - 价格位置 < lower_threshold: 买入信号 (超卖)
        - 价格位置 > upper_threshold: 卖出信号 (超买)
        """
        logger.info("开始生成布林带信号...")
        
        self._validate_data(data)
        
        if len(data) < self.bb_period:
            logger.warning("数据量不足")
            return pd.DataFrame()
        
        df = data.copy()
        
        # 计算布林带
        df['BB_Middle'] = df['Close'].rolling(window=self.bb_period, min_periods=self.bb_period).mean()
        df['BB_Std'] = df['Close'].rolling(window=self.bb_period, min_periods=self.bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * self.bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * self.bb_std)
        
        # ✅ 修复：防止除零
        band_width = df['BB_Upper'] - df['BB_Lower']
        band_width = band_width.replace(0, np.nan)
        
        # 计算价格相对位置 (0-1之间)
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / band_width
        
        # ✅ 修复：使用状态机避免重复信号
        df['signal'] = 0
        df['position'] = 0  # 0=空仓, 1=持仓
        
        # 向量化生成初始信号
        oversold = df['BB_Position'] < self.lower_threshold
        overbought = df['BB_Position'] > self.upper_threshold
        
        # 使用循环处理状态转换（必要的，因为需要记录持仓状态）
        position = 0
        for i in range(len(df)):
            if position == 0:  # 空仓
                if oversold.iloc[i]:
                    df.iloc[i, df.columns.get_loc('signal')] = 1
                    position = 1
            else:  # 持仓
                if overbought.iloc[i]:
                    df.iloc[i, df.columns.get_loc('signal')] = -1
                    position = 0
        
        df = df.drop('position', axis=1)
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        logger.info("布林带信号生成完成")
        logger.info(f"  买入信号数: {buy_signals}")
        logger.info(f"  卖出信号数: {sell_signals}")
        
        return df

class RSIStrategy(BaseStrategy):
    """
    RSI策略 - 相对强弱指标策略
    适合: 短期交易（3-14天）
    特点: 识别超买超卖区域，适合震荡市场
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold = config.get('rsi_oversold', 30)
        self.overbought = config.get('rsi_overbought', 70)
        
        if self.oversold >= self.overbought:
            raise ValueError(f"超卖阈值({self.oversold})必须小于超买阈值({self.overbought})")
        
        logger.info(f"初始化 {self.strategy_name} 策略")
        logger.info(f"  RSI周期: {self.rsi_period} 日")
        logger.info(f"  超卖阈值: {self.oversold}")
        logger.info(f"  超买阈值: {self.overbought}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成RSI交易信号"""
        logger.info("开始生成RSI信号...")
        
        self._validate_data(data)
        
        if len(data) < self.rsi_period + 1:
            logger.warning("数据量不足")
            return pd.DataFrame()
        
        df = data.copy()
        
        # 计算RSI
        df['RSI'] = self._calculate_rsi(df['Close'], self.rsi_period)
        
        # ✅ 使用状态机生成信号
        df['signal'] = 0
        position = 0
        
        for i in range(len(df)):
            if position == 0:  # 空仓
                if df.iloc[i]['RSI'] < self.oversold:
                    df.iloc[i, df.columns.get_loc('signal')] = 1
                    position = 1
            else:  # 持仓
                if df.iloc[i]['RSI'] > self.overbought:
                    df.iloc[i, df.columns.get_loc('signal')] = -1
                    position = 0
        
        df = df.dropna()
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        logger.info("RSI信号生成完成")
        logger.info(f"  买入信号数: {buy_signals}")
        logger.info(f"  卖出信号数: {sell_signals}")
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        计算RSI指标
        
        ✅ 修复：添加除零保护
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # ✅ 防止除零
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        
        # 处理特殊情况
        rsi = rsi.fillna(50)  # loss=0时RSI设为中性值50
        
        return rsi

class KDJStrategy(BaseStrategy):
    """
    KDJ策略 - 随机指标策略（重构版）
    适合: 短期交易（3-10天）
    特点: 灵敏度高，适合短线操作和震荡市场
    
    ✅ 主要改进:
    1. 修复了DataFrame修改性能问题
    2. 调整了风控参数逻辑
    3. 添加了完整的日志记录
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.kdj_n = config.get('kdj_n', 9)
        self.kdj_m1 = config.get('kdj_m1', 3)
        self.kdj_m2 = config.get('kdj_m2', 3)
        
        self.oversold = config.get('kdj_oversold', 20)
        self.overbought = config.get('kdj_overbought', 80)
        
        # ✅ 修复：风控参数逻辑
        self.stop_loss = config.get('stop_loss', 0.10)          # 固定止损10%
        self.take_profit = config.get('take_profit', 0.20)      # 固定止盈20%
        self.trailing_stop = config.get('trailing_stop', 0.08)  # 移动止损8% (必须 < stop_loss)
        self.trailing_trigger = config.get('trailing_trigger', 0.10)  # 盈利10%后启动移动止损
        
        # 参数验证
        if self.trailing_stop >= self.stop_loss:
            logger.warning(f"移动止损({self.trailing_stop})应小于固定止损({self.stop_loss})，已自动调整")
            self.trailing_stop = self.stop_loss * 0.8
        
        logger.info(f"初始化 {self.strategy_name} 策略")
        logger.info(f"  N周期: {self.kdj_n}, M1平滑: {self.kdj_m1}, M2平滑: {self.kdj_m2}")
        logger.info(f"  超卖阈值: {self.oversold}, 超买阈值: {self.overbought}")
        logger.info(f"  固定止损: {self.stop_loss*100:.1f}%, 止盈: {self.take_profit*100:.1f}%")
        logger.info(f"  移动止损: {self.trailing_stop*100:.1f}%, 触发: {self.trailing_trigger*100:.1f}%")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成KDJ交易信号
        
        策略逻辑:
        - K值 < oversold: 超卖，买入信号 (1)
        - K值 > overbought: 超买，卖出信号 (-1)
        - 结合D值交叉确认信号
        - 应用止损止盈风控
        
        Args:
            data: pd.DataFrame, 股票OHLCV数据
            
        Returns:
            pd.DataFrame: 添加了信号和KDJ指标的数据
        """
        logger.info("开始生成KDJ交易信号...")
        
        self._validate_data(data)
        
        if len(data) < self.kdj_n + max(self.kdj_m1, self.kdj_m2):
            logger.warning(f"数据量不足")
            return pd.DataFrame()
        
        df = data.copy()
        
        # 计算KDJ指标
        df = self._calculate_kdj(df)
        
        # 初始化信号和状态
        df['signal'] = 0
        
        # 使用状态机生成信号
        position = 0  # 0=空仓, 1=持仓
        entry_price = 0  # 买入价格
        highest_price = 0  # 持仓期间最高价
        
        for i in range(len(df)):
            current_price = df.iloc[i]['Close']
            k_value = df.iloc[i]['K']
            d_value = df.iloc[i]['D']
            
            if position == 0:  # 空仓状态
                # 超卖区域 + K上穿D => 买入
                if k_value < self.oversold and k_value > d_value:
                    df.iloc[i, df.columns.get_loc('signal')] = 1
                    position = 1
                    entry_price = current_price
                    highest_price = current_price
                    
            else:  # 持仓状态
                # 更新最高价
                if current_price > highest_price:
                    highest_price = current_price
                
                # 计算盈亏
                profit_rate = (current_price - entry_price) / entry_price
                drawdown = (current_price - highest_price) / highest_price
                
                # 卖出条件判断
                should_sell = False
                sell_reason = ""
                
                # 1. 固定止损
                if profit_rate <= -self.stop_loss:
                    should_sell = True
                    sell_reason = "固定止损"
                
                # 2. 固定止盈
                elif profit_rate >= self.take_profit:
                    should_sell = True
                    sell_reason = "固定止盈"
                
                # 3. 移动止损（盈利达到触发阈值后启动）
                elif profit_rate >= self.trailing_trigger and drawdown <= -self.trailing_stop:
                    should_sell = True
                    sell_reason = "移动止损"
                
                # 4. KDJ信号：超买区域 + K下穿D
                elif k_value > self.overbought and k_value < d_value:
                    should_sell = True
                    sell_reason = "KDJ超买"
                
                if should_sell:
                    df.iloc[i, df.columns.get_loc('signal')] = -1
                    position = 0
                    logger.debug(f"卖出 [{sell_reason}]: 价格={current_price:.2f}, 收益率={profit_rate*100:.2f}%")
        
        df = df.dropna()
        
        # 统计信号
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        logger.info("KDJ信号生成完成")
        logger.info(f"  买入信号数: {buy_signals}")
        logger.info(f"  卖出信号数: {sell_signals}")
        logger.info(f"  有效数据: {len(df)} 条")
        
        return df
    
    def _calculate_kdj(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算KDJ指标
        
        KDJ计算公式:
        1. RSV = (Close - Lowest_Low) / (Highest_High - Lowest_Low) * 100
        2. K = MA(RSV, M1)
        3. D = MA(K, M2)
        4. J = 3*K - 2*D
        
        Args:
            data: pd.DataFrame
            
        Returns:
            pd.DataFrame: 添加了K, D, J列的数据
        """
        df = data.copy()
        
        # 计算N日最高价和最低价
        df['Lowest_Low'] = df['Low'].rolling(window=self.kdj_n, min_periods=self.kdj_n).min()
        df['Highest_High'] = df['High'].rolling(window=self.kdj_n, min_periods=self.kdj_n).max()
        
        # 计算RSV (Raw Stochastic Value)
        denominator = df['Highest_High'] - df['Lowest_Low']
        denominator = denominator.replace(0, np.nan)  # 防止除零
        df['RSV'] = (df['Close'] - df['Lowest_Low']) / denominator * 100
        df['RSV'] = df['RSV'].fillna(50)  # 处理特殊情况
        
        # 计算K值（RSV的M1日移动平均）
        df['K'] = df['RSV'].ewm(span=self.kdj_m1, adjust=False).mean()
        
        # 计算D值（K的M2日移动平均）
        df['D'] = df['K'].ewm(span=self.kdj_m2, adjust=False).mean()
        
        # 计算J值
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        # 清理临时列
        df = df.drop(['Lowest_Low', 'Highest_High', 'RSV'], axis=1)
        
        return df
