# storage/database.py
import sqlite3
import json
from datetime import datetime, timezone
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn


def create_tables():
    """
    Create all tables if they don't exist yet.
    Runs once at startup.
    """
    conn = get_connection()
    c = conn.cursor()

    # ── Signals table — one row per bot run ───────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp           TEXT NOT NULL,
            symbol              TEXT NOT NULL,

            -- Sentiment
            bitcoin_score       REAL,
            crypto_score        REAL,
            politics_score      REAL,
            war_macro_score     REAL,
            news_score          REAL,
            rationale           TEXT,

            -- Technical
            current_price       REAL,
            rsi                 REAL,
            support             REAL,
            resistance          REAL,
            ta_score            REAL,

            -- Final
            p_score             REAL,
            signal              TEXT,
            confidence          REAL,
            confidence_label    TEXT,

            -- Risk
            entry_price         REAL,
            stop_loss           REAL,
            take_profit         REAL,
            position_size_btc   REAL,
            position_value_usd  REAL,
            risk_amount_usd     REAL,
            risk_reward_ratio   REAL
        )
    """)

    # ── Paper trades table — track simulated trades ───────
    c.execute("""
        CREATE TABLE IF NOT EXISTS paper_trades (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            opened_at       TEXT NOT NULL,
            closed_at       TEXT,
            symbol          TEXT NOT NULL,
            signal          TEXT NOT NULL,
            entry_price     REAL NOT NULL,
            exit_price      REAL,
            stop_loss       REAL,
            take_profit     REAL,
            position_size   REAL,
            pnl_usd         REAL,
            pnl_pct         REAL,
            status          TEXT DEFAULT 'OPEN',
            close_reason    TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables ready.")


# ── Save signal ───────────────────────────────────────────

def save_signal(score: dict, risk: dict, symbol: str = "BTCUSDT"):
    """Save a full analysis result to the signals table."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO signals (
            timestamp, symbol,
            bitcoin_score, crypto_score, politics_score, war_macro_score,
            news_score, rationale,
            current_price, rsi, support, resistance, ta_score,
            p_score, signal, confidence, confidence_label,
            entry_price, stop_loss, take_profit,
            position_size_btc, position_value_usd,
            risk_amount_usd, risk_reward_ratio
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        symbol,
        score.get("bitcoin_score"),
        score.get("crypto_score"),
        score.get("politics_score"),
        score.get("war_macro_score"),
        score.get("news_score"),
        score.get("rationale"),
        score.get("current_price"),
        score.get("rsi"),
        score.get("support"),
        score.get("resistance"),
        score.get("ta_score"),
        score.get("p_score"),
        score.get("signal"),
        score.get("confidence"),
        score.get("confidence_label"),
        risk.get("entry_price"),
        risk.get("stop_loss"),
        risk.get("take_profit"),
        risk.get("position_size_btc"),
        risk.get("position_value_usd"),
        risk.get("risk_amount_usd"),
        risk.get("risk_reward_ratio"),
    ))

    conn.commit()
    signal_id = c.lastrowid
    conn.close()
    print(f"✅ Signal saved — ID: {signal_id}")
    return signal_id


# ── Paper Trading ─────────────────────────────────────────

def open_paper_trade(risk: dict, symbol: str = "BTCUSDT") -> int:
    """Open a new simulated trade."""
    if risk["signal"] == "HOLD":
        return -1

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO paper_trades (
            opened_at, symbol, signal, entry_price,
            stop_loss, take_profit, position_size, status
        ) VALUES (?,?,?,?,?,?,?,'OPEN')
    """, (
        datetime.now(timezone.utc).isoformat(),
        symbol,
        risk["signal"],
        risk["entry_price"],
        risk["stop_loss"],
        risk["take_profit"],
        risk["position_size_btc"],
    ))

    conn.commit()
    trade_id = c.lastrowid
    conn.close()
    print(f"✅ Paper trade opened — ID: {trade_id} | {risk['signal']} @ ${risk['entry_price']:,.2f}")
    return trade_id


