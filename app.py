
import uuid
from flask import Flask, flash, render_template, request, redirect, url_for, session, Response
from models import *
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_bcrypt import Bcrypt
import email.message 
import smtplib
from werkzeug.utils import secure_filename
from time import sleep
import os
from random import randint
import requests
from flask_modals import Modal

app = Flask(__name__)   
app._static_folder="static"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
modal = Modal(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
UPLOAD_FOLDER = 'C:\\Users\\l.carignato\\Desktop\\Projeto web Flask\\static\\img_user'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Função que habilita os anexos de arquivo na pagina de perfil do Usuario
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Rota para a pagina home, que é a tela de login
@app.route("/home")
def homepage():
    
    if session.get('email'):
   
            return redirect(url_for('main'))

    return render_template("home.html")    

#Rota para a pagina main.html, que é a tela após a autenticação da tela home
@app.route("/main")
def main():

    # Caso o objeto data esteja na sessão(caso o usuario esteja logado) irá fazer um select para pegar o nome da imagem do usuario logado no banco e associar essa imagem 
    # a uma variavel chamada filename, caso o filename seja None ele irá assumir que o usuario não escolheu foto na sessão de upload de foto e irá utilizar o default_profile_pic.png
    # caso o filename seja diferente de None ele irá assumir que o usuario tem uma foto de perfil e com isso a gente passa para o render template a variavel.
    if 'data' in session:
        data = {}
        data = session['data'] 
       

        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user_img, admin from Usuarios where username = '{session['data']['username']}' ")
        data = cursor.fetchall()
        filename = data[0][0]
        admin = data[0][1]
        
      
        cursor.execute(f"SELECT plataforma, nome, status, link, game_id FROM games;")
        dados_games = cursor.fetchall()
        cursor.close()
        print(dados_games)

        if filename == 'None':
            filename = 'default_profile_pic.png' 

        return render_template("main.html",filename = filename, data = data, admin = admin,  games = dados_games)
    
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT plataforma, nome, status, link, game_id FROM games;")
    dados_games = cursor.fetchall()
    cursor.close()
    print(dados_games)
    
    
    

    filename = 'default_profile_pic.png' 
    data = 'Null'
    return render_template("main.html" ,filename = filename, data = data, games = dados_games)


#Rota para a pagina cadastro, após clicar no botão cadastrar-se na pagina home
@app.route("/cadastro")
def cadastro():
        return render_template("cadastro.html")

# Rota para a pagina forgot_password
@app.route("/forgot_password")  
def forgot_password():

     return render_template("forgot_password.html")     

# Rota para a pagina Reset_password
@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")
    

# Rota para a pagina forgot_password_accept
@app.route("/forgot_password_accept")  
def forgot_password_accept():
    return render_template("forgot_password_accept.html")   

 
@app.route("/cadastro_users_admin")
def cadastro_users_admin():
    return render_template("cadastro_users_admin.html")   

@app.route("/edit_game")
def edit_game():

    game_id = request.args.get('id')
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT plataforma, nome, status, link, game_id FROM games where game_id = '{game_id}'")
    dados_games = cursor.fetchall()
    print(dados_games)
    data = {"plataforma": dados_games[0][0],"nome": dados_games[0][1],"status": dados_games[0][2],"link": dados_games[0][3], "game_id": dados_games[0][4]}
   

    return render_template("edit_game.html", data = data)


@app.route("/send_edit_game", methods=["GET","POST"])
def send_edit_game():

    form = Edit_game(plataforma = request.form['plataforma'],
    nome = request.form['nome'],
    status = request.form['status'],
    game_id = request.form['game_id'],    
    link = request.form['link'])
    


    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT plataforma, nome, status, link, game_id from games where game_id = '{form.game_id}'")
    dados_games = cursor.fetchall()

    data = {"plataforma": dados_games[0][0],"nome": dados_games[0][1],"status": dados_games[0][2],"link": dados_games[0][3], "game_id": dados_games[0][4]}
 
    
    if len(form.nome) <= 0:
          flash('Insira o nome do jogo', 'error_game_name') 

    if len(form.nome) > 50:
          flash('Valor maximo de caracteres para o nome do jogo excedido', 'error_game_name')       

    elif len(form.link) <=20:     
          flash('Insira o link da pasta da tradução', 'error_game_link')
          return render_template('edit_game.html', data = data)    

    elif (form.link[0:4] != 'http'):
          flash('Insira o link da pasta com o http ou https na frente', 'broken_link_2')
          return render_template('edit_game.html', data = data)  
      
        
    s = requests.Session() 
    try:
         response = requests.get(f'{form.link}')
    except requests.exceptions.RequestException as err:
         print(err)
         flash('Link quebrado, por favor verifique o link', 'broken_link')

        
    finally:   
        
    
        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f" UPDATE games SET status = '{form.status}', link = '{form.link}' where  game_id ='{form.game_id}' ")  
        sqliteConnection.commit()
        
        
        return redirect(url_for('edit_page'))   


