# BTC signal research

The published sample contains 192 observations from September 24 to October 31, 2026. Three disconnected June observations are excluded. All notebooks contain executed outputs, and all price/score inputs needed by the published studies are frozen locally. No credentials, bot imports or API calls are required.

## Study guide

| Notebook | Question |
|---|---|
| [Original recent-only research](trading_strategy_research_recent.ipynb) | Data quality, BTC/score charts, forward correlations, separate P/news/TA threshold/holding-period comparisons, and 21 news/technical mixes. |
| [News categories](category_research/news_category_analysis.ipynb) | How do Bitcoin, crypto, politics and war/macro scores relate to subsequent 1/4/12/24-hour BTC returns? |
| [Six category formulas](category_research/news_category_weight_comparison.ipynb) | How do original, equal, Bitcoin-only, crypto-only and two 80%-heavy formulas compare under 70/30 news/TA and a 24-hour hold? |
| [Three-period consistency](category_research/sequential_stability_analysis.ipynb) | Do eight previously explored candidates behave consistently over three sequential evaluations with thresholds chosen only from preceding data? |

## Key distinctions

Category weights create the news score. News/technical weights create the final P-score. Neither set of weights has been established as optimal.

In the original and six-category comparisons, earlier means the first 134 observations and later means the final 58. For the sequential study, training grows from 96 to 124 to 153 observations; evaluation uses the next 28, 29 and 39 observations. Thresholds are selected using training net return, with at least ten completed training trades, and then fixed for the corresponding evaluation. Each candidate selects its own threshold.

The latest trading studies hold positions 24 hours, use next-hour-open entry, charge 0.10% fee and 0.05% slippage each side, and prohibit overlapping positions. Each segment starts at $1,000; trades crossing endpoints are excluded. Long/short is unleveraged and excludes borrowing, funding, margin and liquidation. The original study also includes other holding periods; distinguish those results from the fixed 24-hour follow-ups.

Category correlations were weak. Equal category weights at 70/30 were positive in all three long/short sequential evaluations, but made only 5, 1 and 4 trades. A single-trade evaluation cannot establish robustness. No reliable live-trading edge has been established. Historical buying-only outputs remain for completeness; future research focuses on long/short.

## Inputs, outputs and provenance

- `recent_data/`: original frozen recent signals, hourly Binance BTCUSDT prices and their hash manifest.
- `category_research/audit_results/azure_matching_previous_192.csv`: the matching 192 Azure signal records, including the four category scores. Shared scores, price and labels reconcile to the previous CSV; Azure timestamps retain microseconds while the earlier CSV truncates to milliseconds.
- `results_recent/`: original study charts, grids, ledgers and checks.
- The three result folders inside `category_research/`: category charts/tables, six-formula ledgers, sequential splits/selections/ledgers and verification results. The notebooks regenerate these files.

The Azure retrieval also yielded 40 newer observations. Only their existence and reservation are documented here; their raw records are excluded and no strategy outcomes have been evaluated on them. The credential-containing source notebook is excluded. The earlier full-history notebook remains local; the published research focuses on the recent sample.

## Reproduce offline

Use Python 3.14 to match the recorded environment. From the repository root:

```bash
python -m venv .venv-research
# Activate the environment, then:
python -m pip install -r notebooks/requirements.txt
python -m ipykernel install --user --name trading-research
```

Open a notebook in VS Code or Jupyter and select the environment. Run the original notebook from the repository root or notebooks folder. Run the category notebooks from the repository root or their containing category_research folder. Install Jupyter's interface separately if needed. Source hashes are verified before calculation. Keep the directory structure intact.

## Limits

There are five score-collection gaps longer than 12 hours, missing observations are not invented, and incomplete final horizons are excluded. Returns overlap in the descriptive studies and observations are dependent. Candidate definitions and the evaluation periods have already been explored, so the results are exploratory rather than untouched validation. Costs are modeled assumptions, not observed fills. No significance or causal claim is made. Fixed-hold simulations do not validate production risk controls.
