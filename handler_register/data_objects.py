from pydantic import BaseModel, validator, constr


def check_empty_string(*argv):
    for arg in argv:
        if not arg:
            raise Exception('Empty string')
       

class RegisterDto(BaseModel):
    name: str
    surname: str
    username: str
    email: constr(regex=r"^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*$")
    password: str   
    confirm_password: str
    date: str
    
    
    _check_empty_string = validator('name',
                                    'surname',
                                    'username',
                                    'email',
                                    'password',
                                    'confirm_password',
                                    'date',
                                    allow_reuse=True)(
                                    check_empty_string)

class LoginDto(BaseModel):
    email: str
    password: str   
    
    
    _check_empty_string = validator('name',
                                    'password',
                                    allow_reuse=True)(
                                    check_empty_string)
      