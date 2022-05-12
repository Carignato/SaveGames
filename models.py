from click import password_option
from sqlalchemy import BLOB, VARBINARY, create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Date

# Cria o banco de dados sqlite 
engine = create_engine('sqlite:///savegames.db', echo=True)
metadata = MetaData(bind=engine)  
#Cria a tabela Usuarios
Usuarios = Table('Usuarios', metadata,
                      Column('id', Integer(), primary_key = True),
                      Column('nome', String(40), nullable= False),
                      Column('sobrenome', String(40), nullable= False),
                      Column('username', String(40), unique= True),
                      Column('email', String(82), nullable= False,  unique= True),
                      Column('password', String(82), nullable= False),
                      Column('date', Date, nullable= False),
                      Column('admin', String(3), nullable= False),
                      Column('user_img', String(100), nullable=True))
                      
                 
metadata.create_all()    

class Cadastro:
  def __init__(self,nome, sobrenome, username, email, password, confirm_password, date,  admin):
        self.nome = nome
        self.sobrenome = sobrenome
        self.username = username
        self.email = email  
        self.password =  password
        self.confirm_password = confirm_password
        self.date = date  
        self.admin = admin
        

class Login_home:
  def __init__(self, email, password):
        self.email = email
        self.password = password  

class Forgot_password:
  def __init__(self, email):
     self.email = email

class Reset_password:
  def __init__(self,confirm_email,password, confirm_password):
      self.confirm_email = confirm_email     
      self.password = password
      self.confirm_password = confirm_password



class Change_credentials:
  def __init__(self,username,email,confirm_email):
    self.username = username
    self.email = email
    self.confirm_email = confirm_email

class Add_game:
  def __init__(self, plataforma, nome, status, link) :
    self.plataforma = plataforma
    self.nome = nome
    self.status = status
    self.link = link

class Edit_game:
  def __init__(self, plataforma, nome, status, link, game_id) :
    self.plataforma = plataforma
    self.nome = nome
    self.status = status
    self.link = link
    self.game_id = game_id
    

class Meta:
        managed = False
        db_table = 'Usuarios' , 


