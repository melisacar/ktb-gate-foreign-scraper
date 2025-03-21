from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker #
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, Integer, Date, String, Float
from sqlalchemy import create_engine
from config import DATABASE_URL

Base = declarative_base()

# Define the ist_sinir_gelen_yabanci table
class ist_sinir_gelen_yabanci(Base):
    __tablename__ = 'ist_sinir_gelen_yabanci'
    __table_args__ = (UniqueConstraint('tarih', 'sinir_kapilari', 'yabanci_ziyaretci', name = 'unique_ist_sinir_kapi_ziyaretci'),
                 {'schema': 'etl'})
    id = Column(Integer, primary_key=True, autoincrement=True)
    tarih = Column(Date, nullable=True)
    sinir_kapilari = Column(String, nullable=True)
    yabanci_ziyaretci = Column(Float, nullable=True)
    erisim_tarihi = Column(Date, nullable=False)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)