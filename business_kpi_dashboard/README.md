# 📊 Business KPI Dashboard

An interactive **Streamlit + Plotly** dashboard for tracking core business KPIs:
Revenue, Profit, Customer Growth, Monthly Trends, and Customer Feedback Sentiment
(powered by **TextBlob**).

---

## 📁 Project Structure

```
business_kpi_dashboard/
│
├── app.py                     # Main Streamlit application
├── generate_sample_data.py    # Script to generate sample sales data
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── data/
    └── sales_data.csv         # Sample dataset (auto-generated)
```

---

## ⚙️ Setup & Execution Steps (VS Code)

### 1. Extract the project
Unzip the downloaded folder and open it in **VS Code**:
```
File → Open Folder → business_kpi_dashboard
```

### 2. Open the VS Code integrated terminal
```
Terminal → New Terminal
```

### 3. (Recommended) Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. (First time only) Generate sample data
A sample dataset is already included in `data/sales_data.csv`. If you want to
regenerate it (or replace it with your own logic), run:
```bash
python generate_sample_data.py
```

> 💡 To use your **own real data**, replace `data/sales_data.csv` with your file,
> keeping the same columns: `Date, CustomerID, Region, Product, Quantity, Revenue, Cost, Profit, Feedback`

### 6. Run the Streamlit app
```bash
streamlit run app.py
```

### 7. View in browser
Streamlit will automatically open your default browser at:
```
http://localhost:8501
```
If it doesn't open automatically, copy that URL into your browser manually.

---

## 🧩 Features

| Feature | Description |
|---|---|
| **Revenue KPI** | Total revenue with interactive filtering |
| **Profit KPI** | Total profit + profit margin % |
| **Customer Growth** | New customers/month, cumulative growth, active customers |
| **Monthly Trends** | Revenue & profit trend lines, order volume |
| **Interactive Filters** | Date range, Region, Product (sidebar) |
| **Plotly Charts** | Line, bar, pie, and area charts — all interactive (zoom, hover, pan) |
| **Sentiment Analysis (TextBlob)** | Classifies customer feedback as Positive / Neutral / Negative |
| **Data Export** | Download filtered data as CSV directly from the dashboard |

---

## 🛠 Troubleshooting

- **`streamlit: command not found`** → Make sure your virtual environment is
  activated and dependencies installed (`pip install -r requirements.txt`).
- **TextBlob corpora error** (rare, only needed for advanced NLP features) →
  run `python -m textblob.download_corpora` (not required for basic polarity scoring used here).
- **Port already in use** → run `streamlit run app.py --server.port 8502` to use a different port.

---

## 📌 Next Steps / Ideas to Extend
- Connect to a live database (PostgreSQL/MySQL) instead of CSV
- Add authentication (`streamlit-authenticator`)
- Deploy to **Streamlit Community Cloud**, **Render**, or **Azure/AWS**
- Add forecasting (Prophet / ARIMA) for revenue projections
