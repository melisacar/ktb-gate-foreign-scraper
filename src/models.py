from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker #
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, Integer, Date, String, Float

Base = declarative_base()

# Define the ist_sinir_gelen_yabanci table
class ist_sinir_gelen_yabanci(Base):
    __tablename__ = 'ist_sinir_gelen_yabanci'
    __tableargs__ = (UniqueConstraint('tarih', 'sinir_kapilari', 'yabanci_ziyaretci'),
                 {'schema': 'etl'}
                 )
    id = Column(Integer, primary_key=True, autoincrement=True)
    tarih = Column(Date, nullable=True)
    sinir_kapilari = Column(String, nullable=True)
    yabanci_ziyaretci = Column(Float, nullable=True)
    erisim_tarihi = Column(Date, nullable=False)

