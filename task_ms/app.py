from task_ms import create_app
from task_ms.vistas.vistas import VistaConversion, VistaTarea, VistaArchivo
from task_ms.modelos.modelos import db
from flask_restful import Api
from flask_jwt_extended import JWTManager


app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()


api=Api(app)
api.add_resource(VistaConversion, '/api/tasks/')
api.add_resource(VistaTarea, '/api/task/<int:id_task>/')
api.add_resource(VistaArchivo, '/api/files/<int:id_task>/')


jwt = JWTManager(app)

