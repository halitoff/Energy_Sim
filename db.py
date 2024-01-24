import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/power")
Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session()

class Data(Base):
    __tablename__ = 'data'
    number = Column(Integer, primary_key=True, nullable=False)
    people = Column(Integer)
    power = Column(Integer)
    temp = Column(Integer)
    night = Column(Integer)


Base.metadata.create_all(engine)
s.query(Data).delete()
s.commit()

def write(data: list[float]):
    if len(data) != 5:
        return

    d = Data(number=data[0], people=data[1],
             power=data[2], temp=data[3], night=data[4])
    s.add(d)
    s.commit()


def read_all():
    return s.query(Data).all()




