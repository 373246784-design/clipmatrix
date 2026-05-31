"""
License 验证模块 — 免费试用 + LemonSqueezy订阅验证

流程:
  1. 首次运行 → 记录安装时间，7天免费试用
  2. 7天内 → M1-M5全开
  3. 过期 → 提示购买License
  4. 有License → 验证LemonSqueezy订阅状态 → 通过则全开

License Key 配置在 config.yaml:
  license:
    key: ""          # LemonSqueezy License Key
    enable_trial: true
    trial_days: 7
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

try:
    import requests
except ImportError:
    requests = None

# 安装时间文件（存在用户HOME下，不会被skill更新覆盖）
INSTALL_FILE = Path.home() / ".panda_workflow_install"

# LemonSqueezy API
LEMONSQUEEZY_API = "https://api.lemonsqueezy.com/v1/licenses/validate"


def _get_install_days() -> int:
    """返回安装至今的天数"""
    if not INSTALL_FILE.exists():
        return 0
    try:
        installed_at = float(INSTALL_FILE.read_text().strip())
        return (datetime.now() - datetime.fromtimestamp(installed_at)).days
    except (ValueError, OSError):
        return 0


def _record_install():
    """记录首次安装时间"""
    if not INSTALL_FILE.exists():
        INSTALL_FILE.parent.mkdir(parents=True, exist_ok=True)
        INSTALL_FILE.write_text(str(datetime.now().timestamp()))


def _get_license_key(config: dict) -> str:
    """从配置获取License Key"""
    return config.get("license", {}).get("key", "").strip()


def check_license(config: dict, silent: bool = False) -> dict:
    """
    验证License状态

    返回:
      {"valid": True, "plan": "trial", "remaining_days": 3, "message": ""}  # 试用中
      {"valid": True, "plan": "pro", "message": ""}                        # 已授权
      {"valid": False, "message": "..."}                                     # 过期/无效
    """
    license_config = config.get("license", {})
    license_key = _get_license_key(config)
    enable_trial = license_config.get("enable_trial", True)
    trial_days = license_config.get("trial_days", 7)

    # ========== 有License Key → 在线验证 ==========
    if license_key:
        return _validate_online(license_key, silent)

    # ========== 试用模式 ==========
    if not enable_trial:
        return {"valid": False, "plan": "locked",
                "message": "🔒 License required. Free trial disabled."}

    _record_install()
    days = _get_install_days()

    if days <= trial_days:
        remaining = trial_days - days
        msg = f"🎉 Free trial: Day {days}/{trial_days}"
        if remaining <= 2:
            msg += f" — {remaining} days left!"
        return {"valid": True, "plan": "trial", "remaining_days": remaining, "message": msg}

    # 试用过期
    return {
        "valid": False,
        "plan": "trial_expired",
        "message": (
            f"⏰ Free trial expired ({trial_days} days).\n"
            f"   To unlock M1-M5: {license_config.get('store_url', 'https://buy.example.com')}\n"
            f"   Got a License Key? Add to config.yaml → license.key"
        )
    }


def _validate_online(license_key: str, silent: bool = False) -> dict:
    """在线调用 LemonSqueezy 验证 License"""
    if not requests:
        if not silent:
            print("⚠️  requests not installed. Cannot validate license online.")
            print("   pip install requests")
        # 离线降级：允许运行（信任本地Key）
        return {"valid": True, "plan": "pro", "message": "✅ License accepted (offline mode)"}

    try:
        r = requests.post(LEMONSQUEEZY_API, json={
            "license_key": license_key,
            "instance_id": _get_instance_id(),
        }, timeout=10)

        if r.status_code == 200:
            data = r.json()
            if data.get("valid"):
                return {"valid": True, "plan": "pro",
                        "message": f"✅ License valid — {data.get('plan_name', 'Pro')}"}
            else:
                reason = data.get("message", "License invalid or expired")
                return {"valid": False, "plan": "invalid", "message": f"🔒 {reason}"}

    except requests.RequestException as e:
        if not silent:
            print(f"⚠️  License check failed (network): {e}")
        # 网络失败降级：允许已保存的license（宽容策略）
        return {"valid": True, "plan": "pro", "message": "✅ License accepted (cached)"}

    return {"valid": False, "plan": "invalid", "message": "🔒 License validation failed"}


def _get_instance_id() -> str:
    """生成设备唯一ID（硬件指纹）"""
    import hashlib
    import platform
    fingerprint = f"{platform.node()}-{Path.home()}-panda-workflow"
    return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]


def require_license(config: dict):
    """
    强制验证License。不通过直接 sys.exit(1)

    在 production_run.py 的 M1 之前调用:
      from license import require_license
      require_license(load_config())
    """
    result = check_license(config)
    print(f"\n  {result['message']}")
    if not result["valid"]:
        print("\n❌ Cannot continue without valid license.\n")
        sys.exit(1)
    return result
