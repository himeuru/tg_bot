import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlalchemyBase = dec.declarative_base()
__factory = None


def create_session() -> Session:
    global __factory
    return __factory()


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    SqlalchemyBase.metadata.create_all(engine)


class Info(SqlalchemyBase):
    __tablename__ = 'information'
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String, nullable=True)
    exp = sa.Column(sa.Integer)
    daily_photo_time = sa.Column(sa.String)

    def __repr__(self):
        return f"['{self.id}','{self.name}','{self.exp}','{self.daily_photo_time}']"


global_init("information.db")