@app.route("/add_page")
def add_page():

     data = {}
     if 'data' in session:
        data = session['data']['admin'] 
        if data == 'on':    

         return render_template("add_page.html")  
         
     return Response("Você não está autorizado a acessar essa pagina", status=203, mimetype='application/json')

@app.route("/edit_page")
def edit_page():
    data = {}
    if 'data' in session:
        data = session['data']['admin'] 
        if data == 'on':     
            sqliteConnection = sqlite3.connect('Savegames.db')
            cursor = sqliteConnection.cursor()
            cursor.execute(f"SELECT plataforma, nome, status, link, game_id FROM games;")
            dados_games  = cursor.fetchall()

           
    
                
            return render_template("edit_page.html", games = dados_games)   
    return Response("Você não está autorizado a acessar essa pagina", status=203, mimetype='application/json')


# Rota do botão "sair" que fica na pagina main.htmld
@app.route("/logout")
def logout():
    
    [session.pop(key) for key in list(session.keys())]
    
    
    return redirect("/home")

# Rota para a pagina Change_password
@app.route("/change_password", methods = ["GET","POST"])   
def change_password():

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

        return render_template("change_password.html",filename = filename, data = data)

     return render_template("change_password.html", data=data)

#Rota para a pagina profile.html
@app.route("/profile")
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
@app.route("/picture")
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
@app.route("/login_user", methods=["POST", "GET"])  
def login_main():
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
         return redirect(url_for('homepage'))








#Função que pega os dados do formulario de cadastro e envia para o banco 
@app.route('/send_cadastro', methods = ['POST'])
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
@app.route("/upload_img", methods=["GET","POST"])
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
        image.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], filename))
    
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

@app.route("/send_forgot_pass", methods=['POST'])   
def send_forgot_pass():
    
    form = Forgot_password(email = request.form['email'])
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    msg = 'Email enviado'
    print(form.email)
    cursor.execute(f"SELECT email FROM usuarios WHERE email = '{form.email}'")
    
    print(form.email) 
    
    if len(cursor.fetchall()) > 0:    

        #Envia o email com o passo a passo para a redefinição de senha
        msg = email.message.Message()
        corpo_email = f"""

        <p>Recebemos uma solicitação para redefinir sua senha do SaveGames.</p>

        <p>Clique no link abaixo para criar uma nova senha</p>

        <p href="">CLIQUE AQUI PARA REDEFINIR A SUA SENHA</p>

        <p>Não solicitou esta alteração?</p>

        <p>Se você não solicitou uma nova senha, avise-nos.</p>

        """
        msg['Subject'] = "Esqueci minha senha - SaveGames"
        msg['From'] = ""
        msg['To'] = f"{form.email}"
        password = "$"
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        # Credencias para o envio do email
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
        flash('Email de troca de senha enviada', 'pass_accept')     
        return  render_template("forgot_password.html")
    
    
    # Caso o email não exista, ira apresentar uma mensagem na tela  'This email is not save in SaveGames'
    else:  
      flash('Esse email não está cadastrado no SaveGames', 'pass_error')     
      return  render_template("forgot_password.html")
    

# Rota do botão "Esqueci minha senha" na pagina home
@app.route("/send_to_forgot") 
def send_to_forgot():
    return redirect(url_for("forgot_password"))    


# Rota para a função de enviar a nova senha, através do link enviado por e-mail
@app.route("/send_reset_password", methods=["POST"])
def send_reset_password():  
    form = Reset_password(confirm_email = request.form['confirm_email'],password = request.form['password'],confirm_password =  request.form['confirm_password'])

    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()   
    cursor.execute(f"SELECT email FROM Usuarios WHERE email = '{form.confirm_email}'") 
    # Caso o email não esteja cadastrado no sistema, irá aparecer a mensagem: 'Esse email não está cadastrado no SaveGames' 
    if len(cursor.fetchall()) <= 0:   
        flash('Esse email não está cadastrado no SaveGames','email_error_2') 
        cursor.close()
        return  redirect(url_for("reset_password"))

     # Caso a senha tenha menos de 5 caracteres, irá exibir a mensagem 'Por favor, digite a sua nova senha'
    elif len(form.password) < 5 and len(form.confirm_password) < 5:
         flash('Por favor, digite a sua nova senha', 'email_error')
         cursor.close() 
         return  redirect(url_for("reset_password"))
    # Caso o email tenha menos de 5 caracteres, irá exibir a mensagem 'Por favor, digite o seu email'
    elif len(form.confirm_email) < 5:
        flash('Por favor, digite o seu email', 'email_error') 
        cursor.close()
        return  redirect(url_for("reset_password"))


    # Caso a senha e a confirmação de senha não sejam iguais, irá exibir a mensagem 'As senhas não são iguais'
    elif form.password != form.confirm_password:
        flash('As senhas não são iguais', 'pass_error') 
        cursor.close()
        return  redirect(url_for("reset_password"))  

    # Caso tudo esteja certo ele irá gerar o hash para a senha informado e ira guardar no banco
    else:
        pw_hash = bcrypt.generate_password_hash(form.password).decode('utf-8')
        bcrypt.check_password_hash(pw_hash,form.password)
        cursor.execute(f"UPDATE Usuarios SET password = '{pw_hash}' where  email = '{form.confirm_email}'")
        cursor.close()  
        sqliteConnection.commit()
        sqliteConnection.close()
        flash('Senha resetada com sucesso, clique no link abaixo para ser redirecionado para a pagina de login', 'pass_reset_success') 
        return  redirect(url_for("reset_password"))    


