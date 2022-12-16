from database.postgres import PostgresqlConnectionAdapter, Base

class CreateModels():
    def __init__(self) -> None:
        db_connection = PostgresqlConnectionAdapter()
        engine = db_connection.get_engine()
        Base.metadata.create_all(engine)