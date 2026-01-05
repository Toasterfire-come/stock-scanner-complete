# Understanding Sharpe Ratio: A Beginner’s Guide

Sharpe ratio is one of the most common “quality” metrics in finance.

## What Sharpe ratio tries to measure

Sharpe answers:

> “How much return did I earn per unit of volatility (risk)?”

In plain terms: **smooth, consistent returns** get rewarded.

## Why Sharpe can mislead you

Sharpe treats upside and downside volatility as equally “bad.”

That’s not always what you want. A strategy that trends upward with volatility can still be great — Sharpe may punish it.

## When to prefer Sortino

Sortino looks only at **downside volatility**.

If you care about “how painful are the bad swings,” Sortino is often more intuitive.

## When to prefer Calmar

Calmar compares returns to **max drawdown**.

If you want a “survivability” metric, Calmar can be more directly tied to risk tolerance.

## Practical thresholds (rough guidance)

- Sharpe < 0.5: weak / noisy
- 0.5–1.0: modest edge (watch costs)
- 1.0–2.0: strong
- > 2.0: excellent (validate robustness)

## The right way to use Sharpe

Use Sharpe to **compare** strategies that:

- Use similar assets
- Use similar timeframes
- Have similar exposure and leverage

Then validate with drawdown and tail risk.

