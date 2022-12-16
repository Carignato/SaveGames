from database.postgres import PostgresqlConnectionAdapter
from handler_register.data_objects import RegisterDto
from database.models import RegisterModel
from sqlalchemy import or_

class RegisterRepositoryPostgresql:
    def insert(self, new_register: RegisterDto):
        with PostgresqlConnectionAdapter() as db_connection:
            try:
                new_register_dict = RegisterModel(**new_register.__dict__)
                db_connection.session.add(new_register_dict)
                db_connection.session.commit()
                
            except Exception as e:
                db_connection.session.rollback()
                print(e)    
                
            finally:
                db_connection.session.close()  

    def update():
        with PostgresqlConnectionAdapter() as db_connection:
            try:
                new_exercisecategory = ExerciseCategoryModel("")
                db_connection.session.add(new_exercisecategory)
                db_connection.session.commit()
                
            except:
                db_connection.session.rollback()
                raise Exception('An error occurred while trying to insert a new association into the database') 
                
            finally:
                db_connection.session.close()
                
    def delete():
        with PostgresqlConnectionAdapter() as db_connection:
            try:
               db_connection.session.query(RegisterModel).filter(RegisterModel.email == exercisecategory).delete()
               db_connection.session.commit()

            except Exception as e:
                db_connection.session.rollback()
                print(e)
                
            finally:
                db_connection.session.close()              

  
    def get(self, register: RegisterDto):
        with PostgresqlConnectionAdapter() as db_connection:
            try:
                check_register_email = db_connection.session.query(RegisterModel).filter(or_(RegisterModel.email == register.email, RegisterModel.username == register.username)).first()

            except Exception as e:
                print(e)

            finally:
                db_connection.session.close()
                return (check_register_email)

