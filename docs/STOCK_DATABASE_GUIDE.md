# 📚 股票数据库使用指南

## 概述

本项目提供了灵活的股票代码管理系统，支持静态列表和动态获取两种模式。

---

## 🔍 重要概念区分

### 1. 数据源（Data Source）≠ 股票列表

**数据源**：用于获取股票**历史价格数据**的API
- `yfinance` - Yahoo Finance
- `akshare` - AkShare

**股票列表**：用于**自动补全**的股票代码库
- 静态列表：200+只预设股票
- 动态列表：5000+只全部A股

---

## 📊 股票列表方案

### 方案一：静态列表（200+只）

**文件**：`stock_list.py` → `StockDatabase.get_all_stocks()`

**优点**：
- ✅ 启动速度极快（毫秒级）
- ✅ 无需网络连接
- ✅ 稳定可靠
- ✅ 覆盖主流蓝筹股

**缺点**：
- ⚠️ 不包含全部股票
- ⚠️ 需要手动维护

**包含股票**：
- 银行股：20+只（工商、建设、招商等）
- 白酒股：10+只（茅台、五粮液、汾酒等）
- 科技股：30+只（海康、中兴、立讯等）
- 新能源：20+只（宁德时代、比亚迪等）
- 医药股：15+只（恒瑞、迈瑞、爱尔等）
- 其他：100+只

**使用方式**：
```python
# 在 gui_main.py 中
def get_popular_stocks(self):
    return StockDatabase.get_all_stocks()
```

---

### 方案二：动态获取（5000+只）⭐ 当前默认

**文件**：`stock_list.py` → `StockDatabase.get_dynamic_stocks_akshare()`

**优点**：
- ✅ **包含所有A股**（约5000只）
- ✅ 自动更新，包含新上市股票
- ✅ 无需手动维护
- ✅ 数据最全面

**缺点**：
- ⚠️ 首次启动需要10-30秒（下载列表）
- ⚠️ 需要网络连接
- ⚠️ 依赖akshare API稳定性

**工作原理**：
```python
1. 调用 akshare.stock_zh_a_spot_em()
2. 获取实时股票列表
3. 自动判断市场并添加后缀：
   - 深圳主板/中小板/创业板 → .SZ
   - 上海主板/科创板 → .SH
   - 北交所 → .BJ
4. 组合成 "代码 - 名称" 格式
5. 失败时自动降级到静态列表
```

**使用方式**：
```python
# 在 gui_main.py 中（当前默认）
def get_popular_stocks(self):
    return StockDatabase.get_dynamic_stocks_akshare()
```

---

## 🔧 切换方案

### 切换到静态列表

编辑 `gui_main.py` 第120-125行左右：

```python
def get_popular_stocks(self):
    # 注释掉动态获取
    # stocks = StockDatabase.get_dynamic_stocks_akshare()
    
    # 使用静态列表
    return StockDatabase.get_all_stocks()
```

### 切换到动态列表（当前默认）

```python
def get_popular_stocks(self):
    # 使用动态获取
    stocks = StockDatabase.get_dynamic_stocks_akshare()
    return stocks
```

---

## 🎯 使用建议

### 推荐配置

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 日常使用 | 动态获取 | 最全面，任何股票都能找到 |
| 无网络环境 | 静态列表 | 可离线使用 |
| 快速测试 | 静态列表 | 启动更快 |
| 新股研究 | 动态获取 | 包含最新上市股票 |

### 性能对比

| 指标 | 静态列表 | 动态获取 |
|------|----------|----------|
| 首次启动 | 0.1秒 | 10-30秒 |
| 后续启动 | 0.1秒 | 0.1秒（缓存） |
| 股票数量 | 200+ | 5000+ |
| 网络需求 | ❌ | ✅ |
| 覆盖率 | 主流股 | 全部A股 |

---

## 🛠️ 自定义扩展

### 添加自己的股票

编辑 `stock_list.py`，在 `get_all_stocks()` 中添加：

```python
@staticmethod
def get_all_stocks():
    return [
        # 添加你的股票
        "your_code.SZ - 你的股票名称",
        
        # 现有股票...
        "000001.SZ - 平安银行",
        # ...
    ]
```

### 从CSV文件加载

```python
@staticmethod
def get_stocks_from_csv(filename):
    """从CSV文件加载股票列表"""
    import pandas as pd
    df = pd.read_csv(filename)
    return [f"{row['code']} - {row['name']}" for _, row in df.iterrows()]
```

### 从数据库加载

```python
@staticmethod
def get_stocks_from_database():
    """从数据库加载股票列表"""
    import sqlite3
    conn = sqlite3.connect('stocks.db')
    cursor = conn.execute("SELECT code, name FROM stocks")
    return [f"{code} - {name}" for code, name in cursor]
```

---

## 📝 注意事项

### 动态获取的注意事项

1. **首次启动较慢**
   - 第一次需要下载5000+股票列表
   - 耐心等待10-30秒
   - 后续启动会快很多

2. **网络依赖**
   - 需要能访问akshare API
   - 失败时自动降级到静态列表

3. **数据更新**
   - 每次启动都会获取最新列表
   - 包含当天新上市的股票

### 静态列表的优势

1. **快速启动** - 无需等待
2. **离线可用** - 不需要网络
3. **稳定性高** - 不依赖外部API

---

## 🎯 当前配置

**GUI默认设置**：动态获取（5000+只股票）

**特点**：
- ✅ 包含所有A股
- ✅ 自动更新
- ✅ 支持任何股票搜索
- ✅ 失败时自动降级

**启动GUI后**：
- 控制台会显示"正在获取股票列表..."
- 显示"已加载 XXXX 只股票"
- 然后可以搜索任何A股

---

## 💡 最佳实践

### 推荐流程

1. **首次使用**：
   - 使用动态获取（当前默认）
   - 耐心等待列表加载
   - 体验完整功能

2. **日常使用**：
   - 如果网络良好，保持动态获取
   - 如果启动慢，切换到静态列表

3. **特殊需求**：
   - 自定义CSV/数据库
   - 扩展 `stock_list.py`

---

**现在系统默认使用动态获取，包含所有A股！** 🎉
