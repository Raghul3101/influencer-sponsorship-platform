from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c482ba3f2b73413d9638e3a710edfa35'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///influencer_platform.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

if __name__ == '__main__':
    app.run(debug=True)
