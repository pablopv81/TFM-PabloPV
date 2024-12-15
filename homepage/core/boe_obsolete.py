import os
import json
import spacy
import datetime
import requests
import pandas as pd
import re
import pymupdf

from pypdf import PdfReader
from pathlib import Path
from bs4 import BeautifulSoup
from xml.etree import cElementTree as ET

class BoeReader:

    def __init__(self,departments,sections,boe_extraction_date):

      self.__departments = departments
      self.__boe_extraction_date = boe_extraction_date
      self.__sections = sections
      self.__status_code= {200: 'OK',
                             201: 'CREATED',
                             204: 'NO CONTENT',
                             300: 'MULTIPLE CHOICES',
                             302: 'FOUND (TEMPORARY REDIRECT)',
                             304: 'NOT MODIFIED',
                             400: 'BAD REQUEST',
                             404: 'REQUESTED INFO DOES NOT EXIST',
                             401: 'UNAUTHORIZED',
                             500: 'INTERNAL SERVER ERROR',
                             502: 'BAD GATEWAY'
                            }
      self.__headers = {'Accept': 'application/json',
                        }
      self.__file_names = []
      self.__listaboe = []
      self.__listafinal = []
      self.__folder = []
      self.__idx = 0

      #Saving the files names already extracted
      for (root, dirs, file) in os.walk(r'BOE_FILES/'):
        for f in file:
          if '.json' in f:
            f = int(f.replace('.json', ''))
            self.__file_names.append(f)

      # Last extracted file
      if self.__file_names:
        self.__last_file = self.__file_names[-1]

      # NER Custom model for detecting my entities of interest
      self.__ner_model = spacy.load('./trained_models/output/model-best')

      '''
      SAVE RELEVANT INFO FROM BOE AND PDF FILES FROM PREVIOUS BOES
      '''
      self.__boe_extraction()
      if self.__listaboe: #info to save?
        file_path = self.__folder + 'boe.xlsx'
        self.__dfboe=pd.concat(self.__listaboe,ignore_index=True,sort=False)
        self.__dfboe.to_excel(file_path,index=False)

      if self.__listafinal:
        #file_path = self.__folder + 'final.xlsx'
        file_path = self.__folder + 'final.csv'
        self.__dfFinal=pd.concat(self.__listafinal,ignore_index=True,sort=False)
        #self.__dfFinal.to_excel(file_path,index=False)
        self.__dfFinal.to_csv(file_path,encoding="utf_8_sig",sep=';',index=False)

    def __boe_extraction(self):

      boe_date = self.__boe_extraction_date
      secciones_list = []
      items_list = []

      boe_date_s = boe_date.strftime('%Y%m%d') 
      api_url = "https://boe.es/datosabiertos/api/boe/sumario/"+boe_date_s
      print(api_url)

      self.__folder = 'BOE_FILES/'+ boe_date.strftime('%Y%m%d') + '/'
      file_path = self.__folder+boe_date.strftime('%Y%m%d')+'.json'
      print(file_path)

      if Path(file_path).exists(): # CHECK IF FILE IS ALREADY DOWNLOADED -> Example -> does file '20240903.json' exists in BOE_FILES folder?
          print('FILE PATH ' + file_path + ' ALREADY EXISTS. NOT NECESSARY TO DOWNLOAD IT FROM BOE' )
      else: # IT DOES NOT EXIST CREATE THE FOLDER AND THEN DOWNLOAD FILE FROM BOE
          response = requests.get(api_url, headers=self.__headers)

          if(response.status_code == 200):
              print(self.__status_code[response.status_code])
              os.makedirs(self.__folder)

              data = response.content.decode('utf-8') # CONVERTING BYTES TO STRINGS WITH UTF-8 FORMAT

              # SAVE JSON -> Example -> BOE_FILES/20240903.json
              with open(file_path, 'w') as outf:
                  outf.write(data)
          else:
              try:
                  print(self.__status_code[response.status_code])
              except KeyError:
                  print('UNKNOW RESPONSE')

          try:
            with open(file_path, "r") as file:
              data = json.load(file)

              publicacion=data['data']['sumario']['metadatos']['publicacion']
              fecha_publicacion=data['data']['sumario']['metadatos']['fecha_publicacion']
              identificador = data['data']['sumario']['diario'][0]['sumario_diario']['identificador']
              url_pdf = data['data']['sumario']['diario'][0]['sumario_diario']['url_pdf']['texto']
              secciones = data['data']['sumario']['diario'][0]['seccion']

              ''' 
                  I have to validate if secciones is a list. There are files where it is not a list but a dict. 
                  Example -> file generated for https://boe.es/datosabiertos/api/boe/sumario/19781229
              '''
              if type(secciones) != list:
                  secciones_list.append(secciones)
                  secciones = secciones_list

              for seccion in secciones:
                                  
                codigo_seccion = seccion['codigo']
                nombre_seccion = seccion['nombre']
                

                if nombre_seccion in self.__sections:
                    '''
                        There are files where 'departamento' is not after 'seccion' but 'texto'
                        Example -> file generated for https://boe.es/datosabiertos/api/boe/sumario/19781229
                    '''
                    
                    try:
                        departamento = seccion['departamento']
                    except KeyError:
                        departamento = seccion['texto']['departamento']
                    
                    for info_departamento in departamento:
                        '''
                            There are parts of the file where 'departamento' & 'codigo' are empty
                            Check if the info from 'departamento' is a dict
                        '''             
                        if type(info_departamento) == dict:                             
                            codigo_departamento = info_departamento['codigo']
                            nombre_departamento = info_departamento['nombre']

                            if nombre_departamento in self.__departments:
                              '''
                                  There are files not containing 'epigrafe'
                                  Example -> file generated for https://boe.es/datosabiertos/api/boe/sumario/19720524
                                  In that case jumping directly to 'item' element
                              '''
                              try:
                                  for epigrafe in info_departamento['epigrafe']:

                                      nombre_epigrafe = epigrafe['nombre']

                                      if type(epigrafe['item']) != list:
                                          items_list.append(epigrafe['item'])
                                          items = items_list
                                      else:
                                          items = epigrafe['item']

                                      #Generates all the info
                                      self.__info_generation(items,
                                                              api_url,
                                                              publicacion,
                                                              fecha_publicacion,
                                                              identificador,
                                                              url_pdf,
                                                              codigo_seccion,
                                                              nombre_seccion,
                                                              codigo_departamento,
                                                              nombre_departamento,
                                                              nombre_epigrafe)
                                      items_list = []

                              except KeyError:
                                  nombre_epigrafe = 'NO EXISTE EPIGRAFE'

                                  if type(info_departamento['item']) != list:
                                      items_list.append(info_departamento['item'])
                                      items = items_list
                                  else:
                                      items = info_departamento['item']

                                  #Generates all the info
                                  self.__info_generation(items,
                                                          api_url,
                                                          publicacion,
                                                          fecha_publicacion,
                                                          identificador,
                                                          url_pdf,
                                                          codigo_seccion,
                                                          nombre_seccion,
                                                          codigo_departamento,
                                                          nombre_departamento,
                                                          nombre_epigrafe)
                                  items_list = []
          except:
            pass

    def __info_generation(self,items,
                          api_url,
                          publicacion,
                          fecha_publicacion,
                          identificador,
                          url_pdf,
                          codigo_seccion,
                          nombre_seccion,
                          codigo_departamento,
                          nombre_departamento,
                          nombre_epigrafe):

      xmlContent = ''

      for item in items:
        identificador_item = self.__validate_element(item,'identificador')
        control_item = self.__validate_element(item,'control')
        titulo_item = self.__validate_element(item,'titulo')
        url_pdf_item = self.__validate_element(item,'url_pdf')

        if url_pdf_item  == 'NO EXISTE':
            pdfsDict = {'pdfId':'',
                        'pdfContent': ''}
        else:

          
          url_pdf_item = self.__validate_element(item,'url_pdf')['texto']
          #### INICIO BORRAR ####
          #Saving the pdf content for future usage
          '''
          r = requests.get(url_pdf_item, stream=True)
          if r.status_code == 200:
            outpath = self.__folder + identificador_item
            with open(outpath, 'wb') as f:
              for chunk in r.iter_content(1024):
                f.write(chunk)
            
            f.close()

            #pdfReader = PdfReader(outpath)
            pdfReader = pymupdf.open(outpath)
            for page in pdfReader: # iterate the document pages
              pdfContent = pdfContent + page.get_text()
              
            pdfReader.close()
          '''
          #### FIN BORRAR ####


        url_html_item = self.__validate_element(item,'url_html')
        url_xml_item = self.__validate_element(item,'url_xml')


        ant_references,post_references=self.__get_references(url_xml_item)


        
        self.__listaboe.append(pd.DataFrame({ 'publicacion':publicacion,
                          'api_url': api_url,
                          'fecha_publicacion':fecha_publicacion,
                          'identificador':identificador,
                          'url_pdf': url_pdf,
                          'codigo_seccion':codigo_seccion,
                          'nombre_seccion':nombre_seccion,
                          'codigo_departamento':codigo_departamento,
                          'nombre_departamento':nombre_departamento,
                          'nombre_epigrafe': nombre_epigrafe,
                          'identificador_item': identificador_item,
                          'control_item': control_item,
                          'titulo_item': titulo_item,
                          'url_pdf_item': url_pdf_item,
                          'url_html_item': url_html_item,
                          'url_xml_item': url_xml_item,
                          'referencias_anteriores':[ant_references],
                          'referencias_posteriores':[post_references]},
                          index=[self.__idx]))

        '''
        SAVING THE XML FILES 
        '''  
        if ant_references or post_references:
          r = requests.get(url_xml_item, stream=True)
          if r.status_code == 200:
              outpath = self.__folder + identificador_item
              with open(outpath, "wb") as file:
                file.write(r.content)
              file.close()

              with open(outpath, 'r', encoding='utf-8') as f:
                data = f.read()
              f.close()
              xmlContent = BeautifulSoup(data, "xml")

              self.__main_process2(identificador_item,
                      fecha_publicacion,
                      url_html_item,
                      nombre_departamento,
                      nombre_epigrafe,
                      nombre_seccion,
                      titulo_item,
                      ant_references,
                      xmlContent)
              
          else:
            pass


        self.__idx+=1     

    def __main_process2(self,identificador_item,
                      fecha_publicacion,
                      url_html_item,
                      nombre_departamento,
                      nombre_epigrafe,
                      nombre_seccion,
                      titulo_item,
                      ant_references,
                      xmlContent):

      artDetails = []
      dispDetails = []
      old_content = ''
      new_content = ''
      contenttt = ''
      content_=''
      numRes=0
      header = ''
      

      disposcionesDict = {'1':'primera','2':'segunda', '3':'tercera', '4':'cuarta', '5':'quinta','6':'sexta','7':'séptima',
                          '8':'octava', '9':'novena', '10':'décima'}

      for reference in ant_references:
        
        #Extract acccion
        accion = reference[0]['accion']
        
        reference_content = []
        texto= reference[0]['texto']
        reference_content.append(texto)

        for content in reference_content:
        # Extract the entities with the trained model
          doc = self.__ner_model(content)
          for word in doc.ents:
            if (word.label_ == 'ART' or word.label_  == 'DISP') and (accion=='MODIFICA' or accion=='AÑADE'):
              boe_referencia = doc.ents[0][0]
              link = 'https://www.boe.es/buscar/doc.php?id=' + str(boe_referencia)
              page = requests.get(link)
              soup = BeautifulSoup(page.content, 'html.parser')

              entity_type = word.label_

              # Get each articulo and disposcion
              entidades = str(word.text).replace("arts. ","")
              entidades = str(entidades).replace("Arts. ","")  
              entidades = str(entidades).replace("art. ","")        
              entidades = str(entidades).replace("Art. ","")  
              entidades = str(entidades).replace("disposición ","")
              entidades = str(entidades).replace("Disposición ","")
              entidades = str(entidades).replace("disposiciones ","") 
              entidades = str(entidades).replace("Disposiciones ","")

              if word.label_ == 'ART':
                # art 1,2 y 3, art 1 y 2
                arts = re.split(',|y', entidades)
                
                for art in arts:

                  x = art.split(".")
                  if len(x) == 1:
                    articulo = x[0].strip()
                    apartado = 0
                    subapartado = 0
                    validador = 'artículo ' + articulo
                  
                  elif len(x) == 2:
                    articulo = x[0].strip()
                    apartado = x[1].strip()
                    subapartado = 0
                    validador = 'apartado ' + apartado + ' del artículo ' + articulo 
                  elif len(x) == 3:
                    articulo = x[0].strip()
                    apartado = x[1].strip()
                    subapartado = x[2].strip()
                    validador = 'artículo ' + articulo + apartado + subapartado
                  
                  
                  #validador = validador.replace(')','')
                  validador = 'artículo ' + articulo
                  validadorAux = 'artículo ' + articulo
                  #ppv = r'\b'+'({})'.format(validador)+r'\b'
                  ppv= r"(?<!\S)"+'{}'.format(validador)+r"(?!\S)"

                  artDetails.append({'articulo':articulo,
                                  'apartado':apartado,
                                  'subapartado':subapartado})
                  
                  
                  old_content = self.__get_old_content(soup.find_all('h5', class_='articulo'),
                                                            artDetails,
                                                            soup)
                  
                  pattern = r'\xa0'
                  found = False
                  contenido = []

                  '''
                  result=re.search(r'\bgood\b', 'goodbye')
                  if result:
                     print('asasa')
                  result=re.search(r'\bgood\b', 'goodbye gooood good')
                  if result:
                     print('asasa')
                  result=re.search(r'\bgood\b', 'good_bye gooood')
                  if result:
                     print('asasaas')
                  


                  resulst=re.search(r'(?<!\S)good(?!\S)', 'good bye gooood')
                  if resulst:
                     print('SSSSSSSSSSSS')
                  '''
                  

                  content_=xmlContent.find_all("p", class_=['parrafo','parrafo_2'])
                  for c in content_:
                    text=re.sub(pattern, ' ', c.text)
                    text = text.replace(',',' ')
                    text = text.replace('.', ' ')
                    
                    result=re.findall(ppv, text, flags=re.IGNORECASE)

                    if result:
                      contenido.append(c)

                    

                  if contenido:
                    for c in contenido:
                      for sibling in c.find_next_siblings():
                        if sibling.name=='blockquote':
                          for element in sibling:
                            found = True
                            new_content = new_content + element.text
                        if sibling.name=='p':
                          break
                
                  if found == False:
                    if found == False:
                      new_content = 'NO HE PODIDO RECUPERAR CONTENIDO'
                    '''
                    content_=xmlContent.find_all("p", attrs={'class': 'articulo'})
                    for c in content_:
                      text=re.sub(pattern, ' ', c.text)
                      text = text.replace(',',' ')
                      text = text.replace('.', ' ')
                      
                      result=re.findall(ppv, text, flags=re.IGNORECASE)

                      if result:
                        contenido.append(c)

                    if contenido:
                      
                      for c in contenido:
                        found = True
                        new_content = new_content + c.text
                    ''' 


                  self.__listafinal.append(pd.DataFrame({ 'identificador_item':identificador_item,
                                              'fecha_publicacion':fecha_publicacion,
                                              'url_html_item': url_html_item,
                                              'nombre_departamento':nombre_departamento,
                                              'nombre_epigrafe': nombre_epigrafe,
                                              'nombre_seccion':nombre_seccion,
                                              'titulo_item': titulo_item,
                                              'boe_anterior': boe_referencia,
                                              'link_boe_anterior': link,
                                              'accion': accion,
                                              'entity_type': entity_type,
                                              'entities': entidades,
                                              'entity_detail': artDetails,
                                              'old_content': [old_content],
                                              'new_content': [new_content]}))
                  
                  if found == False:
                    print('-------------')
                    print(identificador_item)
                    print(validador)
                    print('NO SE HA ENCONTRADO CONTENIDO')
                  else:
                    print('-------------')
                    print(identificador_item)
                    print(validador)
                    print(new_content)

                  new_content=''
                  found = False
                  artDetails = []
                  old_content = []

              

              else:
                # Just interested in disposiciones with just 1 number
                numDisps=re.findall(r'[0-9]+', entidades)
                entidades_  = entidades
                if len(numDisps) == 1:
                  try:
                    entidades_ = entidades.replace(numDisps[0], disposcionesDict[numDisps[0]])
                  except:
                    pass
                  dispDetails.append(entidades_)
                else:
                  dispDetails.append('NOT PROCESSED')

                validador = dispDetails[0]
                validadorAux = dispDetails[0]
                content_=xmlContent.find_all("p", class_=['parrafo','parrafo_2'])

                ppv = r'\b'+'({})'.format(validador)+r'\b'
                
                pattern = r'\xa0'
                salir = False
                found = False 
                contenido = []     

                content_=xmlContent.find_all("p", class_=['parrafo','parrafo_2'])
                for c in content_:
                  text=re.sub(pattern, ' ', c.text)
                  text = text.replace(',',' ')
                  text = text.replace('.', ' ')
                    
                  result=re.findall(ppv, text, flags=re.IGNORECASE)

                  if result:
                    contenido.append(c)

                    

                if contenido:
                  for c in contenido:
                    for sibling in c.find_next_siblings():
                      if sibling.name=='blockquote':
                        for element in sibling:
                          found = True
                          new_content = new_content + element.text
                      if sibling.name=='p':
                        break
                
                if found == False:
                  new_content = 'NO HE PODIDO RECUPERAR CONTENIDO'
                  '''
                  content_=xmlContent.find_all("p", attrs={'class': 'articulo'})
                  for c in content_:
                    text=re.sub(pattern, ' ', c.text)
                    text = text.replace(',',' ')
                    text = text.replace('.', ' ')
                      
                    result=re.findall(ppv, text, flags=re.IGNORECASE)

                    if result:
                      contenido.append(c)

                  if contenido:
                    for c in contenido:
                      found=True
                      new_content = new_content + c.text  
                  '''
                self.__listafinal.append(pd.DataFrame({ 'identificador_item':identificador_item,
                          'fecha_publicacion':fecha_publicacion,
                          'url_html_item': url_html_item,
                          'nombre_departamento':nombre_departamento,
                          'nombre_epigrafe': nombre_epigrafe,
                          'nombre_seccion':nombre_seccion,
                          'titulo_item': titulo_item,
                          'boe_anterior': boe_referencia,
                          'link_boe_anterior': link,
                          'accion': accion,
                          'entity_type': entity_type,
                          'entities': entidades,
                          'entity_detail': dispDetails,
                          'old_content': [old_content],
                          'new_content': [new_content]}))
                

                if found == False:
                  print('-------------')
                  print(identificador_item)
                  print(validador)
                  print('NO SE HA ENCONTRADO CONTENIDO')
                else:
                
                  print('-------------')
                  print(identificador_item)
                  print(validador)
                  print(new_content)

                new_content=''
                dispDetails = []
                old_content = []
            

      
    def __main_process(self,identificador_item,
                      fecha_publicacion,
                      url_html_item,
                      nombre_departamento,
                      nombre_epigrafe,
                      nombre_seccion,
                      titulo_item,
                      ant_references,
                      xmlContent):

      paragraphs = xmlContent.find_all('p')

      '''
      #Remove header from the pdf
      pdfContent = re.sub('BOLETÍN OFICIAL DEL ESTADO.*? https://www.boe.es', '', pdfContent, flags=re.DOTALL)
      #Remove line breaks
      pdfContent = re.sub("\n|\r", "", pdfContent)
      '''
      '''
      paragraphs = xmlContent.find_all('p')
      for p in paragraphs:
        result=re.findall('\\b'+'adicional octava'+'\\b', p.text, flags=re.IGNORECASE)
        if result:
          next_elements = p.next_elements
          for idx, next in enumerate(next_elements):
            if idx==2 and next.name == 'blockquote':
              for element in next:
                 print(element.text)
          #print(p.find_next("blockquote"))
      '''
      

      
      artDetails = []
      dispDetails = []
      old_content = ''
      new_content = ''
      contenttt = ''
      content_=''

      ppv = r'\b'+'({})'.format(validador)+r'\b\,|\.'

      disposcionesDict = {'1':'primera','2':'segunda', '3':'tercera', '4':'cuarta', '5':'quinta','6':'sexta','7':'séptima',
                          '8':'octava', '9':'novena', '10':'décima'}

      for reference in ant_references:
        
        #Extract acccion
        accion = reference[0]['accion']
        
        reference_content = []
        texto= reference[0]['texto']
        reference_content.append(texto)

        for content in reference_content:
        # Extract the entities with the trained model
          doc = self.__ner_model(content)
          for word in doc.ents:
            if (word.label_ == 'ART' or word.label_  == 'DISP') and (accion=='MODIFICA' or accion=='AÑADE'):
              boe_referencia = doc.ents[0][0]
              link = 'https://www.boe.es/buscar/doc.php?id=' + str(boe_referencia)
              page = requests.get(link)
              soup = BeautifulSoup(page.content, 'html.parser')

              entity_type = word.label_

              # Get each articulo and disposcion
              entidades = str(word.text).replace("arts. ","")
              entidades = str(entidades).replace("Arts. ","")  
              entidades = str(entidades).replace("art. ","")        
              entidades = str(entidades).replace("Art. ","")  
              entidades = str(entidades).replace("disposición ","")
              entidades = str(entidades).replace("Disposición ","")
              entidades = str(entidades).replace("disposiciones ","") 
              entidades = str(entidades).replace("Disposiciones ","")

              if word.label_ == 'ART':
                # art 1,2 y 3, art 1 y 2
                arts = re.split(',|y', entidades)
                
                for art in arts:

                  x = art.split(".")
                  if len(x) == 1:
                    articulo = x[0].strip()
                    apartado = 0
                    subapartado = 0
                    validador = 'artículo ' + articulo
                  elif len(x) == 2:
                    articulo = x[0].strip()
                    apartado = x[1].strip()
                    subapartado = 0
                    validador = 'apartado ' + apartado + ' del artículo ' + articulo 
                  elif len(x) == 3:
                    articulo = x[0].strip() + '.'
                    apartado = x[1].strip() + '.'
                    subapartado = x[2].strip()
                    validador = 'artículo ' + articulo + apartado + subapartado

                  validador = validador.replace(')','')

                  artDetails.append({'articulo':articulo,
                                  'apartado':apartado,
                                  'subapartado':subapartado})
                  

                  old_content = self.__get_old_content(soup.find_all('h5', class_='articulo'),
                                                            artDetails,
                                                            soup)
                  
                  pattern = r'\xa0'
                  found = False


                  content_=xmlContent.find_all("p", class_=['parrafo','parrafo_2'])
                  for z in content_:
                     result=re.findall(ppv, z.text)
                     if result:
                        pass

                  salir = False
                  for c in content_:
                    #text=re.sub(pattern, ' ', c.text).lower()
                    #if validador in text:
                      #contenttt=c
                    text=re.sub(pattern, ' ', c.text)

                    #regex = re.compile(r'\b' +'artículo 45.I.B'+ r'\b', flags=re.IGNORECASE)

                    result=re.findall(ppv, text)
                    if result:
                      contenttt = c

                    if contenttt != '':
                      print(validador)
                      #print('-------------')
                     
                      for sibling in contenttt.find_next_siblings():
                        if sibling.name=='blockquote':
                          for element in sibling:
                            found = True
                            new_content = new_content + element.text
                        if sibling.name=='p':
                          salir = True
                          break
                    if salir == True:
                       break
                      
                    #print(new_content)
                  if found==False:
                    content_=xmlContent.find_all("p", attrs={'class': 'articulo'})
                    for c in content_:
                      #text=re.sub(pattern, ' ', c.text).lower()
                      #if validador in text:
                      #  contenttt=c
                      #  break
                      text=re.sub(pattern, ' ', c.text)

                      result=re.findall(ppv, text)
                      if result:
                        contenttt = c
                        break

                    if contenttt != '':
                       found = True
                       for sibling in contenttt.find_next_siblings():
                          for element in sibling:
                            new_content = new_content + element.text
   
                  #print(new_content)        
                  print(identificador_item)

                  self.__listafinal.append(pd.DataFrame({ 'identificador_item':identificador_item,
                                                          'fecha_publicacion':fecha_publicacion,
                                                          'url_html_item': url_html_item,
                                                          'nombre_departamento':nombre_departamento,
                                                          'nombre_epigrafe': nombre_epigrafe,
                                                          'nombre_seccion':nombre_seccion,
                                                          'titulo_item': titulo_item,
                                                          'boe_anterior': boe_referencia,
                                                          'link_boe_anterior': link,
                                                          'accion': accion,
                                                          'entity_type': entity_type,
                                                          'entities': entidades,
                                                          'entity_detail': artDetails,
                                                          'old_content': [old_content],
                                                          'new_content': [new_content]}))

    
                  artDetails = []
                  old_content = ''
                  new_content = ''
                  contenttt = ''

              else:

                  # Just interested in disposiciones with just 1 number
                  numDisps=re.findall(r'[0-9]+', entidades)
                  entidades_  = entidades
                  if len(numDisps) == 1:
                    try:
                      entidades_ = entidades.replace(numDisps[0], disposcionesDict[numDisps[0]])
                    except:
                      pass
                    dispDetails.append(entidades_)
                  else:
                    dispDetails.append('NOT PROCESSED')

                  validador = dispDetails[0]
                  content_=xmlContent.find_all("p", class_=['parrafo','parrafo_2'])

                  
                  pattern = r'\xa0'
                  salir = False
                  found = False
                  
                  for c in content_:
                    #text=re.sub(pattern, ' ', c.text).lower()
                    #if validador in text:
                    #  contenttt=c
                    
                    text=re.sub(pattern, ' ', c.text)

                    result=re.findall(ppv, text)
                    if result:
                      contenttt = c
                  
                    if contenttt != '':
                      print(validador)
                      #print('-------------')
                     
                      for sibling in contenttt.find_next_siblings():
                        if sibling.name=='blockquote':
                          for element in sibling:
                            found = True
                            new_content = new_content + element.text
                        if sibling.name=='p':
                          salir = True
                          break
                    if salir == True:
                       break
                    #print(new_content)

                  if found==False:
                    content_=xmlContent.find_all("p", attrs={'class': 'articulo'})
                    for c in content_:
                      #text=re.sub(pattern, ' ', c.text).lower()
                      #if validador in text:
                      #  contenttt=c
                      #  break

                      text=re.sub(pattern, ' ', c.text)

                      result=re.findall(ppv, text)
                      if result:
                        contenttt = c
                        break

                    if contenttt != '':
                       found = True
                       for sibling in contenttt.find_next_siblings():
                          for element in sibling:
                            new_content = new_content + element.text
      

                  print(identificador_item)                  


                  self.__listafinal.append(pd.DataFrame({ 'identificador_item':identificador_item,
                                                          'fecha_publicacion':fecha_publicacion,
                                                          'url_html_item': url_html_item,
                                                          'nombre_departamento':nombre_departamento,
                                                          'nombre_epigrafe': nombre_epigrafe,
                                                          'nombre_seccion':nombre_seccion,
                                                          'titulo_item': titulo_item,
                                                          'boe_anterior': boe_referencia,
                                                          'link_boe_anterior': link,
                                                          'accion': accion,
                                                          'entity_type': entity_type,
                                                          'entities': entidades,
                                                          'entity_detail': dispDetails,
                                                          'old_content': [old_content],
                                                          'new_content': [new_content]
                                                          }))

                  dispDetails = []
                  old_content = ''
                  new_content = ''
                  contenttt = ''
              

    def __get_old_content(self, content,artDetails,soup):
      
      old_content_ = ''

      for c in content:
        for x in artDetails:
          result = re.findall('\\b'+x['articulo']+'\\b', c.text, flags=re.IGNORECASE)
          if result:
            h5 = soup.find('h5',string=c.text)
            for s in h5.find_next_siblings():
              if s.name == 'p':
                  #print(s.get_text(strip=True))
                  old_content_  = old_content_ + s.get_text(strip=True)
                  #old_content_.append(s.get_text(strip=True))
              else:
                  #print('-----------------')
                  break   

      return old_content_

    def __validate_element(self,item,element):
        
        try: 
            return item[element]
        except KeyError:
            return 'NO EXISTE'


    def __get_references(self,url_xml):

        ref_anteriores = []
        ref_posteriores = []

        if url_xml != 'NO EXISTE':

            response = requests.get(url_xml)

            soup = BeautifulSoup(response.content, "xml")

            referencias = soup.find_all('anteriores')

            for ref in referencias:
                elements=ref.find_all('anterior')
                if elements:
                    for element in elements:
                        accion = element.find('palabra').get_text()
                        referencia_boe=element['referencia']
                        text = element.find('texto').get_text()
                        texto = referencia_boe + ' ' + text
                        ref_anteriores.append([{'accion':accion, 'referencia':referencia_boe, 'texto':texto}])


            referencias = soup.find_all('posteriores')

            for ref in referencias:
                elements=ref.find_all('posterior')
                if elements:
                    for element in elements:
                        accion = element.find('palabra').get_text()
                        referencia_boe=element['referencia']
                        text = element.find('texto').get_text()
                        texto = referencia_boe + ' ' + text
                        ref_posteriores.append([{'accion':accion, 'referencia':referencia_boe, 'texto':texto}])


        return ref_anteriores, ref_posteriores







       




