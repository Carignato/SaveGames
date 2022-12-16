from sqlalchemy import Column, String, Integer, Date
from database.postgres import Base
    
class RegisterModel(Base):
    """
    A model for the Registrer to be defined on the database.
    """
    __tablename__ = "Register"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    surname = Column(String(32), nullable=False)
    username = Column(String(24), nullable=False, unique=True)
    email = Column(String(64), nullable=True , unique=True)
    password = Column(String(128), nullable=False)
    confirm_password = Column(String(128), nullable=False)
    date = Column(String(12), nullable=True)
    
    def __rep__(self):
        return f"RegisterModel<{self.id}>"
