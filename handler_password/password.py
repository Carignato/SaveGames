from flask import Blueprint, render_template, redirect, url_for, session, flash, request
import sqlite3

blueprint_password = Blueprint('password',
                               __name__,
                               template_folder='templates')

# Rota para a pagina forgot_password
@blueprint_password.route("/forgot_password")  
def forgot_password():
     print('aaa')

     return 'aa'

# Rota para a pagina Reset_password
@blueprint_password.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")
    

# Rota do botão "Esqueci minha senha" na pagina home
@blueprint_password.route("/send_to_forgot") 
def send_to_forgot():
    return redirect(url_for("forgot_password"))    


# Rota para a pagina forgot_password_accept
@blueprint_password.route("/forgot_password_accept")  
def forgot_password_accept():
    return render_template("forgot_password_accept.html")   


# Rota para a pagina Change_password
@blueprint_password.route("/change_password", methods = ["GET","POST"])   
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

@blueprint_password.route("/send_forgot_pass", methods=['POST'])   

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
    
# Rota para a função de enviar a nova senha, através do link enviado por e-mail
@blueprint_password.route("/send_reset_password", methods=["POST"])
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
@blueprint_password.route('/change_credentials', methods = ['POST'])    
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
    