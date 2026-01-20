#!/usr/bin/env python3
"""
WEEX Trading CLI Tool
提供完整的WEEX合约交易命令行工具，包括下单、查看余额、查看订单、查看成交、查看仓位和调整杠杆等功能
"""

import time
import hmac
import hashlib
import base64
import requests
import json
import os
import sys
import argparse
from typing import Optional, Dict, Any, List

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Read API credentials from environment variables
api_key = os.environ.get("WEEX_API_KEY")
secret_key = os.environ.get("WEEX_SECRET_KEY")
access_passphrase = os.environ.get("WEEX_PASSPHRASE")

# Read proxy from environment variables
proxy_url = os.environ.get("WEEX_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")

# Validate that all required environment variables are set
if not api_key or not secret_key or not access_passphrase:
    print("❌ 错误: 缺少必需的环境变量")
    print("请设置以下环境变量:")
    print("  - WEEX_API_KEY")
    print("  - WEEX_SECRET_KEY")
    print("  - WEEX_PASSPHRASE")
    print("\n可选代理设置:")
    print("  - WEEX_PROXY (优先) 或 HTTP_PROXY/HTTPS_PROXY")
    print("\n或者创建 .env 文件，参考 .env.example")
    sys.exit(1)

BASE_URL = os.environ.get("WEEX_API_BASE_URL", "https://api-contract.weex.com")

# 交易对的精度配置
SYMBOL_PRECISION = {
    "cmt_btcusdt": {"price_step": 0.1, "size_step": 0.001, "min_size": 0.001},
    "cmt_ethusdt": {"price_step": 0.01, "size_step": 0.001, "min_size": 0.001},
    "cmt_solusdt": {"price_step": 0.001, "size_step": 0.1, "min_size": 0.1},
    "cmt_dogeusdt": {"price_step": 0.00001, "size_step": 100, "min_size": 100},
    "cmt_xrpusdt": {"price_step": 0.0001, "size_step": 10, "min_size": 10},
    "cmt_adausdt": {"price_step": 0.0001, "size_step": 10, "min_size": 10},
    "cmt_bnbusdt": {"price_step": 0.01, "size_step": 0.1, "min_size": 0.1},
    "cmt_ltcusdt": {"price_step": 0.01, "size_step": 0.1, "min_size": 0.1},
}


def round_to_step(value: float, step: float) -> float:
    """将数值四舍五入到指定步长"""
    if step <= 0:
        return value
    return round(value / step) * step


def adjust_price_to_precision(price: float, symbol: str) -> float:
    """根据交易对精度调整价格"""
    if symbol not in SYMBOL_PRECISION:
        return price
    precision = SYMBOL_PRECISION[symbol]
    return round_to_step(price, precision["price_step"])


def adjust_size_to_precision(size: float, symbol: str) -> float:
    """根据交易对精度调整数量"""
    if symbol not in SYMBOL_PRECISION:
        return size
    precision = SYMBOL_PRECISION[symbol]
    adjusted = round_to_step(size, precision["size_step"])
    # 确保不小于最小数量
    return max(adjusted, precision["min_size"])


def format_price_string(price: float, symbol: str) -> str:
    """格式化价格字符串"""
    if symbol not in SYMBOL_PRECISION:
        return str(price)
    precision = SYMBOL_PRECISION[symbol]
    price_step = precision["price_step"]
    # 计算需要的小数位数
    if price_step >= 1:
        decimal_places = 0
    else:
        decimal_places = len(str(price_step).rstrip('0').split('.')[-1])
    return f"{price:.{decimal_places}f}"


