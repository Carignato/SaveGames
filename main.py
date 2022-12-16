from routes import app
from database.models.create_models import CreateModels

# Colocar o site no ar
if __name__ =="__main__":   
    CreateModels()
    app.run(debug=True)

