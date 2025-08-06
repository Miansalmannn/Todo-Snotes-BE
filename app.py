from flask import Flask, redirect, url_for
from extensions import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

  
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

  
    from routes.auth import auth_bp
    from routes.todos import main_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api')

    
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

  
    with app.app_context():
        from models import User, Todo  

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
