"""Visualization helpers for MindPulse exploratory analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    plt = None
    sns = None


def save_correlation_matrix(df: pd.DataFrame, output_path: Path) -> None:
    """Save a correlation heatmap for numeric fields."""
    if plt is None or sns is None:
        return
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 8))
    sns.heatmap(numeric.corr(numeric_only=True), cmap="viridis", center=0)
    plt.title("MindPulse Numeric Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_risk_distribution(df: pd.DataFrame, output_path: Path) -> None:
    """Save the risk-segment distribution chart."""
    if plt is None or sns is None:
        return
    if "risk_segment" not in df.columns:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    order = ["Lower", "Moderate", "Elevated"]
    sns.countplot(data=df, x="risk_segment", hue="risk_segment", order=order, palette="mako", legend=False)
    plt.title("Estimated Burnout Risk Segment Distribution")
    plt.xlabel("Risk Segment")
    plt.ylabel("Observation Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
