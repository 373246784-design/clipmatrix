#!/usr/bin/env python3
"""
M1 独立站数据 — Cloudflare GraphQL Analytics
拉取 Panda-Journeys.com 的 PV/UV/热门页面/WAF 拦截数据

用法:
  from m1_independent_site import fetch_site_data, format_site_html, format_site_summary
  
  data = fetch_site_data()           # 拉7天数据
  html = format_site_html(data)      # HTML块（嵌入M1报告）
  text = format_site_summary(data)   # 文本块（注入M1策略）
"""

import json, urllib.request, os, logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cloudflare 配置
CF_ZONE_TAG = "05d6b8db2d4e04e3b985e7fa9c91f60f"
CF_ACCOUNT_ID = "e0373fa5ae5a4aaf88d81b5b4a0bc1c5"
CF_GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"

# Token: 优先环境变量 → config文件 → 留空
CF_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "") or os.environ.get("CF_API_TOKEN", "")
if not CF_API_TOKEN:
    _token_paths = [
        os.path.expanduser("~/.openclaw/workspace/pandajourneys/config/cf_api_token.txt"),
        "/tmp/cf_api_token.txt",
    ]
    for _tp in _token_paths:
        if os.path.exists(_tp):
            with open(_tp) as _f:
                CF_API_TOKEN = _f.read().strip()
            break


def _graphql(query: str, token: str = None) -> dict:
    """执行 Cloudflare GraphQL 查询"""
    token = token or CF_API_TOKEN
    if not token:
        raise ValueError("CF_API_TOKEN 未配置。请在环境变量设置 CLOUDFLARE_API_TOKEN")
    
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        CF_GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    
    if result.get("errors"):
        err_msgs = [e.get("message", str(e)) for e in result["errors"]]
        raise RuntimeError(f"GraphQL errors: {'; '.join(err_msgs)}")
    
    return result.get("data", {})


