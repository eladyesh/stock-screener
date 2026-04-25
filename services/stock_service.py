import yfinance as yf
import pandas as pd
import time


class StockService:

    @staticmethod
    def get_bulk_data(tickers: list[str], retries: int = 2) -> pd.DataFrame:
        tickers = [t.upper().replace("$", "").strip() for t in tickers]

        for attempt in range(retries):
            try:
                data = yf.download(
                    tickers=tickers,
                    period="2d",
                    group_by="ticker",
                    auto_adjust=True,
                    progress=False,
                    threads=True
                )
                print("data " + data)

                rows = []

                for ticker in tickers:
                    try:
                        df = data[ticker]

                        if df.empty or len(df) < 2:
                            continue

                        latest = df.iloc[-1]
                        prev = df.iloc[-2]

                        price = float(latest["Close"])
                        change_pct = ((price - prev["Close"]) / prev["Close"]) * 100

                        rows.append({
                            "ticker": ticker,
                            "price": price,
                            "change_percent": round(change_pct, 2),
                        })

                    except Exception as e:
                        print(e)


                return pd.DataFrame(rows)

            except Exception as e:
                print(e)
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return pd.DataFrame()