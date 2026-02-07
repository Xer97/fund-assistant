#!/usr/bin/env python3
"""
持仓管理脚本
用法：
    python portfolio.py init                           # 初始化数据目录
    python portfolio.py list                           # 查看持仓列表
    python portfolio.py add 001618 1000 1.5 [备注]     # 添加持仓
    python portfolio.py update 001618 shares=1500     # 更新持仓
    python portfolio.py remove 001618                  # 删除持仓
    python portfolio.py user [用户名]                  # 切换/查看用户
    python portfolio.py users                          # 列出所有用户
    python portfolio.py export [文件路径]              # 导出持仓
    python portfolio.py import 文件路径                # 导入持仓
"""

import sys
import os
import json
from datetime import datetime
import uuid

# 数据目录（项目本地）
DATA_DIR = ".fund-assistant"
CONFIG_FILE = "config.json"
PORTFOLIO_FILE = "portfolio.json"
TRANSACTIONS_FILE = "transactions.json"

def get_data_dir():
    """获取数据目录路径"""
    return os.path.join(os.getcwd(), DATA_DIR)

def get_config_path():
    """获取配置文件路径"""
    return os.path.join(get_data_dir(), CONFIG_FILE)

def get_user_dir(user=None):
    """获取用户数据目录"""
    if user is None:
        user = get_current_user()
    return os.path.join(get_data_dir(), "users", user)

def get_portfolio_path(user=None):
    """获取持仓文件路径"""
    return os.path.join(get_user_dir(user), PORTFOLIO_FILE)

def get_transactions_path(user=None):
    """获取交易记录文件路径"""
    return os.path.join(get_user_dir(user), TRANSACTIONS_FILE)

def get_current_user():
    """获取当前用户"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("currentUser", "default")
    return "default"

def set_current_user(user):
    """设置当前用户"""
    config_path = get_config_path()
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

    config["currentUser"] = user
    config["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def init_data():
    """初始化数据目录"""
    user_dir = get_user_dir()
    os.makedirs(user_dir, exist_ok=True)

    portfolio_path = get_portfolio_path()
    if not os.path.exists(portfolio_path):
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump({
                "funds": [],
                "updatedAt": datetime.utcnow().isoformat() + "Z"
            }, f, ensure_ascii=False, indent=2)

    transactions_path = get_transactions_path()
    if not os.path.exists(transactions_path):
        with open(transactions_path, 'w', encoding='utf-8') as f:
            json.dump({
                "records": [],
                "updatedAt": datetime.utcnow().isoformat() + "Z"
            }, f, ensure_ascii=False, indent=2)

    return {"status": "ok", "path": user_dir, "user": get_current_user()}

def load_portfolio():
    """加载持仓数据"""
    path = get_portfolio_path()
    if not os.path.exists(path):
        return {"funds": []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_portfolio(data):
    """保存持仓数据"""
    data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    path = get_portfolio_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_portfolio():
    """列出持仓"""
    data = load_portfolio()
    return {
        "user": get_current_user(),
        "funds": data.get("funds", []),
        "count": len(data.get("funds", []))
    }

def add_fund(code, shares, cost, note=""):
    """添加持仓"""
    data = load_portfolio()
    funds = data.get("funds", [])

    # 检查是否已存在
    for fund in funds:
        if fund["code"] == code:
            return {"error": f"基金 {code} 已存在，请使用 update 命令更新"}

    funds.append({
        "code": code,
        "name": "",  # 名称由 API 查询填充
        "shares": float(shares),
        "cost": float(cost),
        "note": note,
        "addedAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    })

    data["funds"] = funds
    save_portfolio(data)
    return {"status": "ok", "code": code, "shares": shares, "cost": cost}

def update_fund(code, **kwargs):
    """更新持仓"""
    data = load_portfolio()
    funds = data.get("funds", [])

    for fund in funds:
        if fund["code"] == code:
            for key, value in kwargs.items():
                if key in ["shares", "cost"]:
                    fund[key] = float(value)
                elif key in ["name", "note"]:
                    fund[key] = value
            fund["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            save_portfolio(data)
            return {"status": "ok", "fund": fund}

    return {"error": f"基金 {code} 不存在"}

def remove_fund(code):
    """删除持仓"""
    data = load_portfolio()
    funds = data.get("funds", [])

    new_funds = [f for f in funds if f["code"] != code]
    if len(new_funds) == len(funds):
        return {"error": f"基金 {code} 不存在"}

    data["funds"] = new_funds
    save_portfolio(data)
    return {"status": "ok", "code": code}

def list_users():
    """列出所有用户"""
    users_dir = os.path.join(get_data_dir(), "users")
    if not os.path.exists(users_dir):
        return {"users": [], "current": get_current_user()}

    users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
    return {"users": users, "current": get_current_user()}

def switch_user(user):
    """切换用户"""
    set_current_user(user)
    init_data()  # 确保用户目录存在
    return {"status": "ok", "user": user}

def export_portfolio(filepath=None):
    """导出持仓"""
    data = load_portfolio()
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "ok", "path": filepath}
    return data

def import_portfolio(filepath):
    """导入持仓"""
    if not os.path.exists(filepath):
        return {"error": f"文件不存在: {filepath}"}

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "funds" not in data:
        return {"error": "无效的持仓文件格式"}

    save_portfolio(data)
    return {"status": "ok", "count": len(data.get("funds", []))}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        result = init_data()
    elif cmd == "list":
        result = list_portfolio()
    elif cmd == "add" and len(sys.argv) >= 5:
        note = sys.argv[5] if len(sys.argv) > 5 else ""
        result = add_fund(sys.argv[2], sys.argv[3], sys.argv[4], note)
    elif cmd == "update" and len(sys.argv) >= 4:
        kwargs = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                kwargs[key] = value
        result = update_fund(sys.argv[2], **kwargs)
    elif cmd == "remove" and len(sys.argv) >= 3:
        result = remove_fund(sys.argv[2])
    elif cmd == "user":
        if len(sys.argv) > 2:
            result = switch_user(sys.argv[2])
        else:
            result = {"user": get_current_user()}
    elif cmd == "users":
        result = list_users()
    elif cmd == "export":
        filepath = sys.argv[2] if len(sys.argv) > 2 else None
        result = export_portfolio(filepath)
    elif cmd == "import" and len(sys.argv) >= 3:
        result = import_portfolio(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