def fetch_site_data(days: int = 7, token: str = None) -> dict:
    """
    拉取独立站数据
    
    Returns:
        {
            "daily": [{"date": "...", "pv": N, "uv": N, "requests": N, "bytes": N}, ...],
            "top_pages": [{"path": "...", "requests": N, "pv": N}, ...],
            "waf": {"total_blocked": N, "rules": [...]},
            "summary": {"total_pv": N, "total_uv": N, "daily_avg_pv": N, "daily_avg_uv": N}
        }
    """
    token = token or CF_API_TOKEN
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    result = {"daily": [], "top_pages": [], "waf": {}, "summary": {}}
    
    # ── 1. 每日PV/UV趋势 (httpRequests1dGroups) ──
    # 免费版无 uniqueVisitors，用 pageViews + bytes
    query_daily = f"""
    {{
      viewer {{
        zones(filter: {{zoneTag: "{CF_ZONE_TAG}"}}) {{
          httpRequests1dGroups(
            filter: {{date_geq: "{start_date.strftime('%Y-%m-%d')}", date_lt: "{end_date.strftime('%Y-%m-%d')}"}},
            limit: {days + 2}
          ) {{
            dimensions {{ date }}
            sum {{ pageViews bytes }}
          }}
        }}
      }}
    }}
    """
    
    try:
        data = _graphql(query_daily, token)
        zones = data.get("viewer", {}).get("zones", [])
        if zones:
            for group in zones[0].get("httpRequests1dGroups", []):
                dims = group.get("dimensions", {})
                sums = group.get("sum", {})
                result["daily"].append({
                    "date": dims.get("date", ""),
                    "pv": sums.get("pageViews", 0),
                    "uv": 0,  # 免费版不提供 uniqueVisitors
                    "requests": 0,  # 免费版不提供
                    "bytes": sums.get("bytes", 0),
                })
    except Exception as e:
        logger.warning(f"每日数据拉取失败: {e}")
    except Exception as e:
        logger.warning(f"每日数据拉取失败: {e}")
    
    # ── 2. 热门页面 (httpRequestsAdaptiveGroups, 最近24h, count代替sum) ──
    query_pages = f"""
    {{
      viewer {{
        zones(filter: {{zoneTag: "{CF_ZONE_TAG}"}}) {{
          httpRequestsAdaptiveGroups(
            filter: {{
              datetime_geq: "{(end_date - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')}",
              datetime_lt: "{end_date.strftime('%Y-%m-%dT00:00:00Z')}"
            }},
            limit: 30
          ) {{
            count
            dimensions {{ clientRequestPath }}
          }}
        }}
      }}
    }}
    """
    
    try:
        data = _graphql(query_pages, token)
        zones = data.get("viewer", {}).get("zones", [])
        if zones:
            for group in zones[0].get("httpRequestsAdaptiveGroups", []):
                dims = group.get("dimensions", {})
                cnt = group.get("count", 0)
                path = dims.get("clientRequestPath", "/")
                # 过滤静态资源 + 扫描路径 + 攻击流量
                skip_patterns = [".js", ".css", ".png", ".jpg", ".ico", ".svg", ".woff2",
                                ".woff", ".ttf", ".webp", ".xml", ".php"]
                skip_prefixes = ["wp-", ".env", "admin", "blog/", "website/", "wordpress",
                                "backup", "curl/", "shell", "cgi-bin/", "test/"]
                if any(path.endswith(ext) for ext in skip_patterns):
                    continue
                if any(path.lower().startswith(p) or p in path.lower() for p in skip_prefixes):
                    continue
                result["top_pages"].append({
                    "path": path,
                    "requests": cnt,
                    "pv": cnt,  # 免费版 count 近似
                })
        # 按请求数排序
        result["top_pages"].sort(key=lambda x: x["requests"], reverse=True)
        result["top_pages"] = result["top_pages"][:15]
    except Exception as e:
        logger.warning(f"热门页面拉取失败: {e}")
    except Exception as e:
        logger.warning(f"热门页面拉取失败: {e}")
    
    # ── 3. WAF 拦截统计 (wp- 路径) ──
    query_waf = f"""
    {{
      viewer {{
        zones(filter: {{zoneTag: "{CF_ZONE_TAG}"}}) {{
          httpRequestsAdaptiveGroups(
            filter: {{
              datetime_geq: "{(end_date - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')}",
              datetime_lt: "{end_date.strftime('%Y-%m-%dT00:00:00Z')}",
              clientRequestPath_like: "%wp-%"
            }},
            limit: 10
          ) {{
            count
            dimensions {{ clientRequestPath }}
          }}
        }}
      }}
    }}
    """
    
    try:
        data = _graphql(query_waf, token)
        zones = data.get("viewer", {}).get("zones", [])
        waf_rules = []
        total_blocked = 0
        if zones:
            for group in zones[0].get("httpRequestsAdaptiveGroups", []):
                dims = group.get("dimensions", {})
                cnt = group.get("count", 0)
                total_blocked += cnt
                waf_rules.append({
                    "path": dims.get("clientRequestPath", ""),
                    "requests": cnt,
                })
        result["waf"] = {"total_blocked": total_blocked, "rules": waf_rules}
    except Exception as e:
        logger.warning(f"WAF数据拉取失败: {e}")
    
    # ── 4. 汇总 ──
    daily = result["daily"]
    total_pv = sum(d.get("pv", 0) for d in daily)
    total_uv = sum(d.get("uv", 0) for d in daily)
    n = len(daily) or 1
    
    result["summary"] = {
        "total_pv": total_pv,
        "total_uv": total_uv,
        "daily_avg_pv": total_pv // n,
        "daily_avg_uv": total_uv // n,
        "days": n,
    }
    
    return result


