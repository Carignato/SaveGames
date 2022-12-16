from werkzeug.security import generate_password_hash, check_password_hash


def generate_hash(password):
    password_encrypted = generate_password_hash(password, 'sha256')
    
    return password_encrypted
 
    
