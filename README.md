# MemeRadar 📡

A Solana memecoin launch radar. MemeRadar watches new [pump.fun](https://pump.fun) token launches, scores them on early signals, and alerts you on the ones worth a second look.

## What it does

- **Tracks** new pump.fun launches in real time (via the pump.fun / DexScreener public APIs)
- **Scores** each token on early momentum: buy/sell ratio, holder growth, volume in the first minutes
- **Alerts** when a token crosses your thresholds (score, market cap, holder count)
- **Filters** out obvious rugs: no socials, dev holding too much supply, mint/freeze authority still on

## Quick start

```bash
pip install -r requirements.txt
python memeradar.py --min-score 60 --min-mcap 10000
```

## How scoring works

Each new token starts at 50 points. Points are added or removed:

| Signal | Points |
|---|---|
| Buys > sells in first 5 min | +15 |
| Holder count growing fast | +10 |
| Twitter / Telegram linked | +10 |
| Dev holds < 10% of supply | +10 |
| Volume > $5k in first 5 min | +10 |
| Mint authority revoked | +5 |
| Dev holds > 30% of supply | −25 |
| No socials at all | −15 |
| Sell pressure > buy pressure | −15 |

A token scoring **60+** gets flagged as `WATCH`. **80+** gets flagged as `HOT`.

## Config

Edit `config.json` to set your thresholds:

```json
{
  "min_score": 60,
  "min_mcap_usd": 10000,
  "poll_seconds": 15,
  "alert_webhook": ""
}
```

## Disclaimer

MemeRadar is a research tool, not financial advice. Memecoins are extremely volatile — most new launches go to zero. Always DYOR.

## License

MIT
