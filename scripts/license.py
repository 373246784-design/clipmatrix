"""
License 验证模块 — 免费试用 + Gumroad License验证
"""
import os, sys, json, time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

INSTALL_FILE = Path.home() / ".clipmatrix_install"
GUMROAD_VERIFY = "https://api.gumroad.com/v2/licenses/verify"
PRODUCT_PERMALINK = "uunfl"


def _get_install_days() -> int:
    if not INSTALL_FILE.exists():
        return 0
    try:
        installed_at = float(INSTALL_FILE.read_text().strip())
        return (datetime.now() - datetime.fromtimestamp(installed_at)).days
    except (ValueError, OSError):
        return 0


def _record_install():
    if not INSTALL_FILE.exists():
        INSTALL_FILE.parent.mkdir(parents=True, exist_ok=True)
        INSTALL_FILE.write_text(str(datetime.now().timestamp()))


def _get_license_key(config: dict) -> str:
    return config.get("license", {}).get("key", "").strip()


def check_license(config: dict, silent: bool = False) -> dict:
    license_config = config.get("license", {})
    license_key = _get_license_key(config)
    enable_trial = license_config.get("enable_trial", True)
    trial_days = license_config.get("trial_days", 7)

    # 有 License Key → Gumroad 在线验证
    if license_key:
        return _validate_gumroad(license_key, silent)

    # 试用模式
    if not enable_trial:
        return {"valid": False, "plan": "locked", "message": "🔒 License required."}

    _record_install()
    days = _get_install_days()

    if days <= trial_days:
        remaining = trial_days - days
        msg = f"🎉 Free trial: Day {days}/{trial_days}"
        if remaining <= 2:
            msg += f" — {remaining} days left!"
        return {"valid": True, "plan": "trial", "remaining_days": remaining, "message": msg}

    store_url = license_config.get("store_url", "https://zplaze.gumroad.com/l/uunfl")
    return {
        "valid": False, "plan": "trial_expired",
        "message": (
            f"⏰ Free trial expired.\n"
            f"   👉 {store_url}\n"
            f"   Got a key? Add to config.yaml → license.key"
        )
    }


def _validate_gumroad(license_key: str, silent: bool = False) -> dict:
    if not requests:
        print("⚠️  pip install requests")
        return {"valid": True, "plan": "pro", "message": "✅ License accepted (offline)"}

    try:
        r = requests.post(GUMROAD_VERIFY, data={
            "product_permalink": PRODUCT_PERMALINK,
            "license_key": license_key,
        }, timeout=10)

        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                purchase = data.get("purchase", {})
                return {
                    "valid": True, "plan": "pro",
                    "message": f"✅ License valid — {purchase.get('email', 'Pro')}"
                }
            else:
                return {"valid": False, "plan": "invalid",
                        "message": f"🔒 {data.get('message', 'License invalid or expired')}"}

        if r.status_code == 404:
            return {"valid": False, "plan": "invalid", "message": "🔒 License key not found"}

    except requests.RequestException as e:
        print(f"⚠️  Network: {e}")
        return {"valid": True, "plan": "pro", "message": "✅ License accepted (cached)"}

    return {"valid": False, "plan": "invalid", "message": "🔒 Validation failed"}


def require_license(config: dict):
    result = check_license(config)
    print(f"\n  {result['message']}")
    if not result["valid"]:
        print("\n❌ Cannot continue without valid license.\n")
        sys.exit(1)
    return result
