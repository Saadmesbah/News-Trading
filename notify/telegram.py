# notify/telegram.py
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str) -> bool:
    """Send a plain text message to your Telegram chat."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured — skipping notification.")
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id":    TELEGRAM_CHAT_ID,
                "text":       text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        response.raise_for_status()
        print("✅ Telegram notification sent.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram error: {e}")
        return False


def send_signal(score: dict, risk: dict):
    """
    Send a formatted trading signal to your phone.
    Looks like this on Telegram:

    ⚡ TRADING SIGNAL — BTCUSDT
    ───────────────────────────
    🟢 Signal     : BUY
    💰 Price      : $103,450.00
    🎯 Target     : $107,588.00 (+4.0%)
    🛑 Stop Loss  : $101,200.00 (-2.18%)
    📦 Size       : 0.00889 BTC ($919.43)
    ⚖️ Risk/Reward : 1:1.84
    ───────────────────────────
    📊 P Score    : +0.178 (LOW)
    📈 RSI        : 42.5
    🟢 Support    : $101,200.00
    🔴 Resistance : $105,800.00
    ───────────────────────────
    💬 "Strong ETF inflows offset by geopolitical tensions."
    """
    signal = score.get("signal", "HOLD")

    if signal == "HOLD":
        icon = "🟡"
    elif signal == "BUY":
        icon = "🟢"
    else:
        icon = "🔴"

    # Build message
    lines = [
        f"<b>⚡ TRADING SIGNAL — BTCUSDT</b>",
        f"───────────────────────────",
        f"{icon} <b>Signal</b>     : {signal}",
        f"💰 <b>Price</b>      : ${score.get('current_price', 0):,.2f}",
    ]

    if signal != "HOLD":
        lines += [
            f"🎯 <b>Target</b>     : ${risk.get('take_profit', 0):,.2f} (+{risk.get('take_profit_pct', 0)}%)",
            f"🛑 <b>Stop Loss</b>  : ${risk.get('stop_loss', 0):,.2f} (-{risk.get('stop_loss_pct', 0)}%)",
            f"📦 <b>Size</b>       : {risk.get('position_size_btc', 0)} BTC (${risk.get('position_value_usd', 0):,.2f})",
            f"⚖️ <b>Risk/Reward</b> : 1:{risk.get('risk_reward_ratio', 0)}",
        ]

    lines += [
        f"───────────────────────────",
        f"📊 <b>P Score</b>    : {score.get('p_score', 0):+.4f} ({score.get('confidence_label', '')})",
        f"📈 <b>RSI</b>        : {score.get('rsi', 0)}",
        f"🟢 <b>Support</b>    : ${score.get('support', 0):,.2f}",
        f"🔴 <b>Resistance</b> : ${score.get('resistance', 0):,.2f}",
        f"───────────────────────────",
        f"💬 <i>\"{score.get('rationale', '')}\"</i>",
    ]

    message = "\n".join(lines)
    return send_message(message)


def send_trade_opened(risk: dict):
    """Notify when a paper trade is opened."""
    icon = "🟢" if risk["signal"] == "BUY" else "🔴"
    msg = (
        f"<b>📥 TRADE OPENED</b>\n"
        f"───────────────────────────\n"
        f"{icon} {risk['signal']} @ ${risk['entry_price']:,.2f}\n"
        f"🛑 Stop Loss  : ${risk['stop_loss']:,.2f}\n"
        f"🎯 Take Profit: ${risk['take_profit']:,.2f}\n"
        f"📦 Size       : {risk['position_size_btc']} BTC\n"
        f"❌ Max Loss   : ${risk['potential_loss_usd']:,.2f}\n"
        f"✅ Max Profit : ${risk['potential_profit_usd']:,.2f}"
    )
    return send_message(msg)


def send_trade_closed(trade_id: int, exit_price: float, pnl_usd: float, pnl_pct: float, reason: str):
    """Notify when a paper trade is closed."""
    icon = "✅" if pnl_usd > 0 else "❌"
    msg = (
        f"<b>📤 TRADE CLOSED #{trade_id}</b>\n"
        f"───────────────────────────\n"
        f"Exit Price : ${exit_price:,.2f}\n"
        f"Reason     : {reason}\n"
        f"{icon} P&L : ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)"
    )
    return send_message(msg)


# ── Test ──────────────────────────────────────────────────

if __name__ == "__main__":
    fake_score = {
        "signal": "BUY", "current_price": 103450.0,
        "p_score": 0.178, "confidence_label": "LOW",
        "rsi": 42.5, "support": 101200.0, "resistance": 105800.0,
        "rationale": "Strong ETF inflows offset by geopolitical tensions."
    }
    fake_risk = {
        "signal": "BUY", "entry_price": 103450.0,
        "stop_loss": 101200.0, "take_profit": 107588.0,
        "stop_loss_pct": 2.18, "take_profit_pct": 4.0,
        "position_size_btc": 0.00889, "position_value_usd": 919.43,
        "potential_loss_usd": 20.0, "potential_profit_usd": 36.79,
        "risk_reward_ratio": 1.84,
    }

    send_signal(fake_score, fake_risk)