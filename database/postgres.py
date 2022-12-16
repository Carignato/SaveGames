from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

    
Base = declarative_base()

class PostgresqlConnectionAdapter:
    def __init__(self) -> None:
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.user = 'postgres'    
        self.password = '123'
        self.host = 'localhost'
        self.port = 5432
        self.db = 'postgres'
        self.SQLACHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        self.__connection_string = self.SQLACHEMY_DATABASE_URI
        
        
    def get_engine(self): 
        """ Cria um mecanismo que realiza a comunicação do nosso programa com a base de dados
            param: None
            return: engine connection to Database
        """    
        engine = create_engine(self.__connection_string, echo = True)
        print('a')
        return engine        
    
    def __enter__(self): 
        engine = self.get_engine()
        session = sessionmaker()
        self.session = session(bind=engine) 
        
        return self  
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()     