# Função para mudar os dados do usuario
@app.route('/change_credentials', methods = ['POST'])    
def change_credentials():
    
    form = Change_credentials(username = request.form['username'],
        email = request.form['email'],
        confirm_email = request.form['confirm_email'])


    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT username, email from Usuarios where email = '{session['data']['email']}' ")  
    query_result = cursor.fetchall()
    sqliteConnection.commit()


    if form.email == query_result[0][1]:
        flash('Você precisa atualizar o e-mail para um que não esteja em uso', 'error_email_1')
        return redirect(url_for('profile'))

    elif form.username == query_result[0][0]:
        flash('Você precisa atualizar o username para um que não esteja em uso', 'error_username_1') 
        return redirect(url_for('profile'))

    elif  form.email != form.confirm_email:
       flash('O campo novo email e confirmação de novo email não são iguais', 'error_email_2')
       return redirect(url_for('profile'))         

    else:
        if len(form.username) == 0:
            form.username = session['data']['username']
            cursor.execute(f"UPDATE Usuarios SET username = '{form.username}', email = '{form.email}'  where username = '{session['data']['username']}' ")   
            sqliteConnection.commit()
            [session.pop(key) for key in list(session.keys())]
            sleep(3)
            return redirect(url_for('main'))
    

        elif len(form.email) == 0:
            form.email  = session['data']['email']  
            cursor.execute(f"UPDATE Usuarios SET username = '{form.username}',  email = '{form.email}'  where username = '{session['data']['username']}' ")   
            sqliteConnection.commit()
            [session.pop(key) for key in list(session.keys())]
            return redirect(url_for('main'))   

        elif len(form.username) < 5:
            flash('Digite um username com no minimo 5 caracteres', 'error_username_2')
            return redirect(url_for('profile'))  
    
       
@app.route('/add_game', methods=['GET','POST'])     
def add_game():
     form = Add_game(plataforma = request.form['plataforma'],
        nome = request.form['nome'],
        status = request.form['status'],
        link = request.form['link'])
     
     sqliteConnection = sqlite3.connect('Savegames.db')
     cursor = sqliteConnection.cursor()             
     cursor.execute(f"SELECT * FROM games where link = '{form.link}' OR nome = '{form.nome}'") 
     
        

     if len(form.nome) <= 0 and (form.link[0:4] != 'http'):
          flash('Insira o nome do jogo', 'error_game_name') 
          return render_template('add_page.html')    
     elif len(form.link) <=20:     
          flash('Insira o link da pasta da tradução', 'error_game_link')
          return render_template('add_page.html')    
     elif (form.link[0:4] != 'http'):
          flash('Insira o link da pasta com o http ou https na frente', 'broken_link_2')
          return render_template('add_page.html')  
     
     elif len(cursor.fetchall()) > 0:
           flash('Esse jogo já está cadastrado na plataforma', 'error_registered_game')  
           return render_template('add_page.html')  
        
    
     s = requests.Session() 
     try:
         response = requests.get(f'{form.link}')
     except requests.exceptions.RequestException as err:
         print(err)
         flash('Link quebrado, por favor verifique o link', 'broken_link')

    
     finally:   
        form.status = 'Funcionando'
        form.plataforma = 'windows.png'
        game_id = (randint(0,5000))   
        sqliteConnection = sqlite3.connect('Savegames.db')
        cursor = sqliteConnection.cursor()
        sqliteConnection = sqlite3.connect('cache.db', timeout=10)
        print(form.plataforma)
        print(form.nome)
        cursor.execute(f"INSERT INTO games VALUES ('{session['data']['user_id']}','{form.plataforma}','{form.nome}','{form.status}','{form.link}','{game_id}')")  
        sqliteConnection.commit()
        sqliteConnection.close()
        flash('Tradução adicionada com sucesso', 'success_trad')
        return render_template('add_page.html')



# Colocar o site no ar
if __name__ =="__main__":   
 app.run(debug=True)
 

 