def close_paper_trade(trade_id: int, exit_price: float, reason: str = "MANUAL"):
    """Close an open simulated trade and calculate P&L."""
    conn = get_connection()
    c = conn.cursor()

    # Get the trade
    trade = c.execute(
        "SELECT * FROM paper_trades WHERE id = ?", (trade_id,)
    ).fetchone()

    if not trade:
        print(f"❌ Trade ID {trade_id} not found.")
        conn.close()
        return

    entry_price   = trade["entry_price"]
    position_size = trade["position_size"]
    signal        = trade["signal"]

    # Calculate P&L
    if signal == "BUY":
        pnl_usd = round((exit_price - entry_price) * position_size, 2)
    else:  # SELL
        pnl_usd = round((entry_price - exit_price) * position_size, 2)

    pnl_pct = round((pnl_usd / (entry_price * position_size)) * 100, 2)

    c.execute("""
        UPDATE paper_trades
        SET closed_at=?, exit_price=?, pnl_usd=?, pnl_pct=?,
            status='CLOSED', close_reason=?
        WHERE id=?
    """, (
        datetime.now(timezone.utc).isoformat(),
        exit_price, pnl_usd, pnl_pct, reason, trade_id
    ))

    conn.commit()
    conn.close()
    print(f"✅ Trade {trade_id} closed @ ${exit_price:,.2f} | P&L: ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)")


# ── Read ──────────────────────────────────────────────────

def get_last_signals(limit: int = 10) -> list:
    """Get the most recent signals."""
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute(
        "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_open_trades() -> list:
    """Get all currently open paper trades."""
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute(
        "SELECT * FROM paper_trades WHERE status='OPEN'"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_trade_summary() -> dict:
    """Get overall paper trading performance."""
    conn = get_connection()
    c = conn.cursor()

    result = c.execute("""
        SELECT
            COUNT(*)                          as total_trades,
            SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl_usd < 0 THEN 1 ELSE 0 END) as losses,
            ROUND(SUM(pnl_usd), 2)            as total_pnl,
            ROUND(AVG(pnl_pct), 2)            as avg_pnl_pct
        FROM paper_trades
        WHERE status='CLOSED'
    """).fetchone()

    conn.close()

    total  = result["total_trades"] or 0
    wins   = result["wins"] or 0
    losses = result["losses"] or 0

    return {
        "total_trades": total,
        "wins":         wins,
        "losses":       losses,
        "win_rate":     round((wins / total * 100), 1) if total > 0 else 0,
        "total_pnl":    result["total_pnl"] or 0,
        "avg_pnl_pct":  result["avg_pnl_pct"] or 0,
    }


# ── Test ──────────────────────────────────────────────────

if __name__ == "__main__":
    create_tables()

    # Test save signal
    fake_score = {
        "bitcoin_score": 0.68, "crypto_score": 0.34,
        "politics_score": -0.18, "war_macro_score": -0.52,
        "news_score": 0.188, "rationale": "Test signal.",
        "current_price": 103450.0, "rsi": 42.5,
        "support": 101200.0, "resistance": 105800.0,
        "ta_score": 0.156, "p_score": 0.178,
        "signal": "BUY", "confidence": 0.178,
        "confidence_label": "LOW",
    }
    fake_risk = {
        "signal": "BUY", "entry_price": 103450.0,
        "stop_loss": 101200.0, "take_profit": 107588.0,
        "position_size_btc": 0.00889, "position_value_usd": 919.43,
        "risk_amount_usd": 20.0, "risk_reward_ratio": 1.84,
    }

    # Save signal
    save_signal(fake_score, fake_risk)

    # Open paper trade
    trade_id = open_paper_trade(fake_risk)

    # Close it with a fake exit price
    close_paper_trade(trade_id, exit_price=105000.0, reason="TAKE_PROFIT")

    # Print summary
    summary = get_trade_summary()
    print(f"\n📊 TRADE SUMMARY")
    print(f"  Total : {summary['total_trades']}")
    print(f"  Wins  : {summary['wins']}")
    print(f"  Losses: {summary['losses']}")
    print(f"  Win % : {summary['win_rate']}%")
    print(f"  P&L   : ${summary['total_pnl']:+.2f}")