#!/usr/bin/env python3
"""OFAC SDN / Consolidated 制裁名单变更监控（仅依赖 Python 标准库）。

用途：下载 OFAC 列表 XML，计算 SHA256，与本地基线比对，输出 Markdown 变更报告。
用于 us-sanctions-research skill 的步骤 7（持续监控）。

新增「关注实体（watchlist）实体级告警」：只报告你盯的实体（如 Zanjani / Dot One / 胡塞系）
是否新被列入、被移除（解除制裁）、或当前仍在名单中，便于收敛告警、避免每日全量噪音。

用法：
  python monitor_ofac.py                          # 默认监控 SDN 列表，首次运行建立基线
  python monitor_ofac.py --list consolidated      # 监控综合清单
  python monitor_ofac.py --watch watchlist.json   # 启用关注实体级告警（默认自动加载同目录 watchlist.json）
  python monitor_ofac.py --baseline base.json --out report.md

行为：
  - 首次运行：写入基线（hash + 条目名），报告"基线已建立"。
  - 后续运行：比对基线，报告新增/移除条目与 hash 是否变动。
  - 若加载到 watchlist：额外报告每个关注实体的当前状态与相对基线的变化（新列入/解除）。
  - 打印 Markdown 摘要到 stdout；指定 --out 时写文件。

端点：默认使用 OFAC 公开 XML 下载地址（见 ENDPOINTS）。
  ⚠️ 首次使用或在新环境部署前，请按 references/ofac_resources.md 核实链接有效性；
     OFAC 可能调整下载地址。可用 --url 覆盖。
"""
import argparse
import datetime
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

ENDPOINTS = {
    "sdn": "https://ofac.treasury.gov/downloads/sdn.xml",
    "consolidated": "https://ofac.treasury.gov/downloads/consolidated.xml",
}

# 内置默认关注实体（当用户未提供 watchlist.json 时使用）。
# 关键词做大小写不敏感子串匹配；命中即视为该实体在名单中。
DEFAULT_WATCH = [
    {"keywords": ["Babak Zanjani", "Zanjani"], "note": "伊朗受列名金融家，BITBANK 控制人"},
    {"keywords": ["Dot One"], "note": "伊朗受列名实体（Pishtaz / Dot One 系）"},
    {"keywords": ["Ansar Allah", "Houthi"], "note": "也门胡塞武装 SDGT（EO 13224）"},
    {"keywords": ["BITBANK"], "note": "伊朗数字资产交易所 SDN #58619"},
]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "OFAC-Monitor/1.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def extract_names(xml_bytes):
    """尽力抽取条目主名（OFAC SDN/Consolidated 均常用 <lastName> 承载主体名，含 aka）。"""
    names = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return names
    for el in root.iter():
        if el.tag.split("}")[-1].lower() == "lastName" and el.text and el.text.strip():
            names.append(el.text.strip())
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def default_watch_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "watchlist.json")


def load_watchlist(path):
    if path and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return DEFAULT_WATCH
        items = []
        for e in data:
            if isinstance(e, str):
                items.append({"keywords": [e], "note": ""})
            elif isinstance(e, dict):
                kws = e.get("keywords") or ([e["name"]] if e.get("name") else [])
                items.append({"keywords": kws, "note": e.get("note", "")})
        return items or DEFAULT_WATCH
    return DEFAULT_WATCH


def match_watch(names_lower, items):
    results = []
    for it in items:
        hits = []
        for kw in it.get("keywords", []):
            k = kw.lower()
            for n in names_lower:
                if k in n:
                    hits.append(n)
                    break
        results.append({"note": it.get("note", ""), "keywords": it.get("keywords", []), "hits": hits})
    return results


