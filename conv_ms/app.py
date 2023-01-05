import os
import shutil
from conv_ms import create_app
from conv_ms.modelos.modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema, ExtSound, EstadoTarea
from conv_ms.flask_celery import make_celery
from celery.schedules import crontab
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from pydub import AudioSegment

app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

celery_app=make_celery(app)
celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'conv_ms.app.convertir_archivos',
        'schedule': 1.0,
        'args': ('prueba', datetime.utcnow())
    },
}  #minute='*/1'  crontab(sec='*/1')
celery_app.conf.timezone = 'UTC'

@celery_app.task(name='conv_ms.app.convertir_archivos', bind=True, ignore_result=False)
def convertir_archivos(self, nom_arch, fecha):
    print("convertir_archivos")
    salida=0
    while True:
        if salida==1:
            print("SALIENDO")
            break
        #try:
        tarea=Tarea.query.with_for_update().filter(Tarea.estado==EstadoTarea.UPLOADED, Tarea.is_lock==False).order_by(Tarea.fecha.asc()).first()
        #result=db.session.query(Tarea.id, Tarea.estado, Tarea.is_lock).with_for_update().filter(Tarea.estado==EstadoTarea.UPLOADED, Tarea.is_lock==False).order_by(Tarea.fecha.asc()).first()
        #tarea=result[0]
        #except Exception as excep:
        #    print("ERROR BLOQUEANDO REGISTRO")
        #    break
        if tarea is None:
            print("SALIENDO: sin tareas pendientes")
            break
        print(tarea)
        try:
            tarea.is_lock=True
            db.session.add(tarea)
            db.session.commit()
        except Exception as excep:   #  IntegrityError:
            db.session.rollback()
            break #continue

        if convArchivo(tarea.id, tarea.nom_arch, tarea.ext_conv.name.lower())==1:
           tarea=Tarea.query.with_for_update().get(tarea.id)
           if tarea is not None:
               tarea.is_lock=False
               tarea.estado=EstadoTarea.PROCESSED
               db.session.commit()
        else:
            tarea=Tarea.query.with_for_update().get(tarea.id)
            if tarea is not None:
               tarea.is_lock=False
               tarea.estado=EstadoTarea.UPLOADED
               db.session.commit()
    print("FIN convertir_archivos")

def convArchivo(id, nombre, ext):
    nombre_in=nombre.replace('.', '-'+str(id)+'.')
    nombre_out=os.path.splitext(nombre_in)[0]+'.'+ext.lower()
    nombre_in=os.getcwd()+'/archivos/input/'+nombre_in    
    nombre_out=os.getcwd()+'/archivos/output/'+nombre_out
    print(nombre_in)
    print(nombre_out)
    #extension = os.path.basename(nombre)
    try:
        if nombre.endswith('.wav'):
            print(".wav")
            song = AudioSegment.from_wav(nombre_in)
        elif nombre.endswith('.mp3'):
            print(".mp3")  
            song = AudioSegment.from_mp3(nombre_in)
        elif nombre.endswith('.ogg'):
            print(".ogg")
            song = AudioSegment.from_ogg(nombre_in)   

        print("Antes de exportar")
        print(ext.lower())
        song.export(nombre_out, format=ext.lower())
        return 1
    except Exception as inst:
        return 0   #shutil.copy(nombre_in, nombre_out)

def nombre_input(nom, id):
   temp=nom
   temp=temp.replace('.', '-'+str(id)+'.')
   temp='/home/luis/Desarrollo/repo/nube/ConversionNube/archivos/'+'input/'+temp
   return temp

def nombre_output(nom, id, ext):
   temp=nom
   temp=temp.replace('.', '-'+str(id)+'.')
   temp=os.path.splitext(temp)[0]+'.'+ext.lower()
   temp='/home/luis/Desarrollo/repo/nube/ConversionNube/archivos/'+'output/'+temp
   return temp