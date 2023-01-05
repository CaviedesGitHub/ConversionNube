from flask import Flask
from sqlalchemy.engine import URL

keepalive_kwargs = {
  "keepalives": 1,
  "keepalives_idle": 60,
  "keepalives_interval": 10,
  "keepalives_count": 5
}

url_object = URL.create(
    "postgresql+psycopg2",
    username="admin",
    password="admin",  # plain (unescaped) text
    host="localhost",
    port=5432,
    database="ConversionAudio",
    query=dict(keepalives='1', keepalives_idle='60', keepalives_interval='10', keepalives_count='5'),
    
)

def create_app(config_name):
    app=Flask(__name__)
    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    app.config['SQLALCHEMY_DATABASE_URI'] = url_object  #'postgresql://admin:admin@localhost:5432/ConversionAudio'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 10, 'pool_recycle': 280, 'pool_timeout': 100, 'pool_pre_ping': True}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app