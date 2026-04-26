from services.data_fetcher import get_market_data
from services.scoring import score_stocks
from services.cache import set_cache
from models.db import SessionLocal, StockSnapshot

def update_market_data():
    stocks = get_market_data()
    scored = score_stocks(stocks)

    # cache
    set_cache(scored)

    # store in DB
    db = SessionLocal()

    for s in scored:
        db.merge(StockSnapshot(
            symbol=s["symbol"],
            price=s["price"],
            change=s["change"],
            score=s["score"]
        ))

    db.commit()
    db.close()