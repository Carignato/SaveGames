from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from random import randint
from werkzeug.utils import secure_filename
from utils import generate_hash
import uuid
import os
import sqlite3
from handler_register.data_objects import RegisterDto, LoginDto

from database.repositories.register_repository import RegisterRepositoryPostgresql

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
postgresql = RegisterRepositoryPostgresql()


blueprint_register = Blueprint('register',
                               __name__,
                               template_folder='templates',
                               static_folder='static',
                               url_prefix='/')


# Função que habilita os anexos de arquivo na pagina de perfil do Usuario:?>Ç
def allowed_file(filename) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Rota para a pagina home, que é a tela de login
@blueprint_register.route("/home")
def homepage():
    
    if session.get('email'):
   
            return redirect(url_for('main'))

    return render_template("home.html")    

#Rota para a pagina main.html, que é a tela após a autenticação da tela home
@blueprint_register.route("/main")
def main():
   
    return render_template("main.html")


#Rota para a pagina cadastro, após clicar no botão cadastrar-se na pagina home
@blueprint_register.route("/register", methods = ['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        register = RegisterDto(name=request.form['name'],
                               surname=request.form['surname'],
                               username=request.form['username'],
                               email=request.form['email'],
                               password=generate_hash(request.form['password']),
                               confirm_password=request.form['confirm_password'],
                               date=request.form['date']
    )
        print(register)
        
        check_if_already_exists = postgresql.get(register) 
        
        if check_if_already_exists:
           print('User already exists in database')
        
        postgresql.insert(register)       
        return render_template("cadastro.html")
           
    else:   
        return render_template("cadastro.html")

 
@blueprint_register.route("/cadastro_users_admin")
def cadastro_users_admin():
    return render_template("cadastro_users_admin.html")   



# Rota do botão "sair" que fica na pagina main.htmld
@blueprint_register.route("/logout")
def logout():
    
    [session.pop(key) for key in list(session.keys())]
    
    
    return redirect("/home")

 
#Rota para a pagina profile.html
@blueprint_register.route("/profile")
def profile():

    # Caso o objeto data esteja na sessão(caso o usuario esteja logado) irá fazer um select para pegar o nome da imagem do usuario logado no banco e associar essa imagem 
    # a uma variavel chamada filename, caso o filename seja None ele irá assumir que o usuario não escolheu foto na sessão de upload de foto e irá utilizar o default_profile_pic.png
    # caso o filename seja diferente de None ele irá assumir que o usuario tem uma foto de perfil e com isso a gente passa para o render template a variavel.

     data = {}
     if 'data' in session:
        data = session['data'] 
        

        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user_img from Usuarios where username = '{session['data']['username']}' ")
        user_img = cursor.fetchall()
        filename = user_img[0][0]
        cursor.close()
        sqliteConnection.commit()
        if filename == 'None':
            filename = 'default_profile_pic.png' 

        return render_template("profile.html",filename = filename, data = data)

     return render_template("profile.html", data=data)   


   

# Rota para a pagina picture.html 
@blueprint_register.route("/picture")
def picture():

    # Caso o objeto data esteja na sessão(caso o usuario esteja logado) irá fazer um select para pegar o nome da imagem do usuario logado no banco e associar essa imagem 
    # a uma variavel chamada filename, caso o filename seja None ele irá assumir que o usuario não escolheu foto na sessão de upload de foto e irá utilizar o default_profile_pic.png
    # caso o filename seja diferente de None ele irá assumir que o usuario tem uma foto de perfil e com isso a gente passa para o render template a variavel.

    data = {}
    filename = 'None'
    if 'data' in session:
        data = session['data'] 
        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user_img from Usuarios where username = '{session['data']['username']}' ")
        user_img = cursor.fetchall()
        filename = user_img[0][0]
        cursor.close()
        sqliteConnection.commit()
    if filename == 'None':
        filename = 'default_profile_pic.png' 

    return render_template("picture.html",filename = filename, data = data)


#Função que pega o login e senha e envia para a pagina main
@blueprint_register.route("/login_user", methods=["POST", "GET"])  
def login_main():
    
    x = request.form['email']
    y = request.form['password']
    
    print(x)
    print(y)
    
    login = LoginDto(email = x,
                     password = y)
    print(login.__dict__)
    
    
    '''
    login= [] 
    form = Login_home(request.form['email'], password = request.form['password'])
    login.append(form)
    
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()   
    cursor.execute(f"SELECT email FROM Usuarios WHERE email = '{form.email}'")
    
    # Se o resultado do select retornar um valor maior que 0, quer dizer que o login existe na base
    if len(cursor.fetchall()) > 0:
            cursor.execute(f"SELECT password, username, email, user_img, admin, user_id FROM Usuarios WHERE email = '{form.email}'")
            query_result = cursor.fetchall()
           
  
            # Checa se a senha passada pelo usuario bate com o hash gravado no banco
            if bcrypt.check_password_hash(query_result[0][0].encode(),form.password.encode()):

                data = {"email": query_result[0][2],"username": query_result[0][1],"user_img": query_result[0][3],"admin": query_result[0][4], "user_id": query_result[0][5]}
                session["data"] = data
                sqliteConnection.commit()
                print(session)
                
                if query_result[0][4] != 'on':
                    login_admin_Accept = False
                    return redirect(url_for('main'))   

                login_admin_Accept = True
                return redirect(url_for('main'))
               
            # Caso a senha esteja errada irá retornar uma mensagem dizendo 'Senha incorreta'
            else:   
                flash('Senha incorreta', 'password_error') 
                cursor.close()
                return redirect(url_for('homepage'))
                

    # Caso o email não esteja cadastrado, irá retornar uma mensage dizendo 'Esse email não está cadastrado no SaveGames'
    else:
         flash('Esse email não está cadastrado no SaveGames')   
         cursor.close()
         
    '''     
    return render_template('home.html')


#Função que pega os dados do formulario de cadastro e envia para o banco 
@blueprint_register.route('/send_cadastro', methods = ['POST'])
def cadastro_form():  
    form = Cadastro(nome = request.form['nome'],
        sobrenome =  request.form['sobrenome'],
        username =  request.form['username'],
        email =  request.form['email'],
        password =  request.form['password'],
        confirm_password =  request.form['confirm_password'],
        date =  request.form['date'],
        admin = request.form['admin'] if 'admin' in request.form else 'off')
        
    
    # Irá gerar o ID 
    id = (randint(0,100))   

    print(form.admin)

    # Irá gerar o hash criptografado da senha que o form enviou
    pw_hash = bcrypt.generate_password_hash(form.password)
    #Conexão com o sqlite    
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()

    # Caso o usuario já esteja cadastrado irá retornar uma mensagem dizendo 'Este usuário já está cadastrado'
    cursor.execute(f" select username from Usuarios where username = '{form.username}'")
    if len(cursor.fetchall()) > 0:
        flash('Este usuário já está cadastrado', 'error_username')
        cursor.close()
        return redirect(url_for("cadastro"))
    
    # Caso o usuario digite uma username menor que 4 digitos irá retornar uma mensagem dizendo 'Por favor digite um username com no minimo 4 caracteres'
    elif len(form.username) < 4:
        flash('Por favor digite um username com no minimo 4 caracteres', 'error_username_two') 
        cursor.close()
        return redirect(url_for("cadastro"))

      # Caso o usuario digite a confirmação da senha diferente da senha irá retornar uma mensagem dizendo 'As senhas não são iguais'
    elif form.password != form.confirm_password:
        flash('As senhas não são iguais', 'pass_error') 
        cursor.close()
        return redirect(url_for("cadastro"))

      # Caso o usuario digite uma senha menor que 8 digitos irá retornar uma mensagem 'Por favor digite uma senha com no minimo 8 caracteres'
    elif len(form.password) and len(form.confirm_password) <= 7:
           flash('Por favor digite uma senha com no minimo 8 caracteres', 'error_password_two')   
           return redirect(url_for("cadastro")) 
    else:

        # Caso o usuario digite um email que já exista na base irá retornar uma mensagem 'Esse email já existe'
        cursor.execute(f" select email from Usuarios where email = '{form.email}'")
        if len(cursor.fetchall()) > 0:
         flash('Esse email já existe', 'email_error')      
         return redirect(url_for("cadastro"))   

        else:

            # Caso todos os dados estejam corretos, irá inserir os dados na tabela Usuarios dentro do Banco, o None é para a imagem, que no caso só vamos adicionar depois
            # na sessão de picture

            sqliteConnection = sqlite3.connect('Savegames.db')
            cursor = sqliteConnection.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO Usuarios VALUES ('{id}', '{form.nome}', '{form.sobrenome}','{form.username}','{form.email}','{pw_hash.decode()}','{form.date}','{form.admin}','{None}')") 

            sqliteConnection.commit()
            cursor.close()
            return redirect(url_for("homepage"))
            

# Função que envia uma imagem que irá servir como imagem de perfil do usuario
@blueprint_register.route("/upload_img", methods=["GET","POST"])
def upload_img(): 
 
    # Caso o objeto data esteja na sessão(caso o usuario esteja logado) irá fazer um select para pegar o nome da imagem do usuario logado no banco e associar essa imagem 
    # a uma variavel chamada filename, caso o filename seja None ele irá assumir que o usuario não escolheu foto na sessão de upload de foto e irá utilizar o default_profile_pic.png
    # caso o filename seja diferente de None ele irá assumir que o usuario tem uma foto de perfil e com isso a gente passa para o render template a variavel.

    data = {}
    if 'data' in session:
        data = session['data'] 
        

        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user_img from Usuarios where username = '{session['data']['username']}' ")
        user_img = cursor.fetchall()
        filename = user_img[0][0]
        cursor.close()
        sqliteConnection.commit()
   
    # Caso a requisição vier via POST, quer dizer que o usuario enviou uma imagem
    if request.method =='POST':
        image = request.files['file']

        # Irá utilizar o secure_filename, para termos uma camada de segurança e o usuario não poder inserir qualquer imagem
        filename = secure_filename(image.filename)

        # Irá gerar um unique ID para a imagem, para que a gente possa diferenciar cada imagem
        filename_uuid = str(uuid.uuid1()) + "_" + filename
        # Irá adicionar o nome do arquivo que o usuario enviou + o unique ID
        filename =  filename_uuid
        # Irá salvar o arquivo que o usuario enviou no BASEDIR
        basedir = os.path.abspath(os.path.dirname(__file__))
        #image.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], filename))
    
        # Caso o objeto data esteja na sessão(caso o usuario esteja logado)
        if 'data' in session:
            sqliteConnection = sqlite3.connect('Savegames.db')
            cursor = sqliteConnection.cursor()
            # Irá selecionar o username, email, e user_img do usuario que esta logado na sessão 
            cursor.execute(f"SELECT user_img FROM Usuarios WHERE email = '{session['data']['email']}'")
            dados = cursor.fetchall()
            sqliteConnection.commit()
           

            # Caso o select retorne um valor diferente de 'None'  ira atualizar a string da imagem no banco e remover a antiga da pasta user_img
            if dados[0][0] != 'None':
                 cursor.execute(f"UPDATE Usuarios SET user_img = '{filename}' where username = '{session['data']['username']}' ")
                 sqliteConnection.commit()
                 os.remove(f"C:\\Users\\l.carignato\\Desktop\\Projeto web Flask\\static\\img_user\\{dados[0][0]}")
                 return render_template("picture.html",filename = filename, data=data)

            # Caso o select retorne 'None' ele irá atualizar a imagem no banco    
            else:
                cursor.execute(f"UPDATE Usuarios SET user_img = '{filename}' where username = '{session['data']['username']}' ")
                
                sqliteConnection.commit()
                return render_template("picture.html",filename = filename, data = data)
        
        return redirect(url_for("main"))
 
 
    # caso a data esteja na sesão irá rodar um select que caso o resultado dele seja igual a 'None' irá setar o filename como 'default_profile_pic.png'
    if 'data' in session:
        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user_img from Usuarios where username = '{session['data']['username']}' ")
        data = cursor.fetchall()
        filename = data[0][0]
        cursor.close()
        sqliteConnection.commit()
        if filename == 'None':
            filename = 'default_profile_pic.png' 
        return render_template("picture.html",filename = filename, data= data)
        
#Rota do botão "Reset Password" na pagina de redefinição de senha, caso o email não exista ele retorna uma mensagem
#caso exista ele envia um email com o passo a passo para a redefinição de senha
