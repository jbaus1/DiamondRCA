"""Matplotlib plotting helpers."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_rolling_metric(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Rolling Metric",
):
    """Plot a line chart for a rolling metric."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df[x_col], df[y_col], label=y_col)
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig, ax


def plot_before_after_comparison(
    before_value: float,
    after_value: float,
    labels: tuple[str, str] = ("Before", "After"),
    title: str = "Before vs After",
):
    """Plot a bar comparison of a metric before and after a collapse window."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([labels[0], labels[1]], [before_value, after_value])
    ax.set_title(title)
    ax.set_ylabel("Value")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig, ax
