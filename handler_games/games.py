from flask import Blueprint, request, render_template
import sqlite3

blueprint_games = Blueprint('games',
                            __name__,
                            template_folder='templates')


@blueprint_games.route("/edit_game")
def edit_game():

    game_id = request.args.get('id')
    sqliteConnection = sqlite3.connect('Savegames.db')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT plataforma, nome, status, link, game_id FROM games where game_id = '{game_id}'")
    dados_games = cursor.fetchall()
    print(dados_games)
    data = {"plataforma": dados_games[0][0],"nome": dados_games[0][1],"status": dados_games[0][2],"link": dados_games[0][3], "game_id": dados_games[0][4]}
   

    return render_template("edit_game.html", data = data)



@blueprint_games.route("/send_edit_game", methods=["GET","POST"])
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




@blueprint_games.route("/add_page")
def add_page():

     data = {}
     if 'data' in session:
        data = session['data']['admin'] 
        if data == 'on':    

         return render_template("add_page.html")  
         
     return Response("Você não está autorizado a acessar essa pagina", status=203, mimetype='application/json')




@blueprint_games.route("/edit_page")
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



       
@blueprint_games.route('/add_game', methods=['GET','POST'])     
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
