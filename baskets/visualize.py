# basckets/visualize.py

import matplotlib.pyplot as plt
import pandas as pd

from backtest.metrics import equity_curve, max_drawdown


def plot_equity_curve(
    trades: pd.DataFrame,
    initial_balance: float,
    title: str = "Equity Curve"
):
    """
    Малює equity curve на основі результатів Backtester.
    Працює з новою архітектурою:
    - trades: DataFrame з колонками ['balance_after']
    - initial_balance: стартовий баланс
    """

    if trades is None or trades.empty:
        print("No trades to plot")
        return

    # Побудова equity curve
    eq = equity_curve(trades, initial_balance)
    dd = max_drawdown(eq)

    plt.figure(figsize=(12, 6))
    plt.plot(eq, label="Equity")
    plt.title(f"{title} | Max DD: {dd:.2%}")
    plt.xlabel("Trades")
    plt.ylabel("Balance")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
