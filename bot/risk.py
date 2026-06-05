# bot/risk.py
from config import CAPITAL, RISK_PER_TRADE, STOP_LOSS_PCT, TAKE_PROFIT_PCT


def calculate_risk(signal: str, current_price: float, support: float, resistance: float) -> dict:
    """
    Calculates position sizing and risk levels for a given signal.

    Money Management Rules:
    ┌─────────────────────────────────────────────────────┐
    │  Risk per trade  = 2% of total capital              │
    │  Stop-loss       = 2% below entry (BUY)             │
    │                    2% above entry (SELL)            │
    │  Take-profit     = 4% above entry (BUY)  → 2:1 RR  │
    │                    4% below entry (SELL) → 2:1 RR  │
    │  Position size   = Risk amount / Stop distance      │
    └─────────────────────────────────────────────────────┘

    Risk/Reward ratio = 2:1 → for every $1 risked, target $2 profit.
    This means you only need to win 34% of trades to be profitable.
    """

    if signal == "HOLD" or current_price <= 0:
        return _no_trade(current_price)

    entry_price = current_price

    if signal == "BUY":
        # Use support as natural stop-loss if it's close enough
        natural_stop = support
        natural_stop_pct = (entry_price - natural_stop) / entry_price

        # Use natural support if it's within 3%, otherwise use fixed %
        if 0 < natural_stop_pct <= 0.03:
            stop_loss = round(natural_stop, 2)
            stop_pct  = round(natural_stop_pct, 4)
        else:
            stop_loss = round(entry_price * (1 - STOP_LOSS_PCT), 2)
            stop_pct  = STOP_LOSS_PCT

        take_profit = round(entry_price * (1 + TAKE_PROFIT_PCT), 2)
        take_pct    = TAKE_PROFIT_PCT

    elif signal == "SELL":
        # Use resistance as natural stop-loss if close enough
        natural_stop = resistance
        natural_stop_pct = (natural_stop - entry_price) / entry_price

        if 0 < natural_stop_pct <= 0.03:
            stop_loss = round(natural_stop, 2)
            stop_pct  = round(natural_stop_pct, 4)
        else:
            stop_loss = round(entry_price * (1 + STOP_LOSS_PCT), 2)
            stop_pct  = STOP_LOSS_PCT

        take_profit = round(entry_price * (1 - TAKE_PROFIT_PCT), 2)
        take_pct    = TAKE_PROFIT_PCT

    # ── Position Sizing ───────────────────────────────────
    # How much USD to risk on this trade
    risk_amount = round(CAPITAL * RISK_PER_TRADE, 2)

    # Stop distance in USD
    stop_distance = abs(entry_price - stop_loss)

    # How many BTC units to buy/sell
    if stop_distance > 0:
        position_size_btc = round(risk_amount / stop_distance, 6)
    else:
        position_size_btc = 0.0

    # Total position value in USD
    position_value_usd = round(position_size_btc * entry_price, 2)

    # Potential profit and loss
    potential_profit = round(abs(take_profit - entry_price) * position_size_btc, 2)
    potential_loss   = round(risk_amount, 2)
    risk_reward      = round(potential_profit / potential_loss, 2) if potential_loss > 0 else 0

    return {
        "signal":              signal,
        "entry_price":         entry_price,
        "stop_loss":           stop_loss,
        "take_profit":         take_profit,
        "stop_loss_pct":       round(stop_pct * 100, 2),
        "take_profit_pct":     round(take_pct * 100, 2),
        "risk_amount_usd":     risk_amount,
        "position_size_btc":   position_size_btc,
        "position_value_usd":  position_value_usd,
        "potential_profit_usd": potential_profit,
        "potential_loss_usd":   potential_loss,
        "risk_reward_ratio":   risk_reward,
        "capital":             CAPITAL,
    }


def _no_trade(current_price: float) -> dict:
    return {
        "signal":              "HOLD",
        "entry_price":         current_price,
        "stop_loss":           None,
        "take_profit":         None,
        "stop_loss_pct":       None,
        "take_profit_pct":     None,
        "risk_amount_usd":     0.0,
        "position_size_btc":   0.0,
        "position_value_usd":  0.0,
        "potential_profit_usd": 0.0,
        "potential_loss_usd":   0.0,
        "risk_reward_ratio":   0.0,
        "capital":             CAPITAL,
    }


def print_risk_report(risk: dict):
    """Pretty print the risk management report."""

    if risk["signal"] == "HOLD":
        print("\n🟡 HOLD — No trade. No risk calculated.\n")
        return

    icon = "🟢" if risk["signal"] == "BUY" else "🔴"

    print("\n" + "─"*45)
    print("       RISK MANAGEMENT")
    print("─"*45)
    print(f"  {icon} Signal       : {risk['signal']}")
    print(f"  💰 Capital       : ${risk['capital']:,.2f}")
    print(f"  📥 Entry Price   : ${risk['entry_price']:,.2f}")
    print(f"  🛑 Stop Loss     : ${risk['stop_loss']:,.2f}  (-{risk['stop_loss_pct']}%)")
    print(f"  🎯 Take Profit   : ${risk['take_profit']:,.2f}  (+{risk['take_profit_pct']}%)")
    print(f"  📦 Position Size : {risk['position_size_btc']} BTC")
    print(f"  💵 Position Val  : ${risk['position_value_usd']:,.2f}")
    print(f"  ❌ Max Loss      : ${risk['potential_loss_usd']:,.2f}")
    print(f"  ✅ Target Profit : ${risk['potential_profit_usd']:,.2f}")
    print(f"  ⚖️  Risk/Reward   : 1:{risk['risk_reward_ratio']}")
    print("─"*45 + "\n")


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test BUY signal
    print("TEST 1 — BUY signal")
    risk_buy = calculate_risk(
        signal="BUY",
        current_price=103450.0,
        support=101200.0,
        resistance=105800.0
    )
    print_risk_report(risk_buy)

    # Test SELL signal
    print("TEST 2 — SELL signal")
    risk_sell = calculate_risk(
        signal="SELL",
        current_price=103450.0,
        support=101200.0,
        resistance=105800.0
    )
    print_risk_report(risk_sell)

    # Test HOLD signal
    print("TEST 3 — HOLD signal")
    risk_hold = calculate_risk(
        signal="HOLD",
        current_price=103450.0,
        support=101200.0,
        resistance=105800.0
    )
    print_risk_report(risk_hold)