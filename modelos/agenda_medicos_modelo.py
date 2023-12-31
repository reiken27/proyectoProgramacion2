# modelos/agenda_medicos_modelo.py
import csv
from datetime import datetime
from modelos.medicos_modelo import es_medico_habilitado
import re

'''
agenda
primera dimension:id medico
segunda dimension:dia_numero
tercera dimension: array con [hora_inicio,hora_fin,fecha_actualizacion]
'''
ruta_archivo_agenda='modelos/agenda_medicos.csv'
agenda={}

def llenarAgenda()->None:
    global agenda
    agenda={}
    with open(ruta_archivo_agenda, newline='') as csvfile:
        reader= csv.DictReader(csvfile)
        for row in reader:
            if agenda.get(row['id_medico']) is not None: #si existe
                agenda[row['id_medico']][row['dia_numero']]=[row['hora_inicio'],row['hora_fin'],row['fecha_actualizacion']]
            else:
                agenda[row['id_medico']]={} #si no existe
                agenda[row['id_medico']][row['dia_numero']]=[row['hora_inicio'],row['hora_fin'],row['fecha_actualizacion']]

def escribir_csv()->None:
    csvlist=convertir_agenda_a_lista()

    with open(ruta_archivo_agenda, 'w', newline='') as csvfile:
        first_row = ['id_medico','dia_numero','hora_inicio','hora_fin','fecha_actualizacion']
        writer = csv.DictWriter(csvfile, fieldnames=first_row)
        writer.writeheader()
        for string in csvlist:
            csvfile.write(string + '\n')

def convertir_agenda_a_lista():
    csv_list=[]
    for medic_id,dias_dict in agenda.items():
        for dias,lista in dias_dict.items():
            hora_inicio=lista[0]
            hora_fin=lista[1]
            fecha_actualizacion=lista[2]
            line=medic_id+","+dias+","+hora_inicio+","+hora_fin+","+fecha_actualizacion
            csv_list.append(line)
    return csv_list

def agregar_agenda(id, dia_numero, hora_inicio, hora_fin):
    global agenda
    try:
        dia_comparacion=int(dia_numero)
    except:
        return {"response":"El dia_numero debe ser un numero entre 0 y 6, lo que ha insertado no es un numero"}
    if dia_comparacion<0 or dia_comparacion>6:
        return {"response":"El dia_numero debe ser un numero entre 0 y 6"}
    if not es_medico_habilitado(id):
        return {"response":"El medico no esta habilitado"}
    if es_hora_valida(hora_inicio) and es_hora_valida(hora_fin) and es_dia_valido(getDate()):
        if str(id) not in agenda:
            agenda[str(id)]={}
        agenda[str(id)][dia_numero]=[hora_inicio,hora_fin,getDate()]
        print(agenda[id])
        escribir_csv()
        return agenda[str(id)][dia_numero]
    else:
        return {"response":"Datos ingresados invalidos"}

def editar_agenda(id, dia_numero, hora_inicio, hora_fin):
    global agenda

    if str(id) not in agenda:
        return {"Respuesta": "ID de médico no encontrado"}
    if dia_numero not in agenda[str(id)]:
        return {"Respuesta": "Día no encontrado para el médico, no puedes agregar nuevos dias utilizando PUT, debes realizarlo con POST"}
    agenda[str(id)][dia_numero] = [hora_inicio, hora_fin, getDate()]
    escribir_csv()
    return agenda[str(id)][dia_numero]

def eliminar_agenda(id_medico, dia_numero):
    id_medico=str(id_medico)
    dia_numero=str(dia_numero)
    if id_medico in agenda and dia_numero in agenda[id_medico]:
        agenda[id_medico].pop(dia_numero)
        escribir_csv()
        return {"message": "Elemento eliminado correctamente"}, 200
    else:
        return {"message": "No se ha encontrado el elemento a eliminar"}, 404

def eliminar_medico_de_agenda(id_medico):
    global agenda
    if str(id_medico) in agenda:
        del agenda[str(id_medico)]
        escribir_csv()
        print(f"El médico con ID {id_medico} ha sido eliminado de la agenda.")
    else:
        print(f"No se encontró ningún médico con el ID {id_medico} en la agenda.")

def es_dia_valido(dia_str:str)->bool:
    # Expresión regular para el formato "d/m/yyyy"
    patron = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d{4}$')
    if patron.match(dia_str):
        return True
    else:
        return False

def es_hora_valida(hora_str:str)->bool:
    # Expresión regular para el formato "HH:MM"
    patron = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    if patron.match(hora_str):
        return True
    else:
        return False

def getDate():
    hoy = datetime.now()
    fecha = hoy.strftime("%d/%m/%Y")
    return fecha

def dentro_de_horario_de_atencion(id,hora_turno,fecha_solicitud)->bool:
    if(agenda.get(id).get(fecha_a_dia_semana(fecha_solicitud))) is None:
        print("El medico no atiende ese dia")
        return False
    hora_turno=datetime.strptime(hora_turno, '%H:%M').time()
    hora_inicio=agenda.get(id).get(fecha_a_dia_semana(fecha_solicitud))[0]
    hora_inicio = datetime.strptime(hora_inicio, '%H:%M').time()
    hora_cierre=agenda.get(id).get(fecha_a_dia_semana(fecha_solicitud))[1]
    hora_cierre=datetime.strptime(hora_cierre, '%H:%M').time()
    
    if hora_turno>=hora_inicio and hora_turno<=hora_cierre:
        #print("El turno se encuentra dentro del horario de trabajo")
        return True
    else:
        #print(f"El turno se encuentra fuera del horario de atencion, intente entre las{hora_inicio} y {hora_cierre}")
        return False

def fecha_a_dia_semana(fecha)->str:
    fecha = datetime.strptime(fecha,'%d/%m/%Y')
    semana=(fecha.weekday()+1)
    #Como weekday toma a 0 como lunes y la consigna pide que domingo sea 0, se le suma 1 y se corrige en el caso de 7
    if(semana==7):
        semana=0
    return str(semana)

llenarAgenda()