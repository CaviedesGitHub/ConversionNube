from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_login import (current_user, login_user, logout_user, login_required)
from auth_ms.modelos.modelos import db, Usuario, UsuarioSchema

usuario_schema = UsuarioSchema()
class VistaSignIn(Resource):   
    def post(self):
        print('VistaSignIn')
        if request.json['password']==request.json['password2']:
            usuario=Usuario.query.filter(Usuario.email == request.json["email"]).first()
            if usuario is None:
                print(request.json["is_admin"])
                nuevo_usuario = Usuario(name=request.json["name"], email=request.json["email"], is_admin=eval(request.json["is_admin"]))
                nuevo_usuario.set_password(request.json["password"])
                db.session.add(nuevo_usuario)
                db.session.commit()
                login_user(nuevo_usuario)
                token_de_acceso = create_access_token(identity=nuevo_usuario.id)
                return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}
            else:
                return {"mensaje": "Usuario Ya Existe"}
        else:
            return {"mensaje": "No coincide password de confirmación"}

class VistaLogIn(Resource):
    def post(self):
        usuario = Usuario.query.filter(Usuario.email == request.json["email"]).first()
        db.session.commit()
        if usuario is not None and usuario.authenticate(request.json["password"]):
            login_user(usuario)
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}
        else:
            return {"mensaje":"LogIn Incorrecto."}, 404

class VistaLogOut(Resource):
    def post(self):
        logout_user()
        return {"mensaje":"LogOut Exitoso."}


class VistaUsuario(Resource):   
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        return usuario_schema.dump(usuario)

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if request.json.get("password") is not None:
           usuario.set_password(request.json["password"])
        usuario.name=request.json.get("name", usuario.name)
        usuario.email=request.json.get("email", usuario.email)
        if request.json.get("is_admin") is not None:
           usuario.is_admin=eval(request.json.get("is_admin"))
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return "Usuario Borrado.",  204

class VistaUsuarios(Resource):   
   @jwt_required()     
   def get(self):
       user_jwt=int(get_jwt_identity())  
       if current_user.is_authenticated:  ##current_user.get_id() is not None:
            if current_user.get_id()==user_jwt:  
                if current_user.is_admin:
                    return [usuario_schema.dump(user) for user in Usuario.query] 
       return  {"Msg":"Usuario desautorizado."}

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong"}