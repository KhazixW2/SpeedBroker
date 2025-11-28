# 测试脚本说明

本目录包含 SpeedBroker 项目的各种测试脚本，用于验证数据获取、功能修复和系统诊断。

## 测试脚本列表

### 1. test_akshare.py
**用途**: AkShare数据源基础测试  
**功能**: 快速测试AkShare是否能正常工作  
**运行方式**:
```bash
python tests/test_akshare.py
```

**适用场景**:
- 首次使用前验证AkShare是否安装正确
- 快速检查数据获取功能是否正常

---

### 2. test_akshare_detailed.py
**用途**: AkShare数据源详细诊断  
**功能**: 全面诊断AkShare数据获取问题  
**运行方式**:
```bash
python tests/test_akshare_detailed.py
```

**适用场景**:
- 遇到"没有成功获取任何股票数据"错误时
- 需要详细了解数据获取失败原因
- 验证多个股票代码的数据获取情况

**输出信息**:
- ✓ akshare安装检查
- ✓ 网络连接测试
- ✓ 股票代码格式转换验证
- ✓ 实际数据获取测试
- ✓ 问题诊断和解决方案建议

---

### 3. test_fix.py
**用途**: 数据获取功能修复验证  
**功能**: 验证带名称的股票代码是否能正确处理  
**运行方式**:
```bash
python tests/test_fix.py
```

**适用场景**:
- 修复代码后验证功能是否正常
- 测试GUI下拉列表选择的股票代码（如"000001.SZ - 平安银行"）是否能正常工作

**测试用例**:
1. 纯股票代码: `000001.SZ`
2. 带名称（中划线）: `000001.SZ - 平安银行`
3. 带名称（括号）: `000001.SZ(平安银行)`

---

## 运行测试的最佳实践

### 首次使用时
按以下顺序运行测试：
```bash
# 1. 基础测试
python tests/test_akshare.py

# 2. 如果基础测试失败，运行详细诊断
python tests/test_akshare_detailed.py

# 3. 验证修复功能
python tests/test_fix.py
```

### 遇到问题时
```bash
# 直接运行详细诊断
python tests/test_akshare_detailed.py
```

根据诊断结果参考 `docs/DATA_SOURCE_TROUBLESHOOTING.md` 进行修复。

---

## 常见问题处理

### 问题1: 所有测试都返回空数据
**原因**: AkShare版本过旧或API变化  
**解决方案**:
```bash
pip install akshare --upgrade
```

### 问题2: 测试脚本找不到模块
**原因**: 路径问题  
**解决方案**: 确保在项目根目录运行测试
```bash
# 正确的运行方式（在项目根目录）
cd d:/workspace/SpeedBroker
python tests/test_akshare.py

# 错误的运行方式
cd d:/workspace/SpeedBroker/tests
python test_akshare.py  # ❌ 可能找不到core模块
```

### 问题3: 网络连接失败
**解决方案**: 检查防火墙或设置代理
```python
# 在测试脚本开头添加
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

---

## 测试数据说明

### 推荐的测试股票
- `000001.SZ` - 平安银行（深圳）
- `600000.SH` - 浦发银行（上海）
- `000002.SZ` - 万科A（深圳）
- `600519.SH` - 贵州茅台（上海）

这些股票数据稳定，适合用于测试。

### 日期范围建议
```python
start_date = "2024-01-01"  # 不要太早
end_date = "2024-10-01"    # 不要超过今天
```

---

## 测试结果解读

### 成功的标志
```
✓ akshare 已安装，版本: 1.17.79
✓ 网络连接正常 (状态码: 200)
✓ 股票代码格式转换正确
✓ 成功获取 242 条记录
✓ 测试通过
```

### 失败的标志
```
✗ 返回空数据
✗ 获取失败: HTTPError
✗ 测试失败: ValueError
```

---

## 相关文档

- **数据源问题排查**: `docs/DATA_SOURCE_TROUBLESHOOTING.md`
- **配置指南**: `docs/CONFIG_GUIDE.md`
- **用户指南**: `docs/USER_GUIDE.md`

---

## 添加新测试

如需添加新的测试脚本：

1. 在 `tests/` 目录下创建新的测试文件
2. 使用清晰的命名：`test_<功能名称>.py`
3. 在文件开头添加文档字符串说明用途
4. 更新本README文件

示例：
```python
"""
测试功能：XXX
用途：验证XXX是否正常工作
"""

# 测试代码...
