#!/usr/bin/env python3
"""
MemeRadar - Solana memecoin launch radar.
Watches new pump.fun launches, scores them on early signals,
and flags the ones worth a second look.

Usage:
    python memeradar.py [--min-score 60] [--min-mcap 10000] [--poll 15]
"""
import argparse
import json
import time
import urllib.request

DEXSCREENER_NEW_PAIRS = "https://api.dexscreener.com/token-profiles/latest/v1"
PUMP_FUN_API = "https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false"


def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "MemeRadar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def score_token(t):
    """Score a fresh token 0-100 based on early signals. Starts at 50."""
    score, reasons = 50, []
    mcap = t.get("market_cap", 0) or 0
    buys = t.get("buys", 0) or 0
    sells = t.get("sells", 0) or 0
    holders = t.get("holders", 0) or 0
    volume = t.get("volume_5m", 0) or 0
    dev_pct = t.get("dev_holding_pct", 0) or 0
    has_social = bool(t.get("twitter") or t.get("telegram") or t.get("website"))
    mint_revoked = bool(t.get("mint_revoked"))

    if buys > sells:
        score += 15; reasons.append("buys>sells")
    elif sells > buys:
        score -= 15; reasons.append("sell pressure")
    if holders >= 50:
        score += 10; reasons.append("holders growing")
    if has_social:
        score += 10; reasons.append("has socials")
    else:
        score -= 15; reasons.append("no socials")
    if 0 < dev_pct < 10:
        score += 10; reasons.append("dev holds <10%")
    elif dev_pct >= 30:
        score -= 25; reasons.append("dev holds 30%+")
    if volume > 5000:
        score += 10; reasons.append("vol >$5k/5m")
    if mint_revoked:
        score += 5; reasons.append("mint revoked")
    if mcap >= 50000:
        score += 5; reasons.append("mcap >$50k")
    return max(0, min(100, score)), reasons


def flag(score):
    if score >= 80:
        return "HOT"
    if score >= 60:
        return "WATCH"
    return "skip"


def scan_once(min_score, min_mcap):
    try:
        coins = fetch_json(PUMP_FUN_API)
    except Exception as e:
        print(f"[!] pump.fun API error: {e}")
        return
    for c in coins if isinstance(coins, list) else []:
        t = {
            "mint": c.get("mint"),
            "name": c.get("name"),
            "symbol": c.get("symbol"),
            "market_cap": c.get("usd_market_cap", 0),
            "buys": 0, "sells": 0, "holders": 0, "volume_5m": 0,
            "dev_holding_pct": 0,
            "twitter": c.get("twitter"),
            "telegram": c.get("telegram"),
            "website": c.get("website"),
            "mint_revoked": False,
        }
        if (t["market_cap"] or 0) < min_mcap:
            continue
        s, reasons = score_token(t)
        f = flag(s)
        if s >= min_score:
            print(f"[{f}] {t['symbol']} ({t['name']}) score={s} "
                  f"mcap=${t['market_cap']:,.0f} | {', '.join(reasons)} | "
                  f"https://pump.fun/coin/{t['mint']}")


def main():
    p = argparse.ArgumentParser(description="MemeRadar - Solana memecoin launch radar")
    p.add_argument("--min-score", type=int, default=60)
    p.add_argument("--min-mcap", type=float, default=10000)
    p.add_argument("--poll", type=int, default=15, help="seconds between scans (0 = once)")
    a = p.parse_args()
    print(f"MemeRadar started — min_score={a.min_score} min_mcap=${a.min_mcap:,.0f}")
    while True:
        scan_once(a.min_score, a.min_mcap)
        if a.poll <= 0:
            break
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
