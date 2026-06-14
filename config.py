class Config:
    
    SECRET_KEY = "agroscore_secret"

    SQLALCHEMY_DATABASE_URI = \
        "sqlite:///agroscore.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "jwt_secret"