# WEEX CLI

WEEX合约交易命令行工具，提供完整的交易功能，包括下单、查看余额、查看订单、查看成交、查看仓位和调整杠杆等。

## ✨ 特性

- 🚀 **完整的交易功能**：账户查询、下单、撤单、订单查询、成交查询
- 📊 **仓位管理**：查询单个或全部合约的仓位信息
- ⚙️ **杠杆管理**：查询和设置杠杆倍数
- 🎯 **自动精度调整**：根据交易对要求自动调整价格和数量精度
- 📝 **详细日志**：支持详细模式查看完整的API请求和响应
- 🔒 **安全认证**：使用WEEX官方API签名机制
- 🌐 **代理支持**：支持HTTP/HTTPS代理

## 📦 安装

### 方式一：直接使用（推荐）

```bash
# 克隆仓库
git clone https://github.com/signalalpha/weex-cli.git
cd weex-cli

# 安装依赖
pip install -r requirements.txt

# 设置可执行权限
chmod +x weex_cli.py

# 使用
./weex_cli.py account
# 或
python weex_cli.py account
```

### 方式二：安装为系统命令（使用 setup.py）

```bash
# 安装
pip install -e .

# 使用（全局命令）
weex-cli account
```

### 方式三：手动安装为系统命令

```bash
# 安装依赖
pip install -r requirements.txt

# 创建软链接或添加到PATH
sudo ln -s $(pwd)/weex_cli.py /usr/local/bin/weex-cli

# 使用
weex-cli account
```

## 🔧 配置

### 环境变量配置

设置以下必需的环境变量：

```bash
export WEEX_API_KEY="your_api_key"
export WEEX_SECRET_KEY="your_secret_key"
export WEEX_PASSPHRASE="your_passphrase"
```

可选环境变量：

```bash
# 代理设置（可选）
export WEEX_PROXY="http://user:pass@host:port"

# API 基础URL（可选，默认: https://api-contract.weex.com）
export WEEX_API_BASE_URL="https://api-contract.weex.com"
```

### 使用 .env 文件（推荐）

创建 `.env` 文件：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```env
WEEX_API_KEY=your_api_key
WEEX_SECRET_KEY=your_secret_key
WEEX_PASSPHRASE=your_passphrase
WEEX_PROXY=http://user:pass@host:port  # 可选
```

## 📖 使用指南

### 查询账户余额

```bash
weex-cli account
```

### 查询价格

```bash
weex-cli price -s cmt_btcusdt
```

### 下单

**限价单：**

```bash
weex-cli order -s cmt_btcusdt -d buy -t limit -z 10 --price 80000
```

**市价单：**

```bash
weex-cli order -s cmt_btcusdt -d buy -t market -z 10
```

参数说明：
- `-s, --symbol`: 交易对符号（必需）
- `-d, --side`: 方向，`buy` 或 `sell`（必需）
- `-t, --type`: 订单类型，`market` 或 `limit`（必需）
- `-z, --size`: 订单数量（必需）
- `--price`: 价格（限价单必需）

### 查询当前活跃订单

```bash
weex-cli orders -s cmt_btcusdt
```

### 查询历史订单

```bash
weex-cli history -s cmt_btcusdt
weex-cli history -s cmt_btcusdt --size 20  # 返回20条
```

### 查询成交记录

```bash
weex-cli fills -s cmt_btcusdt
weex-cli fills -s cmt_btcusdt --size 20  # 返回20条
```

### 查询仓位信息

**查询单个合约仓位：**

```bash
weex-cli positions -s cmt_btcusdt
```

**查询全部合约仓位：**

```bash
weex-cli positions
```

### 查询杠杆信息

```bash
weex-cli leverage get -s cmt_btcusdt
```

### 设置杠杆

```bash
weex-cli leverage set -s cmt_btcusdt --long 20 --short 20 --mode 1
```

参数说明：
- `-s, --symbol`: 交易对符号（必需）
- `--long`: 做多杠杆倍数（必需）
- `--short`: 做空杠杆倍数（必需）
- `--mode`: 保证金模式，`1`=全仓，`2`=逐仓（必需）

### 取消订单

```bash
weex-cli cancel <order_id>
```

### 详细模式

所有命令都支持 `-v` 或 `--verbose` 参数，显示详细的请求和响应信息：

```bash
weex-cli order -s cmt_btcusdt -d buy -t limit -z 10 --price 80000 -v
```

## 🎯 支持的交易对

工具内置了以下8个官方比赛交易对的精度配置：

- `cmt_btcusdt` - BTC/USDT
- `cmt_ethusdt` - ETH/USDT
- `cmt_solusdt` - SOL/USDT
- `cmt_dogeusdt` - DOGE/USDT
- `cmt_xrpusdt` - XRP/USDT
- `cmt_adausdt` - ADA/USDT
- `cmt_bnbusdt` - BNB/USDT
- `cmt_ltcusdt` - LTC/USDT

## 📋 完整示例

```bash
# 1. 查询账户余额
weex-cli account

# 2. 查询当前价格
weex-cli price -s cmt_btcusdt

# 3. 设置杠杆为20倍（全仓模式）
weex-cli leverage set -s cmt_btcusdt --long 20 --short 20 --mode 1

# 4. 下限价买单
weex-cli order -s cmt_btcusdt -d buy -t limit -z 0.001 --price 80000

# 5. 查询当前订单
weex-cli orders -s cmt_btcusdt

# 6. 查询全部合约仓位
weex-cli positions

# 7. 查询成交记录
weex-cli fills -s cmt_btcusdt

# 8. 取消订单
weex-cli cancel <order_id>
```

## 🛠️ 帮助信息

查看所有可用命令：

```bash
weex-cli --help
```

查看特定命令的帮助：

```bash
weex-cli order --help
weex-cli leverage --help
```

## 🔍 功能特性详解

### 自动精度调整

工具会根据交易对的精度要求自动调整价格和数量：

- **价格精度**：根据 `price_step` 自动调整
- **数量精度**：根据 `size_step` 自动调整
- **最小数量**：确保订单数量不小于 `min_size`

### 详细日志模式

使用 `-v` 参数可以查看：
- 完整的API请求URL
- 请求头和请求体（敏感信息已脱敏）
- HTTP响应状态码
- 完整的响应体

### 仓位查询

查询全部合约仓位时会显示：
- 每个有持仓的合约的详细信息
- 持仓方向、数量、杠杆
- 开仓价、标记价
- 未实现盈亏
- 持仓价值统计

## 📝 依赖

- Python 3.6+
- requests
- python-dotenv (可选，用于支持 .env 文件)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

本工具仅供学习和研究使用。使用本工具进行交易产生的任何损失，开发者不承担任何责任。请谨慎使用，理性交易。
