import pandas as pd
import numpy as np


def equity_curve(trades: pd.DataFrame, initial_balance: float) -> pd.Series:
    if trades.empty:
        return pd.Series([initial_balance])

    balances = trades["balance_after"].astype(float).tolist()
    return pd.Series([initial_balance] + balances)


def max_drawdown(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0

    roll_max = equity.cummax()
    dd = (equity - roll_max) / roll_max
    return dd.min()


def winrate(trades: pd.DataFrame) -> float:
    if trades.empty:
        return 0.0

    wins = (trades["pnl"] > 0).sum()
    return wins / len(trades)


def expectancy(trades: pd.DataFrame) -> float:
    if trades.empty:
        return 0.0

    return trades["pnl"].mean()


def profit_factor(trades: pd.DataFrame) -> float:
    if trades.empty:
        return 0.0

    gross_profit = trades.loc[trades["pnl"] > 0, "pnl"].sum()
    gross_loss = -trades.loc[trades["pnl"] < 0, "pnl"].sum()

    if gross_loss == 0:
        return np.inf

    return gross_profit / gross_loss


def summary_metrics(trades: pd.DataFrame, initial_balance: float) -> dict:
    eq = equity_curve(trades, initial_balance)
    dd = max_drawdown(eq)

    final_balance = eq.iloc[-1]
    total_return = (final_balance - initial_balance) / initial_balance

    return {
        "final_balance": float(final_balance),
        "total_return": float(total_return),
        "max_drawdown": float(dd),
        "winrate": float(winrate(trades)),
        "expectancy": float(expectancy(trades)),
        "profit_factor": float(profit_factor(trades)),
        "num_trades": int(len(trades)),
    }
