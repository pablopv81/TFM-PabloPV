from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

from .core.boe_processing import BoeProcessing
from .core.neo4j_db import Neo4jDB
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect

import datetime
import os



def home(request):
    
    fecha_extraccion = ''
    error = ''
    
    if request.method == 'POST':
        fecha_extraccion=request.POST['fecha_extraccion']
        path = os.path.dirname(os.path.realpath(__file__ )) 
        with open(path+'\core\extraccion_fecha.txt', "w") as file:
            file.write(fecha_extraccion)

        if fecha_extraccion:
            if len(fecha_extraccion) == 10:
                return redirect('/boe_extraction_log')
            else:
                return HttpResponseRedirect(request.path_info)
        else:
            return HttpResponseRedirect(request.path_info)
    
    return render(request,"home.html")


def boe_extraction(request):

    departments = ('MINISTERIO DE TRABAJO Y ASUNTOS SOCIALES',
                'MINISTERIO DE TRABAJO Y SEGURIDAD SOCIAL',
                'MINISTERIO DE TRABAJO Y ECONOMÍA SOCIAL',
                'JEFATURA DEL ESTADO',
                'MINISTERIO DE EMPLEO Y SEGURIDAD SOCIAL',
                'MINISTERIO DE INCLUSIÓN, SEGURIDAD SOCIAL Y MIGRACIONES')

    sections = ('I. Disposiciones generales',
                'III. Otras disposiciones')

    
    path = os.path.dirname(os.path.realpath(__file__ )) 

    fecha_extraccion = open(path+'\core\extraccion_fecha.txt','r')
    fecha = fecha_extraccion.read()


    fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

    boe_processing_date = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

    #boe_processing_date = datetime.datetime(2022,7,1).date()

    print('-----PROCESANDO VISTA BOE LOG ------')
    print(boe_processing_date)

    boe_processing = BoeProcessing(departments,sections,boe_processing_date)

    content = boe_processing.getLog()
    
    neo4j = Neo4jDB()

    if boe_processing.get_extraction_status():
        lista = boe_processing.get_lista_final()
        neo4j.add_record(lista)


    return render(request,"boe_extraction_log.html", {'content':content})


