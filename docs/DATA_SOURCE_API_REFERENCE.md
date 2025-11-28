# 数据源 API 参考文档

> SpeedBroker 量化交易系统支持的三大数据源详细说明

## 📋 目录

- [数据源对比](#数据源对比)
- [AkShare API](#akshare-api)
- [Tushare Pro API](#tushare-pro-api)
- [Futu OpenAPI](#futu-openapi)
- [使用建议](#使用建议)
- [切换数据源](#切换数据源)

---

## 数据源对比

| 特性 | AkShare | Tushare Pro | Futu OpenAPI |
|------|---------|-------------|--------------|
| **费用** | 完全免费 | 积分制（部分免费） | 需开户（行情免费） |
| **注册要求** | 无需注册 | 需要注册获取token | 需要富途账号 |
| **数据覆盖** | 全面（A股/港股/美股） | 专业全面（以A股为主） | 港股/美股/A股通 |
| **数据质量** | 良好 | 非常好 | 实时专业级 |
| **实时性** | 日线级别 | 日线/分钟/Tick | 实时推送 |
| **API限制** | 无明确限制 | 积分消耗 | 订阅数量限制 |
| **适用场景** | 回测、研究 | 专业回测 | 实时交易+回测 |
| **Python库** | `akshare` | `tushare` | `futu-api` |

---

## AkShare API

### 🌟 特点

- **完全免费**：无需注册和token
- **数据丰富**：涵盖股票、期货、债券、基金、指数、宏观等
- **更新及时**：经常更新API接口
- **易于使用**：API设计简洁

### 📦 安装

```bash
pip install akshare --upgrade
```

### 🔧 核心API接口

#### 1. 股票数据

##### A股日线行情
```python
import akshare as ak

# 获取A股日线历史数据
df = ak.stock_zh_a_hist(
    symbol="sz000001",        # 股票代码（sz开头：深圳，sh开头：上海）
    period="daily",           # 周期：daily/weekly/monthly
    start_date="20230101",    # 开始日期（YYYYMMDD格式）
    end_date="20241001",      # 结束日期
    adjust="qfq"              # 复权类型：qfq(前复权)/hfq(后复权)/空(不复权)
)

# 返回字段
# 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率
```

##### 股票列表
```python
# 获取A股股票列表
stock_list = ak.stock_zh_a_spot()  # 实时行情
# 返回：代码, 名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额等
```

##### 实时行情
```python
# 获取个股实时行情
df = ak.stock_zh_a_spot_em()
# 包含所有A股的实时数据
```

#### 2. 指数数据

```python
# 获取指数历史数据
df = ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数
df = ak.stock_zh_index_daily(symbol="sz399001")  # 深证成指
df = ak.stock_zh_index_daily(symbol="sz399006")  # 创业板指
```

#### 3. 港股数据

```python
# 获取港股实时行情
df = ak.stock_hk_spot_em()

# 获取港股历史行情
df = ak.stock_hk_hist(
    symbol="00700",           # 腾讯控股
    period="daily",
    start_date="20230101",
    end_date="20241001",
    adjust="qfq"
)
```

#### 4. 美股数据

```python
# 获取美股实时行情
df = ak.stock_us_spot_em()

# 获取美股历史行情（需要通过yfinance）
```

#### 5. 基金数据

```python
# 公募基金净值
df = ak.fund_open_fund_info_em(
    fund="000001",            # 基金代码
    indicator="单位净值走势"
)

# ETF实时行情
df = ak.fund_etf_spot_em()
```

#### 6. 财务数据

```python
# 财务报表
df = ak.stock_financial_report_sina(
    stock="000001",
    symbol="利润表"           # 利润表/资产负债表/现金流量表
)

# 业绩预告
df = ak.stock_yjyg_em(date="20241231")
```

#### 7. 宏观数据

```python
# GDP数据
df = ak.macro_china_gdp()

# CPI数据
df = ak.macro_china_cpi()

# PMI数据
df = ak.macro_china_pmi()

# 货币供应量
df = ak.macro_china_money_supply()
```

### 📊 数据字段说明

#### 股票日线数据字段
| 字段名 | 说明 | 类型 |
|--------|------|------|
| 日期 | 交易日期 | str |
| 开盘 | 开盘价 | float |
| 收盘 | 收盘价 | float |
| 最高 | 最高价 | float |
| 最低 | 最低价 | float |
| 成交量 | 成交量（手） | int |
| 成交额 | 成交额（元） | float |
| 振幅 | 振幅（%） | float |
| 涨跌幅 | 涨跌幅（%） | float |
| 涨跌额 | 涨跌额（元） | float |
| 换手率 | 换手率（%） | float |

### ⚠️ 注意事项

1. **股票代码格式**：
   - 深圳股票：`sz + 6位代码`（如 sz000001）
   - 上海股票：`sh + 6位代码`（如 sh600000）

2. **日期格式**：YYYYMMDD（如 20240101）

3. **更新频率**：数据一般在当日收盘后更新

4. **API稳定性**：AkShare经常更新，建议定期升级

---

## Tushare Pro API

### 🌟 特点

- **数据专业**：金融数据质量高
- **接口规范**：统一的API设计
- **权限管理**：基于积分的权限系统
- **数据全面**：包含基本面、财务、行情等全方位数据

### 📦 安装与配置

```bash
pip install tushare
```

### 🔑 获取Token

1. 访问 [https://tushare.pro](https://tushare.pro)
2. 注册账号
3. 获取API Token
4. 配置Token

```python
import tushare as ts

# 设置token
ts.set_token('your_token_here')
pro = ts.pro_api()
```

### 🔧 核心API接口

#### 1. 股票数据

##### 股票列表
```python
# 获取所有股票列表
df = pro.stock_basic(
    exchange='',              # 交易所：SSE上交所/SZSE深交所/BSE北交所
    list_status='L',          # 上市状态：L上市/D退市/P暂停上市
    fields='ts_code,symbol,name,area,industry,list_date'
)

# 返回字段
# ts_code(股票代码), symbol(股票代码), name(股票名称), 
# area(地区), industry(行业), list_date(上市日期)
```

##### 日线行情
```python
# 获取日线行情（通用接口）
df = pro.daily(
    ts_code='000001.SZ',      # 股票代码（000001.SZ格式）
    start_date='20230101',    # 开始日期
    end_date='20241001',      # 结束日期
    fields='ts_code,trade_date,open,high,low,close,vol,amount'
)

# 返回字段
# ts_code, trade_date(交易日期), open(开盘价), high(最高价), 
# low(最低价), close(收盘价), vol(成交量-手), amount(成交额-千元)
```

##### 周/月线行情
```python
# 周线行情
df = pro.weekly(ts_code='000001.SZ', start_date='20230101', end_date='20241001')

# 月线行情
df = pro.monthly(ts_code='000001.SZ', start_date='20230101', end_date='20241001')
```

##### 复权因子
```python
# 获取复权因子
df = pro.adj_factor(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20241001'
)

# 手动计算前复权价格
# 前复权价 = 收盘价 * 复权因子 / 最新复权因子
```

##### 分钟行情（需要5000积分以上）
```python
# 获取1分钟K线
df = pro.stk_mins(
    ts_code='000001.SZ',
    start_date='20241001 09:30:00',
    end_date='20241001 15:00:00',
    freq='1min'               # 频率：1min/5min/15min/30min/60min
)
```

#### 2. 指数数据

```python
# 获取指数日线行情
df = pro.index_daily(
    ts_code='000001.SH',      # 上证指数
    start_date='20230101',
    end_date='20241001'
)

# 获取指数成分和权重
df = pro.index_weight(
    index_code='399300.SZ',   # 沪深300
    start_date='20240101',
    end_date='20241001'
)
```

#### 3. 财务数据

##### 利润表
```python
df = pro.income(
    ts_code='000001.SZ',
    period='20231231',        # 报告期
    fields='ts_code,end_date,total_revenue,total_cogs,operate_profit,net_profit'
)
```

##### 资产负债表
```python
df = pro.balancesheet(
    ts_code='000001.SZ',
    period='20231231'
)
```

##### 现金流量表
```python
df = pro.cashflow(
    ts_code='000001.SZ',
    period='20231231'
)
```

##### 财务指标
```python
df = pro.fina_indicator(
    ts_code='000001.SZ',
    period='20231231',
    fields='ts_code,end_date,eps,roe,roa,debt_to_assets,current_ratio'
)
```

#### 4. 市场数据

```python
# 每日涨跌停统计
df = pro.limit_list(trade_date='20241001')

# 龙虎榜数据
df = pro.top_list(trade_date='20241001')

# 大单成交
df = pro.block_trade(trade_date='20241001')
```

#### 5. 基础数据

```python
# 交易日历
df = pro.trade_cal(
    exchange='SSE',
    start_date='20230101',
    end_date='20241231'
)

# 股票曾用名
df = pro.namechange(ts_code='000001.SZ')

# 停复牌信息
df = pro.suspend_d(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20241001'
)
```

### 💎 积分权限说明

| 接口类型 | 所需积分 | 说明 |
|----------|----------|------|
| 基础行情 | 120+ | 日线行情、基础数据 |
| 财务数据 | 2000+ | 三大报表、财务指标 |
| 分钟行情 | 5000+ | 1/5/15/30/60分钟K线 |
| Tick数据 | 10000+ | 逐笔成交数据 |

**获取积分方式**：
- 注册：120积分
- 每日签到：1积分
- 邀请用户：200积分/人
- 贡献代码：500-5000积分
- 捐赠：2000积分起

### 📊 数据字段说明

#### 日线行情字段
| 字段名 | 说明 | 类型 |
|--------|------|------|
| ts_code | 股票代码 | str |
| trade_date | 交易日期 | str |
| open | 开盘价 | float |
| high | 最高价 | float |
| low | 最低价 | float |
| close | 收盘价 | float |
| pre_close | 昨收价 | float |
| change | 涨跌额 | float |
| pct_chg | 涨跌幅(%) | float |
| vol | 成交量(手) | float |
| amount | 成交额(千元) | float |

### ⚠️ 注意事项

1. **股票代码格式**：`000001.SZ`（深圳）、`600000.SH`（上海）

2. **日期格式**：YYYYMMDD（如 20240101）

3. **积分消耗**：每次调用会消耗一定积分

4. **请求限制**：
   - 普通用户：200次/分钟
   - VIP用户：500次/分钟

---

## Futu OpenAPI

### 🌟 特点

- **实时行情**：毫秒级推送
- **交易能力**：支持港股、美股、A股通交易
- **专业级**：适合量化交易和程序化交易
- **全市场**：覆盖港股、美股、A股、期货、期权

### 📦 安装与配置

#### 1. 安装OpenD网关

下载地址：[https://www.futunn.com/download/OpenAPI](https://www.futunn.com/download/OpenAPI)

支持平台：
- Windows
- MacOS  
- Linux (CentOS/Ubuntu)

#### 2. 安装Python SDK

```bash
pip install futu-api
```

### 🔑 账号要求

1. 注册富途账号（牛牛号）或 moomoo 账号
2. 下载并安装富途牛牛APP
3. 开通相应市场权限

### 🔧 核心API接口

#### 1. 连接与初始化

```python
from futu import *

# 创建行情上下文
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 创建交易上下文（真实交易）
trade_ctx = OpenSecTradeContext(
    filter_trdmarket=TrdMarket.HK,
    host='127.0.0.1',
    port=11111,
    security_firm=SecurityFirm.FUTUSECURITIES
)

# 关闭连接
quote_ctx.close()
trade_ctx.close()
```

#### 2. 行情接口

##### 订阅实时行情
```python
# 订阅K线
quote_ctx.subscribe(
    code_list=['HK.00700'],   # 腾讯控股
    subtype_list=[SubType.K_DAY],  # K_1M/K_5M/K_15M/K_DAY/K_WEEK
    is_first_push=True
)

# 获取K线数据
ret, data = quote_ctx.get_cur_kline(
    code='HK.00700',
    num=100,                  # 获取数量
    ktype=KLType.K_DAY        # K线类型
)

if ret == RET_OK:
    print(data)
else:
    print('获取失败:', data)
```

##### 获取历史K线
```python
ret, data = quote_ctx.get_history_kline(
    code='HK.00700',
    start='2023-01-01',
    end='2024-10-01',
    ktype=KLType.K_DAY,
    autype=AuType.QFQ         # 前复权
)

# 返回字段
# code, time_key, open, close, high, low, volume, turnover, 
# pe_ratio, turnover_rate, change_rate
```

##### 实时报价
```python
# 获取实时报价
ret, data = quote_ctx.get_market_snapshot(code_list=['HK.00700', 'HK.00388'])

# 返回字段：最新价、买卖盘、成交量、涨跌幅等
```

##### 逐笔成交
```python
# 获取逐笔成交
ret, data = quote_ctx.get_rt_ticker(code='HK.00700', num=100)

# 返回：成交时间、价格、成交量、成交类型
```

##### 买卖盘口
```python
# 获取买卖盘
ret, data = quote_ctx.get_order_book(code='HK.00700')

# 返回：买一到买十、卖一到卖十的价格和数量
```

#### 3. 基础数据

```python
# 获取股票列表
ret, data = quote_ctx.get_stock_basicinfo(
    market=Market.HK,
    stock_type=SecurityType.STOCK
)

# 获取交易日历
ret, data = quote_ctx.get_trading_days(
    market=Market.HK,
    start='2023-01-01',
    end='2024-12-31'
)

# 获取静态信息
ret, data = quote_ctx.get_stock_basicinfo(
    market=Market.HK,
    stock_code='HK.00700'
)
```

#### 4. 交易接口

```python
# 查询账户资产
ret, data = trade_ctx.accinfo_query()

# 查询持仓
ret, data = trade_ctx.position_list_query()

# 下单（买入）
ret, data = trade_ctx.place_order(
    price=400.0,              # 价格
    qty=100,                  # 数量
    code='HK.00700',          # 股票代码
    trd_side=TrdSide.BUY,     # 买入/卖出
    order_type=OrderType.NORMAL,  # 订单类型
    trd_env=TrdEnv.SIMULATE   # SIMULATE模拟/REAL真实
)

# 查询订单
ret, data = trade_ctx.order_list_query()

# 撤单
ret, data = trade_ctx.modify_order(
    modify_order_op=ModifyOrderOp.CANCEL,
    order_id=order_id
)
```

### 📊 支持的市场和品种

#### 行情数据支持

| 市场 | 股票 | ETF | 指数 | 期权 | 期货 |
|------|------|-----|------|------|------|
| 香港 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 美国 | ✓ | ✓ | ✗ | ✓ | ✓ |
| A股 | ✓ | ✓ | ✓ | ✗ | ✗ |
| 新加坡 | ✗ | ✗ | ✗ | ✗ | ✗ |

#### 交易能力支持

| 市场 | 模拟交易 | 真实交易 |
|------|----------|----------|
| 香港股票 | ✓ | ✓ |
| 美国股票 | ✓ | ✓ |
| A股通 | ✓ | ✓ |
| 期权 | ✓ | ✓ |
| 期货 | ✓ | ✓ |

### ⚠️ 限制说明

#### 订阅限制
- 免费用户：最多订阅10只股票
- LV1行情：最多订阅100只股票  
- LV2行情：最多订阅500只股票

#### 请求限制
- 每个接口都有频率限制
- 建议使用订阅推送而非频繁拉取

### 💡 使用建议

1. **实时交易场景**：优先选择Futu
2. **历史回测**：数据量大时使用AkShare或Tushare
3. **混合使用**：
   - 历史数据：AkShare/Tushare
   - 实时行情：Futu
   - 实盘交易：Futu

---

## 使用建议

### 📌 场景选择

| 使用场景 | 推荐数据源 | 理由 |
|----------|------------|------|
| 量化回测（A股） | AkShare / Tushare | 免费/数据全面 |
| 量化回测（港美股） | AkShare / Futu | 覆盖全面 |
| 实时行情监控 | Futu | 实时推送 |
| 程序化交易 | Futu | 交易接口 |
| 基本面研究 | Tushare | 财务数据完整 |
| 学习研究 | AkShare | 完全免费 |

### 🎯 组合策略

#### 策略1：免费回测方案
```
历史数据：AkShare
优点：完全免费，数据覆盖全面
适合：个人投资者、学习研究
```

#### 策略2：专业回测方案  
```
历史数据：Tushare Pro
优点：数据质量高，接口稳定
适合：量化团队、专业投资者
```

#### 策略3：实盘交易方案
```
历史回测：AkShare/Tushare
实时行情：Futu OpenAPI
实盘交易：Futu OpenAPI
优点：回测成本低，实盘专业
适合：程序化交易、量化策略
```

---

## 切换数据源

### 方法1：GUI界面切换

```
1. 启动GUI: python run_gui.py
2. 在"数据配置"区域
3. 将"数据源"改为 akshare/tushare/futu
4. 如选择tushare，需要填写token
5. 如选择futu，需要确保OpenD已启动
```

### 方法2：修改配置文件

编辑 `core/config.py`:

```python
DATA_CONFIG = {
    'tickers': ['000001.SZ'],
    'start_date': '2023-01-01',
    'end_date': '2024-10-01',
    
    # 数据源选择
    'data_source': 'akshare',  # 改为 'tushare' 或 'futu'
    
    # Tushare配置（仅使用tushare时需要）
    'tushare_token': 'your_token_here',
    
    # Futu配置（仅使用futu时需要）
    'futu_host': '127.0.0.1',
    'futu_port': 11111,
}
```

### 方法3：代码中动态切换

```python
from core.data_handler import DataHandler
from core.config import DATA_CONFIG

# 临时修改数据源
DATA_CONFIG['data_source'] = 'tushare'
DATA_CONFIG['tushare_token'] = 'your_token'

# 创建数据处理器
handler = DataHandler(DATA_CONFIG)
data = handler.get_data(['000001.SZ'])
```

---

## 📚 参考资源

### AkShare
- 官方文档：[https://akshare.akfamily.xyz](https://akshare.akfamily.xyz)
- GitHub：[https://github.com/akfamily/akshare](https://github.com/akfamily/akshare)
- 微信公众号：数据科学实战

### Tushare Pro
- 官方文档：[https://tushare.pro/document/2](https://tushare.pro/document/2)
- 注册地址：[https://tushare.pro/register](https://tushare.pro/register)
- 社区论坛：[https://tushare.pro/community](https://tushare.pro/community)

### Futu OpenAPI
- 官方文档：[https://openapi.futunn.com](https://openapi.futunn.com)
- 下载OpenD：[https://www.futunn.com/download/OpenAPI](https://www.futunn.com/download/OpenAPI)
- API SDK：[https://github.com/FutunnOpen/py-futu-api](https://github.com/FutunnOpen/py-futu-api)

---

## 📝 版本更新

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2024-11 | 初始版本，支持三大数据源 |

---

**注意**：本文档基于各数据源当前版本编写，具体API可能会随版本更新而变化，请以官方文档为准。
