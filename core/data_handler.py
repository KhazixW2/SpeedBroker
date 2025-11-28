"""
数据层 (Data Layer)
职责: 唯一的数据来源，负责获取、清洗、存储和提供数据
对上层模块屏蔽数据源的差异
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle


class DataHandler:
    """数据处理器 - 负责所有数据相关的操作"""
    
    def __init__(self, config):
        """
        初始化数据处理器
        
        Args:
            config: 数据配置字典 (DATA_CONFIG)
        """
        self.config = config
        self.data_source = config['data_source']
        self.use_cache = config['use_cache']
        self.cache_dir = config['cache_dir']
        
        # 确保缓存目录存在
        if self.use_cache:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_data(self, tickers):
        """
        获取股票数据的核心方法
        
        Args:
            tickers: 股票代码列表
            
        Returns:
            pd.DataFrame: 清洗后的股票数据
        """
        print(f"[数据层] 开始获取数据: {tickers}")
        
        # 检查缓存
        if self.use_cache:
            cached_data = self._load_from_cache(tickers)
            if cached_data is not None:
                print(f"[数据层] 从缓存加载数据成功")
                return cached_data
        
        # 从数据源下载
        print(f"[数据层] 从 {self.data_source} 下载数据...")
        data = self._fetch_from_source(tickers)
        
        # 数据清洗
        data = self._clean_data(data)
        
        # 保存到缓存
        if self.use_cache:
            self._save_to_cache(tickers, data)
        
        print(f"[数据层] 数据获取完成，共 {len(data)} 条记录")
        return data
    
    def _fetch_from_source(self, tickers):
        """从指定数据源获取数据"""
        if self.data_source == 'akshare':
            return self._fetch_from_akshare(tickers)
        elif self.data_source == 'yfinance':
            return self._fetch_from_yfinance(tickers)
        elif self.data_source == 'tushare':
            return self._fetch_from_tushare(tickers)
        elif self.data_source == 'futu':
            return self._fetch_from_futu(tickers)
        else:
            raise ValueError(f"不支持的数据源: {self.data_source}")
    
    def _fetch_from_akshare(self, tickers):
        """从 AkShare 获取数据"""
        try:
            import akshare as ak
        except ImportError:
            raise ImportError("请先安装 akshare: pip install akshare")
        
        all_data = []
        
        for ticker in tickers:
            print(f"  正在获取 {ticker} 的数据...")
            
            # 清理股票代码：移除可能的股票名称（如 "600941.SH - 中国移动" -> "600941.SH"）
            ticker_clean = ticker.split(' - ')[0].split('(')[0].strip()
            
            # AkShare 股票代码格式: sz000001 或 sh600000
            symbol = ticker_clean.replace('.SZ', '').replace('.SH', '')
            if ticker_clean.endswith('.SZ'):
                symbol = 'sz' + symbol
            elif ticker_clean.endswith('.SH'):
                symbol = 'sh' + symbol
            
            try:
                # 获取历史行情数据
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=self.config['start_date'].replace('-', ''),
                    end_date=self.config['end_date'].replace('-', ''),
                    adjust="qfq"  # 前复权
                )
                
                # 检查数据是否为空
                if df is None or df.empty:
                    print(f"  警告: {ticker_clean} 返回空数据")
                    continue
                
                # 打印列名以便调试
                print(f"  获取到的列: {df.columns.tolist()}")
                
                # 重命名列以统一格式（处理可能的不同列名）
                column_mapping = {
                    '日期': 'Date',
                    '开盘': 'Open',
                    '收盘': 'Close',
                    '最高': 'High',
                    '最低': 'Low',
                    '成交量': 'Volume',
                    '成交额': 'Amount',
                    '振幅': 'Amplitude',
                    '涨跌幅': 'Change',
                    '涨跌额': 'ChangeAmount',
                    '换手率': 'Turnover'
                }
                
                # 只重命名存在的列
                rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
                df = df.rename(columns=rename_dict)
                
                # 确保Date列存在
                if 'Date' not in df.columns:
                    print(f"  警告: 无法找到日期列，可用列: {df.columns.tolist()}")
                    continue
                
                # 使用清理后的代码作为Ticker
                df['Ticker'] = ticker_clean
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
                
                # 确保必需的列存在
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    print(f"  警告: 缺少必需列: {missing_cols}")
                    continue
                
                # 选择需要的列
                df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]
                
                all_data.append(df)
                print(f"  成功获取 {len(df)} 条记录")
                
            except Exception as e:
                print(f"  警告: 获取 {ticker_clean} 数据失败: {str(e)}")
                continue
        
        if not all_data:
            raise ValueError("没有成功获取任何股票数据")
        
        # 合并所有股票数据
        result = pd.concat(all_data, axis=0)
        return result
    
    def _fetch_from_yfinance(self, tickers):
        """从 yfinance 获取数据"""
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("请先安装 yfinance: pip install yfinance")
        
        all_data = []
        
        for ticker in tickers:
            print(f"  正在获取 {ticker} 的数据...")
            
            # 清理股票代码：移除可能的股票名称（如 "600941.SH - 中国移动" -> "600941.SH"）
            ticker_clean = ticker.split(' - ')[0].split('(')[0].strip()
            
            try:
                # 使用 Ticker 对象获取数据
                stock = yf.Ticker(ticker_clean)
                df = stock.history(
                    start=self.config['start_date'],
                    end=self.config['end_date']
                )
                
                if df.empty:
                    print(f"  警告: {ticker_clean} 返回空数据")
                    continue
                
                # yfinance 返回的列名
                # ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
                print(f"  获取到 {len(df)} 条记录")
                
                # 添加股票代码列（使用清理后的代码）
                df['Ticker'] = ticker_clean
                
                # 确保索引是日期类型
                df.index.name = 'Date'
                
                # 选择需要的列
                df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]
                
                all_data.append(df)
                
            except Exception as e:
                print(f"  警告: 获取 {ticker_clean} 数据失败: {str(e)}")
                continue
        
        if not all_data:
            raise ValueError("没有成功获取任何股票数据")
        
        # 合并所有股票数据
        result = pd.concat(all_data, axis=0)
        return result
    
    def _clean_data(self, data):
        """清洗数据"""
        print(f"[数据层] 开始清洗数据...")
        
        # 删除缺失值
        original_len = len(data)
        data = data.dropna()
        removed = original_len - len(data)
        if removed > 0:
            print(f"  删除了 {removed} 条含缺失值的记录")
        
        # 删除重复行
        data = data[~data.index.duplicated(keep='first')]
        
        # 确保数据按日期排序
        data = data.sort_index()
        
        # 数据类型转换
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # 删除异常值 (价格为0或负数)
        if 'Close' in data.columns:
            data = data[data['Close'] > 0]
        
        print(f"[数据层] 数据清洗完成")
        return data
    
    def _get_cache_path(self, tickers):
        """生成缓存文件路径"""
        ticker_str = '_'.join(sorted(tickers))
        start = self.config['start_date'].replace('-', '')
        end = self.config['end_date'].replace('-', '')
        filename = f"{ticker_str}_{start}_{end}_{self.data_source}.pkl"
        return os.path.join(self.cache_dir, filename)
    
    def _load_from_cache(self, tickers):
        """从缓存加载数据"""
        cache_path = self._get_cache_path(tickers)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                return data
            except Exception as e:
                print(f"  警告: 加载缓存失败: {str(e)}")
                return None
        
        return None
    
    def _save_to_cache(self, tickers, data):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(tickers)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"[数据层] 数据已缓存到: {cache_path}")
        except Exception as e:
            print(f"  警告: 保存缓存失败: {str(e)}")
    
    def _fetch_from_tushare(self, tickers):
        """从 Tushare Pro 获取数据"""
        try:
            import tushare as ts
        except ImportError:
            raise ImportError("请先安装 tushare: pip install tushare")
        
        # 检查是否配置了token
        token = self.config.get('tushare_token', '')
        if not token:
            raise ValueError("使用Tushare需要配置token，请在config.py中设置 'tushare_token'")
        
        # 设置token
        ts.set_token(token)
        pro = ts.pro_api()
        
        all_data = []
        
        for ticker in tickers:
            print(f"  正在获取 {ticker} 的数据...")
            
            # 清理股票代码
            ticker_clean = ticker.split(' - ')[0].split('(')[0].strip()
            
            # Tushare使用标准格式：000001.SZ 或 600000.SH
            try:
                # 获取日线行情
                df = pro.daily(
                    ts_code=ticker_clean,
                    start_date=self.config['start_date'].replace('-', ''),
                    end_date=self.config['end_date'].replace('-', ''),
                    fields='ts_code,trade_date,open,high,low,close,vol'
                )
                
                if df is None or df.empty:
                    print(f"  警告: {ticker_clean} 返回空数据")
                    continue
                
                # 重命名列以统一格式
                df = df.rename(columns={
                    'ts_code': 'Ticker',
                    'trade_date': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'vol': 'Volume'
                })
                
                # 转换日期格式
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
                
                # 确保必需的列存在
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if all(col in df.columns for col in required_cols):
                    # Tushare的成交量单位是手，需要转换为股（1手=100股）
                    df['Volume'] = df['Volume'] * 100
                    
                    # 选择需要的列
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]
                    
                    all_data.append(df)
                    print(f"  成功获取 {len(df)} 条记录")
                else:
                    print(f"  警告: 缺少必需列")
                    continue
                
            except Exception as e:
                print(f"  警告: 获取 {ticker_clean} 数据失败: {str(e)}")
                continue
        
        if not all_data:
            raise ValueError("没有成功获取任何股票数据")
        
        # 合并所有股票数据
        result = pd.concat(all_data, axis=0)
        return result
    
    def _fetch_from_futu(self, tickers):
        """从 Futu OpenAPI 获取数据"""
        try:
            from futu import OpenQuoteContext, KLType, AuType, RET_OK
        except ImportError:
            raise ImportError("请先安装 futu-api: pip install futu-api")
        
        # 获取Futu配置
        host = self.config.get('futu_host', '127.0.0.1')
        port = self.config.get('futu_port', 11111)
        
        all_data = []
        
        # 创建行情上下文
        try:
            quote_ctx = OpenQuoteContext(host=host, port=port)
            print(f"  已连接到Futu OpenD: {host}:{port}")
        except Exception as e:
            raise ConnectionError(f"无法连接到Futu OpenD ({host}:{port})，请确保OpenD已启动。错误: {str(e)}")
        
        try:
            for ticker in tickers:
                print(f"  正在获取 {ticker} 的数据...")
                
                # 清理股票代码
                ticker_clean = ticker.split(' - ')[0].split('(')[0].strip()
                
                # 转换为Futu格式
                # A股: 000001.SZ -> SZ.000001 或 600000.SH -> SH.600000
                # 港股: HK.00700
                # 美股: US.AAPL
                futu_code = self._convert_to_futu_code(ticker_clean)
                
                try:
                    # 获取历史K线数据
                    ret, data = quote_ctx.get_history_kline(
                        code=futu_code,
                        start=self.config['start_date'],
                        end=self.config['end_date'],
                        ktype=KLType.K_DAY,
                        autype=AuType.QFQ  # 前复权
                    )
                    
                    if ret != RET_OK:
                        print(f"  警告: 获取 {ticker_clean} 数据失败: {data}")
                        continue
                    
                    if data.empty:
                        print(f"  警告: {ticker_clean} 返回空数据")
                        continue
                    
                    # 重命名列以统一格式
                    df = data.rename(columns={
                        'code': 'Ticker',
                        'time_key': 'Date',
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    })
                    
                    # 将Ticker改回标准格式
                    df['Ticker'] = ticker_clean
                    
                    # 转换日期格式
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date')
                    
                    # 选择需要的列
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]
                    
                    all_data.append(df)
                    print(f"  成功获取 {len(df)} 条记录")
                    
                except Exception as e:
                    print(f"  警告: 获取 {ticker_clean} 数据失败: {str(e)}")
                    continue
            
        finally:
            # 关闭连接
            quote_ctx.close()
            print(f"  已断开Futu OpenD连接")
        
        if not all_data:
            raise ValueError("没有成功获取任何股票数据")
        
        # 合并所有股票数据
        result = pd.concat(all_data, axis=0)
        return result
    
    def _convert_to_futu_code(self, ticker):
        """
        转换股票代码为Futu格式
        
        A股格式转换:
        000001.SZ -> SZ.000001
        600000.SH -> SH.600000
        
        港股格式:
        00700 -> HK.00700
        
        美股格式:
        AAPL -> US.AAPL
        """
        ticker = ticker.upper()
        
        # A股
        if ticker.endswith('.SZ'):
            code = ticker.replace('.SZ', '')
            return f'SZ.{code}'
        elif ticker.endswith('.SH'):
            code = ticker.replace('.SH', '')
            return f'SH.{code}'
        # 港股（纯数字或HK.开头）
        elif ticker.isdigit():
            return f'HK.{ticker.zfill(5)}'  # 补齐到5位
        elif ticker.startswith('HK.'):
            return ticker
        # 美股
        elif '.' not in ticker:
            return f'US.{ticker}'
        else:
            # 默认返回原格式
            return ticker