def format_site_summary(data: dict) -> str:
    """
    文本摘要 — 注入 M1 策略 prompt
    
    格式: 简短中文摘要，供 DeepSeek 在分析趋势时参考
    """
    s = data.get("summary", {})
    if not s.get("total_pv"):
        return ""
    
    lines = [
        f"独立站 {s['days']}天数据: {s['total_pv']:,} PV / {s['total_uv']:,} UV",
        f"日均: {s['daily_avg_pv']} PV / {s['daily_avg_uv']} UV",
    ]
    
    # 热门页面
    pages = data.get("top_pages", [])[:3]
    if pages:
        lines.append("热门页面: " + ", ".join(f"{p['path']}({p['pv']})" for p in pages))
    
    # WAF
    waf = data.get("waf", {})
    if waf.get("total_blocked", 0) > 0:
        lines.append(f"WAF拦截: {waf['total_blocked']}次 (wp扫描已屏蔽)")
    
    return " | ".join(lines)


def format_site_html(data: dict) -> str:
    """
    HTML块 — 嵌入 M1 报告
    """
    s = data.get("summary", {})
    daily = data.get("daily", [])
    pages = data.get("top_pages", [])
    waf = data.get("waf", {})
    
    if not s.get("total_pv"):
        return '<p style="color:#64748b;font-size:12px">🌐 独立站数据: 暂无 (需配置 CLOUDFLARE_API_TOKEN)</p>'
    
    # ── 概览卡片 ──
    cards = f"""
    <div class="cards">
      <div class="card"><div class="n">{s['total_pv']:,}</div><div class="l">{s['days']}天总PV</div></div>
      <div class="card"><div class="n">{s['total_uv']:,}</div><div class="l">{s['days']}天总UV</div></div>
      <div class="card"><div class="n">{s['daily_avg_pv']}</div><div class="l">日均PV</div></div>
      <div class="card"><div class="n">{s['daily_avg_uv']}</div><div class="l">日均UV</div></div>
    </div>
    """
    
    # ── 每日趋势表 ──
    daily_rows = ""
    for d in daily:
        daily_rows += f"<tr><td>{d['date']}</td><td>{d['pv']:,}</td><td>{d['uv']:,}</td><td>{d['requests']:,}</td><td>{d['bytes']//1024//1024}MB</td></tr>"
    
    daily_table = f"""
    <table>
      <tr><th>日期</th><th>PV</th><th>UV</th><th>请求</th><th>流量</th></tr>
      {daily_rows}
    </table>
    """
    
    # ── 热门页面 ──
    page_rows = ""
    for p in pages[:10]:
        page_rows += f"<tr><td>{p['path'][:60]}</td><td>{p['pv']:,}</td><td>{p['requests']:,}</td></tr>"
    
    pages_table = f"""
    <table>
      <tr><th>页面</th><th>PV</th><th>请求</th></tr>
      {page_rows}
    </table>
    """ if page_rows else '<p style="color:#64748b;font-size:12px">暂无页面数据</p>'
    
    # ── WAF 状态 ──
    waf_html = ""
    if waf.get("total_blocked", 0) > 0:
        waf_html = f"""
        <div style="background:#1e293b;border-left:3px solid #4ade80;border-radius:6px;padding:10px;margin:8px 0;font-size:13px">
          🛡️ WAF防火墙: 24h拦截 <b style="color:#4ade80">{waf['total_blocked']:,}</b> 次扫描 (wp-admin/wp-login等)
        </div>
        """
    else:
        waf_html = '<p style="color:#64748b;font-size:12px">🛡️ WAF: 无拦截 (或数据暂未更新)</p>'
    
    return f"""
    <h2>🌐 独立站数据 — Panda-Journeys.com</h2>
    {cards}
    <h3 style="font-size:13px;color:#94a3b8;margin:10px 0 4px">📈 每日趋势</h3>
    {daily_table}
    <h3 style="font-size:13px;color:#94a3b8;margin:10px 0 4px">🔥 热门页面 (24h)</h3>
    {pages_table}
    {waf_html}
    """


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    token = CF_API_TOKEN
    if not token:
        print("❌ CLOUDFLARE_API_TOKEN 未设置")
        print("   export CLOUDFLARE_API_TOKEN=xxx")
        exit(1)
    
    print("📊 拉取独立站数据...")
    data = fetch_site_data(token=token)
    
    print(f"\n{format_site_summary(data)}")
    print(f"\n--- HTML Preview ---")
    print(format_site_html(data)[:500])
