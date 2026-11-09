# Swell

A simple scanner that shows which US stocks are moving a lot: at least a dollar amount you choose
($5 by default), up or down, today or on a typical day. It shows movement only. It does not tell you
what to buy or sell.

## How it works
- A GitHub Action runs every 30 minutes on weekdays during US market hours, downloads prices for the
  tickers in `tickers.txt` (Yahoo Finance via yfinance, can be delayed) and saves `data/quotes.json`.
- `index.html` reads that file and lets you filter, sort and star stocks. Your stars and settings stay
  in your own browser.

## Setup (about 10 minutes)
1. Create a new GitHub repository (for example `swell`).
2. Add the files keeping this structure. For the hidden folder use Add file > Create new file and type the full path:
   - `index.html`
   - `tickers.txt`
   - `data/quotes.json`
   - `scripts/fetch_quotes.py`
   - `.github/workflows/quotes.yml`
3. Settings > Pages > Deploy from a branch > `main` / root.
4. Settings > Actions > General > Workflow permissions > **Read and write permissions** > Save.
5. Actions tab > **Update quotes** > Run workflow. Wait about 2 minutes.
6. Open your Pages URL on the iPhone and use Share > Add to Home Screen.

## Customize
- Edit `tickers.txt` on GitHub to add or remove stocks (one symbol per line).
- Change the schedule in `.github/workflows/quotes.yml` (the `cron` line).

## Good to know
- If the repository is public, your ticker list is public. Your stars are not stored there.
- Yahoo can block or throttle requests from GitHub's servers now and then. When that happens the app
  keeps the previous data and shows a warning.
- GitHub can delay scheduled runs, and it may pause scheduled workflows in repositories with no activity for 60 days.
- A $5 move means very different things: 25% on a $20 stock, about 1% on a $500 stock. Each row shows both.