def generate_signature(secret_key: str, timestamp: str, method: str, request_path: str, query_string: str, body: str = "") -> str:
    """生成 API 签名"""
    message = timestamp + method.upper() + request_path + query_string + str(body)
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def send_request(method: str, request_path: str, query_string: str = "", body: Optional[Dict] = None, verbose: bool = False) -> requests.Response:
    """发送 API 请求"""
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(body) if body else ""
    
    signature = generate_signature(secret_key, timestamp, method, request_path, query_string, body_str)
    
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": access_passphrase,
        "Content-Type": "application/json",
        "locale": "zh-CN"
    }
    
    url = BASE_URL + request_path
    if query_string:
        if query_string.startswith("?"):
            url += query_string
        else:
            url += "?" + query_string
    
    proxies = None
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"📤 请求详情")
        print(f"{'='*60}")
        print(f"端点: {request_path}")
        print(f"完整URL: {url}")
        print(f"方法: {method}")
        print(f"请求头:")
        masked_headers = headers.copy()
        masked_headers["ACCESS-KEY"] = masked_headers["ACCESS-KEY"][:10] + "***"
        masked_headers["ACCESS-SIGN"] = masked_headers["ACCESS-SIGN"][:20] + "***"
        masked_headers["ACCESS-PASSPHRASE"] = "***"
        for k, v in masked_headers.items():
            print(f"  {k}: {v}")
        print(f"请求体: {body_str}")
        if proxies:
            print(f"代理: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")
    
    if method == "GET":
        response = requests.get(url, headers=headers, proxies=proxies)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=body_str, proxies=proxies)
    
    if verbose:
        print(f"\n📥 响应详情")
        print(f"{'='*60}")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应体: {response.text}")
        print(f"{'='*60}\n")
    
    return response


