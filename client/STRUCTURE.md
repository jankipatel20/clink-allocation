# Project Structure Overview

## New Folder Organization

```
client/
├── main.py                    # Entry point (56 lines instead of 800+)
├── config.py                  # Configuration & setup
├── styles.css                 # All CSS styling
├── components/
│   ├── __init__.py
│   ├── navbar.py              # Navigation bar component
│   ├── kpi_cards.py           # KPI cards display
│   ├── file_uploader.py       # File upload & optimization button
│   └── footer.py              # Footer section
├── pages/
│   ├── __init__.py
│   ├── overview.py            # Overview tab (Cost & Heatmap)
│   ├── network_flow.py        # Network Flow tab (Sankey & Table)
│   ├── inventory.py           # Inventory tab (Line chart)
│   └── scenarios.py           # Scenarios tab (What-if analysis)
├── mock_data/                 # Test data files
└── requirements.txt           # Dependencies
```
