# PLP Data Analytics Assignment 3: Duka Sales & Agent Cleanup

Two analytics engagements for a Nairobi consultancy, delivered in one repository.

## Summary of the engagements

### Engagement 1 · Duka Electronics (sales exploration)
Half-year (January–June 2026) review of 1,000 orders for the Head of Sales. The notebook inspects the data,
creates derived columns (`revenue`, `month`, `weekday`, `is_weekend`, `price_band`), and answers questions on
branch ranking, top products, weekend vs weekday orders, best and worst month, and Premium online orders
from Nairobi and Mombasa. A spreadsheet (SUMIFS, XLOOKUP, PivotTable) reproduces the branch revenue ranking,
and the notebook confirms its totals match pandas.

### Engagement 2 · Mobile money agent network (data cleaning)
Audit, clean, merge and summarise an unreliable transaction extract from five counties. The cleaning rules live in
`cleaning_pipeline.py` as `clean_agent_data(txns, agents)`, which returns the clean DataFrame and a cleaning log.
The notebook contains the data-quality audit, post-merge validation, county summary, weekly pivot table and a
Data Quality Report organised by six dimensions, including a privacy paragraph under the Kenya Data Protection Act 2019.

## Repository structure

```
├── README.md
├── requirements.txt
├── generate_data.py                  # both dataset generators (Duka seed 2026, agents seed 44)
├── cleaning_pipeline.py              # clean_agent_data(txns, agents) -> (clean_df, log)
├── duka_sales_exploration.ipynb      # Engagement 1
├── agent_cleanup.ipynb               # Engagement 2
├── excel/
│   └── duka_branch_summary.xlsx      # SUMIFS, XLOOKUP, PivotTable
└── outputs/
    ├── premium_online_coast_capital.csv
    └── agent_transactions_clean.csv
```

Raw generated CSVs (`duka_sales.csv`, `agents.csv`, `agent_transactions.csv`) are not committed; they are regenerated.

## How to regenerate the data and run the notebooks

1. Install the requirements: `pip install -r requirements.txt`
2. Generate all three raw CSVs: `python generate_data.py`
   - Creates `duka_sales.csv` (seed 2026), `agents.csv` and `agent_transactions.csv` (seed 44).
3. Open a notebook and use **Restart and run all** (Google Colab: **Runtime → Restart session and run all**).
   - `duka_sales_exploration.ipynb` reads `duka_sales.csv` and writes `outputs/premium_online_coast_capital.csv`.
   - `agent_cleanup.ipynb` imports `cleaning_pipeline.py`, reads the two agent CSVs and writes `outputs/agent_transactions_clean.csv`.

**In Google Colab**, run this first in a cell, then continue with the notebook:
```python
!git clone https://github.com/mangacindy9-code/plp-da-a3-duka-sales-and-agent-cleanup.git
%cd plp-da-a3-duka-sales-and-agent-cleanup
!python generate_data.py
```

## Duka Executive Summary

- **Branches:** Nairobi leads with KES 26.1M (36.4% of revenue), nearly three times the lowest branch, Eldoret, at KES 8.8M (12.3%).
- **Products:** Laptops earn KES 41.5M (57.9% of revenue), 2.1x the runner-up Tablet, so laptop stock and pricing drive the half-year result.
- **Channels:** Phone orders have the highest average value (KES 79,576) but only 101 orders versus 579 in-store, so they are valuable but small.
- **Timing:** April 2026 was the best month (KES 13.5M), 24.0% above the worst month, June 2026 (KES 10.9M).
- **Premium online:** 83 Premium online