def print_json(data: Any, indent: int = 2):
    """格式化打印 JSON"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


# ==================== API 功能函数 ====================

def get_account_assets(verbose: bool = False) -> Optional[Dict]:
    """获取账户资产"""
    request_path = "/capi/v2/account/assets"
    response = send_request("GET", request_path, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询账户资产失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def get_ticker(symbol: str, verbose: bool = False) -> Optional[Dict]:
    """获取价格行情"""
    request_path = "/capi/v2/market/ticker"
    query_string = f"?symbol={symbol}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询价格失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def get_current_orders(symbol: str, verbose: bool = False) -> Optional[List]:
    """获取当前活跃订单"""
    request_path = "/capi/v2/order/current"
    query_string = f"?symbol={symbol}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        data = response.json()
        # API 可能返回数组或包装在 data/list 中
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            elif "list" in data and isinstance(data["list"], list):
                return data["list"]
        return []
    else:
        print(f"❌ 查询当前订单失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def get_order_history(symbol: str, page_size: int = 10, verbose: bool = False) -> Optional[Dict]:
    """获取历史订单"""
    request_path = "/capi/v2/order/history"
    query_string = f"?symbol={symbol}&pageSize={page_size}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询历史订单失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def get_trade_fills(symbol: str, page_size: int = 10, verbose: bool = False) -> Optional[Dict]:
    """获取成交记录"""
    request_path = "/capi/v2/order/fills"
    query_string = f"?symbol={symbol}&pageSize={page_size}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询成交记录失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def get_single_position(symbol: str, verbose: bool = False) -> Optional[Dict]:
    """获取单个合约的仓位信息"""
    request_path = "/capi/v2/account/position/singlePosition"
    query_string = f"?symbol={symbol}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        if verbose:
            print(f"⚠️  查询 {symbol} 仓位失败: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
        return None


def get_all_positions(verbose: bool = False) -> List[Dict]:
    """获取全部合约的仓位信息"""
    print("正在获取全部合约的仓位信息...")
    
    # 所有支持的交易对列表
    all_symbols = list(SYMBOL_PRECISION.keys())
    
    positions = []
    for symbol in all_symbols:
        position_data = get_single_position(symbol, verbose=False)  # 不显示每个的详细日志
        
        if position_data:
            # 处理不同的响应格式
            if isinstance(position_data, dict):
                # 检查是否有仓位数据
                if "data" in position_data:
                    pos = position_data["data"]
                    if pos and (isinstance(pos, dict) and (pos.get("size") or pos.get("amount"))):
                        positions.append({
                            "symbol": symbol,
                            **pos
                        })
                elif position_data.get("size") or position_data.get("amount"):
                    # 直接是仓位数据
                    positions.append({
                        "symbol": symbol,
                        **position_data
                    })
    
    return positions


def get_leverage(symbol: str, verbose: bool = False) -> Optional[Dict]:
    """获取杠杆信息"""
    request_path = "/capi/v2/account/leverage"
    query_string = f"?symbol={symbol}"
    response = send_request("GET", request_path, query_string=query_string, verbose=verbose)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 查询杠杆信息失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def set_leverage(symbol: str, margin_mode: int, long_leverage: str, short_leverage: str, verbose: bool = False) -> bool:
    """设置杠杆"""
    request_path = "/capi/v2/account/leverage"
    body = {
        "symbol": symbol,
        "marginMode": margin_mode,  # 1 = 全仓模式, 2 = 逐仓模式
        "longLeverage": long_leverage,
        "shortLeverage": short_leverage
    }
    response = send_request("POST", request_path, body=body, verbose=verbose)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ 设置杠杆失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return False


def place_order(symbol: str, side: str, order_type: str, size: float, price: Optional[float] = None, verbose: bool = False) -> Optional[str]:
    """下单"""
    # 调整精度
    adjusted_size = adjust_size_to_precision(size, symbol)
    
    # 构建请求体
    client_oid = str(int(time.time() * 1000))
    side_type = "1" if side == "buy" else "2"  # "1"=开多(买), "2"=开空(卖)
    match_price = "1" if order_type == "market" else "0"  # "0"=限价, "1"=市价
    
    body = {
        "symbol": symbol,
        "client_oid": client_oid,
        "size": str(adjusted_size),
        "type": side_type,
        "order_type": "0",  # 普通订单
        "match_price": match_price,
    }
    
    # 处理价格
    if order_type == "limit":
        if price is None:
            print("❌ 限价单必须指定价格")
            return None
        adjusted_price = adjust_price_to_precision(price, symbol)
        body["price"] = format_price_string(adjusted_price, symbol)
    else:
        # 市价单也需要价格字段（可能不生效）
        body["price"] = "0"
    
    if verbose:
        print(f"\n下单参数:")
        print(f"  交易对: {symbol}")
        print(f"  方向: {side} ({side_type})")
        print(f"  类型: {order_type} (match_price={match_price})")
        print(f"  数量: {size} -> {adjusted_size} (已调整精度)")
        if price:
            print(f"  价格: {price} -> {body.get('price')} (已调整精度)")
        print(f"  client_oid: {client_oid}")
    
    response = send_request("POST", "/capi/v2/order/placeOrder", body=body, verbose=verbose)
    
    if response.status_code == 200:
        data = response.json()
        order_id = None
        if isinstance(data, dict):
            order_id = data.get("order_id") or data.get("orderId") or data.get("data")
        if order_id:
            print(f"\n✅ 订单创建成功! 订单ID: {order_id}")
            return str(order_id)
        else:
            print(f"\n✅ 订单可能已创建，但未获取到订单ID")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return "unknown"
    else:
        print(f"\n❌ 下单失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def cancel_order(order_id: str, verbose: bool = False) -> bool:
    """取消订单"""
    request_path = "/capi/v2/order/cancel_order"
    body = {
        "orderId": order_id
    }
    response = send_request("POST", request_path, body=body, verbose=verbose)
    
    if response.status_code == 200:
        print(f"\n✅ 订单取消成功")
        return True
    else:
        print(f"\n❌ 订单取消失败: {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return False


# ==================== CLI 命令处理 ====================

def cmd_account(args):
    """查询账户余额"""
    print("查询账户资产...")
    data = get_account_assets(verbose=args.verbose)
    if data:
        print("\n账户资产:")
        print_json(data)


def cmd_price(args):
    """查询价格"""
    print(f"获取 {args.symbol} 价格...")
    data = get_ticker(args.symbol, verbose=args.verbose)
    if data:
        print(f"\n{args.symbol} 行情信息:")
        print_json(data)


def cmd_orders(args):
    """查询当前活跃订单"""
    print(f"查询 {args.symbol} 的当前活跃订单...")
    orders = get_current_orders(args.symbol, verbose=args.verbose)
    if orders is not None:
        if len(orders) == 0:
            print("\n✅ 当前没有活跃订单")
        else:
            print(f"\n✅ 找到 {len(orders)} 个活跃订单:")
            print_json(orders)


def cmd_history(args):
    """查询历史订单"""
    print(f"查询 {args.symbol} 的历史订单...")
    data = get_order_history(args.symbol, page_size=args.size, verbose=args.verbose)
    if data:
        print("\n历史订单:")
        print_json(data)


def cmd_fills(args):
    """查询成交记录"""
    print(f"查询 {args.symbol} 的成交记录...")
    data = get_trade_fills(args.symbol, page_size=args.size, verbose=args.verbose)
    if data:
        print("\n成交记录:")
        print_json(data)


def cmd_positions(args):
    """查询仓位信息"""
    if args.symbol:
        # 查询单个合约的仓位
        print(f"查询 {args.symbol} 的仓位信息...")
        data = get_single_position(args.symbol, verbose=args.verbose)
        if data:
            print(f"\n{args.symbol} 仓位信息:")
            print_json(data)
        else:
            print(f"\n⚠️  {args.symbol} 没有持仓或查询失败")
    else:
        # 查询全部合约的仓位
        positions = get_all_positions(verbose=args.verbose)
        
        if len(positions) == 0:
            print("\n✅ 当前没有持仓")
        else:
            print(f"\n✅ 找到 {len(positions)} 个合约的持仓:")
            print("\n" + "="*80)
            
            # 格式化显示
            total_value = 0
            for pos in positions:
                symbol = pos.get("symbol", "unknown")
                size = pos.get("size") or pos.get("amount") or "0"
                side = pos.get("side") or pos.get("positionSide") or "unknown"
                entry_price = pos.get("entryPrice") or pos.get("avgPrice") or "0"
                mark_price = pos.get("markPrice") or pos.get("currentPrice") or "0"
                unrealized_pnl = pos.get("unrealizedPnl") or pos.get("unrealizedPNL") or "0"
                leverage = pos.get("leverage") or "1"
                
                # 计算持仓价值
                try:
                    size_float = float(size)
                    mark_price_float = float(mark_price)
                    value = size_float * mark_price_float
                    total_value += value
                except:
                    value = 0
                
                print(f"\n📊 {symbol}")
                print(f"  方向: {side}")
                print(f"  数量: {size}")
                print(f"  杠杆: {leverage}x")
                print(f"  开仓价: {entry_price}")
                print(f"  标记价: {mark_price}")
                print(f"  未实现盈亏: {unrealized_pnl} USDT")
                print(f"  持仓价值: {value:.2f} USDT")
            
            print("\n" + "="*80)
            print(f"总持仓价值: {total_value:.2f} USDT")
            print("="*80)
            
            # 如果需要，也输出JSON格式
            if args.verbose:
                print("\n完整数据 (JSON):")
                print_json(positions)


def cmd_leverage_get(args):
    """查询杠杆信息"""
    print(f"查询 {args.symbol} 的杠杆信息...")
    data = get_leverage(args.symbol, verbose=args.verbose)
    if data:
        print("\n杠杆信息:")
        print_json(data)


def cmd_leverage_set(args):
    """设置杠杆"""
    print(f"设置 {args.symbol} 杠杆: 做多={args.long}x, 做空={args.short}x, 模式={args.mode}")
    success = set_leverage(
        args.symbol,
        args.mode,
        str(args.long),
        str(args.short),
        verbose=args.verbose
    )
    if success:
        print("\n✅ 杠杆设置成功")


def cmd_order(args):
    """下单"""
    print(f"下单: {args.side} {args.type} {args.symbol} {args.size} USDT...")
    
    price = None
    if args.type == "limit":
        if not args.price:
            print("❌ 限价单必须指定价格 (--price)")
            return
        price = float(args.price)
    
    order_id = place_order(
        args.symbol,
        args.side,
        args.type,
        float(args.size),
        price=price,
        verbose=args.verbose
    )
    
    if order_id:
        print(f"\n订单ID: {order_id}")
        if order_id == "unknown":
            print("提示: 如果查询不到订单，可能是订单已立即成交。")
            print("      限价单如果价格接近市价，可能会立即成交。")


def cmd_cancel(args):
    """取消订单"""
    print(f"取消订单: {args.order_id}")
    cancel_order(args.order_id, verbose=args.verbose)


def main():
    parser = argparse.ArgumentParser(
        description="WEEX Trading CLI Tool - WEEX合约交易命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询账户余额
  weex-cli account

  # 查询价格
  weex-cli price -s cmt_btcusdt

  # 下限价买单
  weex-cli order -s cmt_btcusdt -d buy -t limit -z 10 --price 80000

  # 下市价买单
  weex-cli order -s cmt_btcusdt -d buy -t market -z 10

  # 查询当前订单
  weex-cli orders -s cmt_btcusdt

  # 查询历史订单
  weex-cli history -s cmt_btcusdt

  # 查询成交记录
  weex-cli fills -s cmt_btcusdt

  # 查询单个合约仓位
  weex-cli positions -s cmt_btcusdt

  # 查询全部合约仓位
  weex-cli positions

  # 查询杠杆
  weex-cli leverage get -s cmt_btcusdt

  # 设置杠杆
  weex-cli leverage set -s cmt_btcusdt --long 20 --short 20 --mode 1

环境变量:
  WEEX_API_KEY: API密钥
  WEEX_SECRET_KEY: 密钥
  WEEX_PASSPHRASE: 密码短语
  WEEX_PROXY: 代理地址 (可选)
  WEEX_API_BASE_URL: API基础URL (可选，默认: https://api-contract.weex.com)
        """
    )
    
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细的请求和响应信息")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # account 命令
    parser_account = subparsers.add_parser("account", help="查询账户余额")
    parser_account.set_defaults(func=cmd_account)
    
    # price 命令
    parser_price = subparsers.add_parser("price", help="查询价格")
    parser_price.add_argument("-s", "--symbol", required=True, help="交易对符号 (例如: cmt_btcusdt)")
    parser_price.set_defaults(func=cmd_price)
    
    # orders 命令
    parser_orders = subparsers.add_parser("orders", help="查询当前活跃订单")
    parser_orders.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_orders.set_defaults(func=cmd_orders)
    
    # history 命令
    parser_history = subparsers.add_parser("history", help="查询历史订单")
    parser_history.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_history.add_argument("--size", type=int, default=10, help="返回数量 (默认: 10)")
    parser_history.set_defaults(func=cmd_history)
    
    # fills 命令
    parser_fills = subparsers.add_parser("fills", help="查询成交记录")
    parser_fills.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_fills.add_argument("--size", type=int, default=10, help="返回数量 (默认: 10)")
    parser_fills.set_defaults(func=cmd_fills)
    
    # positions 命令
    parser_positions = subparsers.add_parser("positions", help="查询仓位信息")
    parser_positions.add_argument("-s", "--symbol", help="交易对符号 (可选，不指定则查询全部合约)")
    parser_positions.set_defaults(func=cmd_positions)
    
    # leverage 子命令
    parser_leverage = subparsers.add_parser("leverage", help="杠杆相关操作")
    leverage_subparsers = parser_leverage.add_subparsers(dest="leverage_action", help="杠杆操作")
    
    # leverage get
    parser_leverage_get = leverage_subparsers.add_parser("get", help="查询杠杆信息")
    parser_leverage_get.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_leverage_get.set_defaults(func=cmd_leverage_get)
    
    # leverage set
    parser_leverage_set = leverage_subparsers.add_parser("set", help="设置杠杆")
    parser_leverage_set.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_leverage_set.add_argument("--long", type=int, required=True, help="做多杠杆倍数")
    parser_leverage_set.add_argument("--short", type=int, required=True, help="做空杠杆倍数")
    parser_leverage_set.add_argument("--mode", type=int, required=True, help="保证金模式 (1=全仓, 2=逐仓)")
    parser_leverage_set.set_defaults(func=cmd_leverage_set)
    
    # order 命令
    parser_order = subparsers.add_parser("order", help="下单")
    parser_order.add_argument("-s", "--symbol", required=True, help="交易对符号")
    parser_order.add_argument("-d", "--side", choices=["buy", "sell"], required=True, help="方向 (buy/sell)")
    parser_order.add_argument("-t", "--type", choices=["market", "limit"], required=True, help="订单类型 (market/limit)")
    parser_order.add_argument("-z", "--size", required=True, help="订单数量")
    parser_order.add_argument("--price", help="价格 (限价单必需)")
    parser_order.set_defaults(func=cmd_order)
    
    # cancel 命令
    parser_cancel = subparsers.add_parser("cancel", help="取消订单")
    parser_cancel.add_argument("order_id", help="订单ID")
    parser_cancel.set_defaults(func=cmd_cancel)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 处理 leverage 子命令
    if args.command == "leverage":
        if not args.leverage_action:
            parser_leverage.print_help()
            sys.exit(1)
        args.func = cmd_leverage_get if args.leverage_action == "get" else cmd_leverage_set
    
    args.func(args)


if __name__ == "__main__":
    main()
