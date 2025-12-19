# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese financial market monitoring tool that fetches real-time data for:
- Fund valuations (基金估值)
- Market indices (上证指数, 深证指数, 创业板指, etc.)
- Gold prices (黄金价格)
- Sector/industry performance (行业板块)
- Market news and alerts (7×24 快讯)

The tool supports both CLI and web server modes.

## Core Commands

### Development & Running

**View fund information (CLI mode):**
```bash
python fund.py
```

**Add funds to watchlist:**
```bash
python fund.py -a
# Then input fund codes separated by commas
```

**Delete funds from watchlist:**
```bash
python fund.py -d
# Then input fund codes separated by commas
```

**Mark funds as held:**
```bash
python fund.py -c
# Then input fund codes to mark with ⭐
```

**Unmark held funds:**
```bash
python fund.py -b
# Then input fund codes to unmark
```

**Start web server:**
```bash
python fund_server.py
# Server runs on http://0.0.0.0:8311
# Access via: http://localhost:8311/fund
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Architecture

### Data Flow

The application follows a three-layer architecture:

1. **Data Layer** (`fund.py` - `MaYiFund` class)
   - Fetches data from external APIs (fund123.cn, Baidu Finance, Eastmoney)
   - Manages fund code cache in `cache/fund_map.json`
   - Uses threading with semaphore (limit: 5) for concurrent API calls
   - Handles CSRF token management and session persistence

2. **Presentation Layer**
   - CLI: Uses `tabulate` for terminal output with ANSI color codes
   - Web: `module_html.py` generates HTML tables with sortable columns
   - `fund_server.py` uses Flask to serve web interface

3. **Cache Layer**
   - `cache/fund_map.json` stores fund codes with structure:
     ```json
     {
       "fund_code": {
         "fund_key": "internal_id",
         "fund_name": "fund_name",
         "is_hold": false
       }
     }
     ```

### Key Design Patterns

**Threading for Performance:**
- Fund data queries run in parallel threads (max 5 concurrent via semaphore)
- Web server uses separate threads for each data section (market, gold, funds, sectors)

**Session Management:**
- Maintains two separate sessions:
  - `session`: for fund123.cn API calls with CSRF protection
  - `baidu_session`: for Baidu Finance API with BDUSS cookies

**Data Formatting:**
- CLI: ANSI color codes (`\033[1;31m` = red for gains, `\033[1;32m` = green for losses)
- Web: HTML tables with client-side JavaScript sorting
- Both modes calculate: daily growth, 30-day trends, consecutive gains/losses

### File Responsibilities

**fund.py** (main data engine):
- `MaYiFund.init()`: Initializes sessions and fetches CSRF tokens
- `MaYiFund.add_code()` / `delete_code()`: Manage watchlist
- `MaYiFund.search_one_code()`: Fetches individual fund data (threaded)
- `MaYiFund.search_code()`: Orchestrates parallel fund queries
- `MaYiFund.bk()`: Industry sector data
- `MaYiFund.gold()` / `real_time_gold()`: Gold price data
- `MaYiFund.get_market_info()`: Market indices
- `MaYiFund.A()` / `seven_A()`: Shanghai index minute-by-minute and 7-day volume
- Methods ending in `_html()`: Return HTML strings for web interface

**fund_server.py** (web server):
- Single route: `/fund` (GET)
- Query params: `?add=code1,code2` or `?delete=code1,code2`
- Returns full HTML page with all data sections
- Uses `importlib.reload(fund)` to ensure fresh data

**module_html.py** (HTML generation):
- `get_table_html()`: Generates sortable HTML tables
- `get_full_page_html()`: Combines tables with CSS/JS
- `get_css_style()`: Table styling with white background, blue accents
- `get_javascript_code()`: Client-side table sorting logic

### API Endpoints Used

**fund123.cn:**
- `/api/fund/searchFund` - Search and add funds
- `/matiaria?fundCode=XXX` - Get fund growth data
- `/api/fund/queryFundQuotationCurves` - 30-day trend data
- `/api/fund/queryFundEstimateIntraday` - Real-time valuation

**Baidu Finance:**
- `/api/getbanner` - Market indices (Asia, America)
- `/vapi/v1/getquotation` - Specific index data
- `/selfselect/expressnews` - Market news alerts
- `/sapi/v1/metrictrend` - 7-day trading volume

**Other:**
- `api.jijinhao.com` - Gold prices (China Gold, Chow Tai Fook)
- `push2.eastmoney.com` - Sector/industry data

### Data Processing Notes

**30-Day Trend Calculation:**
- Fetches ONE_MONTH data points from fund quotation curves
- Compares sequential rates to determine up/down days
- Calculates consecutive gain/loss streaks from most recent day
- Color codes based on positive/negative growth

**Time Handling:**
- All timestamps converted to Beijing time
- Real-time data updates use current timestamp in milliseconds
- Date formats: `%Y-%m-%d` for dates, `%H:%M:%S` for times

**SSL/TLS Configuration:**
- Disables warnings via `urllib3.disable_warnings()`
- Custom cipher suite for compatibility with Chinese finance APIs
- All requests use `verify=False` to bypass certificate validation

## Important Files

- `cache/fund_map.json` - User's fund watchlist (GBK encoding)
- `dist/fund.exe` - Compiled Windows executable
- `requirements.txt` - Python dependencies

## Character Encoding

- Cache files use **GBK encoding** (Chinese character support)
- Source files use **UTF-8** with BOM marker
- Terminal output uses ANSI escape codes for colors
