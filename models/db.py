from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class StockSnapshot(Base):
    __tablename__ = "stock_snapshots"

    symbol = Column(String, primary_key=True)
    price = Column(Float)
    change = Column(Float)
    score = Column(Float)

def init_db():
    Base.metadata.create_all(bind=engine)