def render_watch(watch_now, watch_base, first_run):
    lines = ["", "### 关注实体（watchlist）实体级状态", f"- 关注实体数: {len(watch_now)}"]
    for i, now in enumerate(watch_now):
        is_now = bool(now["hits"])
        status = "在名单中" if is_now else "未在名单中"
        change = ""
        if not first_run:
            was = bool(watch_base[i]["hits"]) if i < len(watch_base) else False
            if is_now and not was:
                change = " 🔴 新被列入"
            elif not is_now and was:
                change = " 🟢 已解除制裁"
        matched = ", ".join(now["hits"][:3]) + ("…" if len(now["hits"]) > 3 else "") if now["hits"] else "—"
        kw = ", ".join(now["keywords"])
        lines.append(f"- [{status}{change}] 关键词: {kw}（{now['note']}）匹配: {matched}")
    return lines


def main():
    p = argparse.ArgumentParser(description="OFAC sanctions list change monitor (with watchlist)")
    p.add_argument("--list", choices=list(ENDPOINTS), default="sdn")
    p.add_argument("--baseline", default=None, help="baseline json path")
    p.add_argument("--out", default=None, help="write markdown report to this path")
    p.add_argument("--url", default=None, help="override endpoint url")
    p.add_argument("--watch", default=None, help="watchlist json path (default: watchlist.json beside script)")
    args = p.parse_args()

    url = args.url or ENDPOINTS[args.list]
    baseline_path = args.baseline or (f".ofac_baseline_{args.list}.json")

    try:
        data = fetch(url)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: failed to fetch {url}: {e}", file=sys.stderr)
        sys.exit(2)

    digest = sha256(data)
    names = extract_names(data)
    names_lower = [n.lower() for n in names]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    auto = default_watch_path() if os.path.exists(default_watch_path()) else None
    watch_path = args.watch or auto
    watch_items = load_watchlist(watch_path) if watch_path else DEFAULT_WATCH
    watch_now = match_watch(names_lower, watch_items)

    if not os.path.exists(baseline_path):
        baseline = {"hash": digest, "count": len(names), "names": names, "ts": ts}
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, ensure_ascii=False, indent=2)
        report = (
            f"## OFAC {args.list} 监控（基线已建立）\n\n"
            f"- 时间(UTC): {ts}\n- 数据源: {url}\n"
            f"- SHA256: `{digest[:16]}...`\n- 条目数: {len(names)}\n"
            f"- 基线文件: {baseline_path}\n\n首次运行，已记录基线。下次运行将比对变更。"
        )
        report += "\n".join(render_watch(watch_now, [], True))
        print(report)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
        return

    with open(baseline_path, encoding="utf-8") as f:
        base = json.load(f)

    base_names = set(base.get("names", []))
    added = [n for n in names if n not in base_names]
    removed = [n for n in base.get("names", []) if n not in set(names)]
    changed = digest != base.get("hash")

    base_lower = [n.lower() for n in base.get("names", [])]
    watch_base = match_watch(base_lower, watch_items)

    lines = [
        f"## OFAC {args.list} 监控报告",
        "",
        f"- 时间(UTC): {ts}",
        f"- 数据源: {url}",
        f"- 当前 SHA256: `{digest[:16]}...`",
        f"- 基线 SHA256: `{base.get('hash', '')[:16]}...`",
        f"- 当前条目数: {len(names)}（基线 {base.get('count', '?')}）",
        f"- 列表是否变动: {'是' if changed else '否'}",
    ]
    if added:
        lines += ["", f"### 新增（{len(added)}）"] + [f"- {n}" for n in added[:200]]
        if len(added) > 200:
            lines.append(f"- …（其余 {len(added) - 200} 条略）")
    if removed:
        lines += ["", f"### 移除（{len(removed)}）"] + [f"- {n}" for n in removed[:200]]
        if len(removed) > 200:
            lines.append(f"- …（其余 {len(removed) - 200} 条略）")
    if not added and not removed and not changed:
        lines += ["", "✅ 与基线一致，未检测到变更。"]

    lines += render_watch(watch_now, watch_base, False)

    report = "\n".join(lines)
    print(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)


if __name__ == "__main__":
    main()
