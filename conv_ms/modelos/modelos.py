import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_login import UserMixin

from sqlalchemy import DateTime
from marshmallow import fields
from sqlalchemy.sql import func

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    name = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Usuario, self).__init__(*args, **kw)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        return checked

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Usuario.query.get(id)

    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(email=email).first()
    
class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

usuario_schema = UsuarioSchema()

class ExtSound(enum.Enum):
    MP3 = 1
    ACC = 2
    OGG = 3
    WAV = 4
    WMA = 5
    
class EstadoTarea(enum.Enum):
    UPLOADED = 1
    PROCESSED = 2

class Tarea(db.Model):
    __tablename__ = 'tarea'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(DateTime(timezone=True), nullable=False, default=func.now())
    id_usr = db.Column(db.Integer, nullable=False)
    nom_arch = db.Column(db.Unicode(128))
    ext_conv = db.Column(db.Enum(ExtSound))
    estado = db.Column(db.Enum(EstadoTarea), default=EstadoTarea.UPLOADED)
    is_lock = db.Column(db.Boolean, default=False)
    
class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        else:
            return {'llave':value.name, 'valor':value.value}
    
class TareaSchema(SQLAlchemyAutoSchema):
    ext_conv=EnumADiccionario(attribute=('ext_conv'))
    estado=EnumADiccionario(attribute=('estado'))
    class Meta:
        model = Tarea
        include_relationships = True
        load_instance = True