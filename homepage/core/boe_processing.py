import os
import json
import spacy
import requests
import pandas as pd
import re

from pathlib import Path
import pathlib
from bs4 import BeautifulSoup

class BoeProcessing:
    
    ner_model = spacy.load(str(pathlib.Path(__file__).parent.resolve()) + '/NER_CUSTOM_MODEL/trained_models/output/model-best')

    def __init__(self,departments,sections,boe_extraction_date):
      
      self.__departments = departments  
      self.__boe_extraction_date = boe_extraction_date
      self.__sections = sections

      self.__listaboe = []
      self.__listafinal = []
      self.__idx = 0

      self.__headers = {'Accept': 'application/json',}

      self.__pattern = r'\xa0'
      self.__found = False
      self.__xmlContent = ''
      self.extraction_status = False
      
      self.__disposcionesDict = {'1':'primera','2':'segunda', '3':'tercera', '4':'cuarta', '5':'quinta','6':'sexta','7':'séptima',
                                '8':'octava', '9':'novena', '10':'décima', '11': 'undécima', '12':'doceava', '13':'treceava', '14':'catorceava',
                                '15':'quinceava','16':'dieciseisava', '17':'decimoséptima', '18': 'decimooctava', '19': 'decimonovena', '20': 'vigésima',
                                '21': 'vigésimo primera', '22': 'vigésimo segunda', '23': 'vigésimo tercera', '24': 'vigésimo cuarta', '25': 'vigésimo quinta',
                                '26': 'vigésimo sexta', '27': 'vigésimo séptima', '28': 'vigésimo actava', '29': 'vigésimo novena', '30': 'trigésima',
                                '31': 'trigésima primera', '32':'trigésima segunda', '33': 'trigésima tercera', '34': 'trigésima cuarta', '35':'trigésima quinta',
                                '36': 'trigésima sexta', '37':'trigésima séptima', '38':'trigésima octava', '39':'trigésima novena', '40': 'cuadragésima',
                                '41': 'cuadragésima primera', '42':'cuadragésima segunda', '43': 'cuadragésima tercera', '44': 'cuadragésima cuarta','45':'cuadragésima quinta', 
                                '46': 'cuadragésima sexta', '47': 'cuadragésima séptima','48': 'cuadragésima octava', '49': 'cuadragésima novena', '50': 'quincuagésima',
                                '51': 'quincuagésima primera', '52': 'quincuagésima segunda', '53': 'quincuagésima tercera', '54':'quincuagésima cuarta', '55': 'quincuagésima quinta',
                                '56': 'quincuagésima sexta', '57': 'quincuagésima séptima', '58': 'quincuagésima octava', '59': 'quincuagésima novena', '60': 'sexagésima',
                                '61': 'sexagésima primera', '62': 'sexagésima segunda', '63': 'sexagésima tercera', '64':'sexagésima cuarta', '65':'sexagésima quinta',
                                '66':'sexagésima sexta', '67':'sexagésima séptima', '68':'sexagésima octava', '69':'sexagésima novena', '70': 'septuagésima',
                                '71': 'septuagésima primera', '72': 'septuagésima segunda', '73':'septuagésima tercera', '74':'septuagésima cuarta', '75':'septuagésima quinta',
                                '76': 'septuagésima sexta', '77': 'septuagésima séptima', '78':'septuagésima octava', '79':'septuagésima novena', '80':'octogésima',
                                '81': 'octogésima primera', '82': 'octogésima segunda', '83':'octogésima tercera', '84':'octogésima cuarta', '85':'octogésima quinta',
                                '86': 'octogésima sexta', '87': 'octogésima séptima', '88': 'octogésima octava', '89':'octogésima novena', '90': 'nonagésima',
                                '91':'nonagésima primera', '92':'nonagésima segunda', '93': 'nonagésima tercera', '94':'nonagésima cuarta', '95':'nonagésima quinta',
                                '96':'nonagésima sexta', '97':'nonagésima séptima', '98': 'nonagésima octava', '99':'nonagésima novena', '100': 'centésima',
                                '101': 'centésima primera','102': 'centésima segunda', '103': 'centésima tercera', '104': 'centésima cuarta','105':'centésima qunita'}
      
      '''PRINT LOG'''
      self.__print_log = True

      ''' LIST FOR SAVING LOG INFO'''
      self.__logList = []

      ''' NER MODEL FOR DETECTING ENTITIES OF MY INTERES, SUCH AS ARTICULOS AND DISPOSICIONES '''
      #self.__pwd = os.path.dirname(os.path.realpath(__file__ )) 
      self.__pwd= str(pathlib.Path(__file__).parent.resolve()) 
      print('------ INICIANDO CARGA MODELO CUSTOM NER ------')
      #self.__ner_model = spacy.load(self.__pwd + '/trained_models/output/model-best')
      self.__ner_model = BoeProcessing.ner_model
      print('------ FIN CARGA MODELO CUSTOM NER ------')
      #self.__ner_model = spacy.load(os.path.join(self.__pwd, '/trained_models/output/model-best') )

      self.__boe_extraction()

    def getLog(self):
        return self.__logList

    def get_extraction_status(self):
        return self.extraction_status

    def get_lista_final(self):
        return self.__listafinal

    def __boe_extraction(self):
       
      boe_date = self.__boe_extraction_date
      secciones_list = []
      items_list = []
      
      self.__append_log('------INICIO EXTRACCION-------')

      boe_date_s = boe_date.strftime('%Y%m%d') 
      api_url = "https://boe.es/datosabiertos/api/boe/sumario/"+boe_date_s

      ''' SAVING BOE WEB PAGE NAME'''
      self.__append_log('BOE URL -> ' + api_url)

      self.__folder = self.__pwd + '/BOE_PROCESSED_FILES/'+ boe_date.strftime('%Y%m%d') + '/'
      file_path = self.__folder+boe_date.strftime('%Y%m%d')+'.json'

      '''PATH WHERE THE FILES ARE GENERATED'''
      self.__append_log('Ruta generacion fichero ->' + file_path)

      if Path(file_path).exists(): # CHECK IF FILE IS ALREADY DOWNLOADED -> Example -> does file '20240903.json' exists in BOE_FILES folder?
        self.__append_log('Fichero ' + file_path + ' ya existe. Generacion no necesaria')
        #print('FICHERO ' + file_path + ' YA EXISTE. GENERACION NO ES NECESARIA' )
      else:

        try:
            self.__boe_file_generation(api_url,file_path)
            if self.__listaboe:
                '''GENERATE BOE FILE'''
                file_path = self.__folder + 'boe.xlsx'
                self.__dfboe=pd.concat(self.__listaboe,ignore_index=True,sort=False)
                self.__dfboe.to_excel(file_path,index=False)
                '''GENERATE BOE BREAKDOWN'''
                self.__boe_breakdown()
                if self.__listafinal:
                    file_path = self.__folder + 'final.csv'
                    self.__dfFinal=pd.concat(self.__listafinal,ignore_index=True,sort=False)
                    self.__dfFinal.to_csv(file_path,encoding="utf_8_sig",sep=';',index=False)
            ''' GENERATE LOG FILE '''
            self.__log_file_generation()
            self.extraction_status = True
        except Exception as e:
            print(e)



    def __boe_file_generation(self,api_url,file_path):

        items_list = []
       
        response = requests.get(api_url, headers=self.__headers)
        print(response.status_code)

        if(response.status_code != 200):
            self.__append_log(response.status_code)
            self.__append_log('\n')
        else:
            self.__append_log(response.status_code)
            self.__append_log('\n')

            os.makedirs(self.__folder)

            data = response.content.decode('utf-8')
            with open(file_path, 'w') as outf:
                outf.write(data)
            outf.close()
            
            with open(file_path, "r") as file:
                data = json.load(file)
                
                publicacion=data['data']['sumario']['metadatos']['publicacion']
                fecha_publicacion=data['data']['sumario']['metadatos']['fecha_publicacion']
                identificador = data['data']['sumario']['diario'][0]['sumario_diario']['identificador']
                url_pdf = data['data']['sumario']['diario'][0]['sumario_diario']['url_pdf']['texto']
                secciones = data['data']['sumario']['diario'][0]['seccion']
                
                for seccion in secciones:
                                    
                    codigo_seccion = seccion['codigo']
                    nombre_seccion = seccion['nombre']

                    if nombre_seccion in self.__sections:
                    
                        departamento = seccion['departamento']

                        for info_departamento in departamento:

                            codigo_departamento = info_departamento['codigo']
                            nombre_departamento = info_departamento['nombre']
                            
                            if nombre_departamento in self.__departments:
                            
                                for epigrafe in info_departamento['epigrafe']:
                                
                                    nombre_epigrafe = epigrafe['nombre']

                                    if type(epigrafe['item']) != list:
                                        items_list.append(epigrafe['item'])
                                        items = items_list
                                    else:
                                        items = epigrafe['item']

                                    for item in items:

                                        identificador_item = self.__validate_element(item,'identificador')
                                        control_item = self.__validate_element(item,'control')
                                        titulo_item = self.__validate_element(item,'titulo')
                                        url_pdf_item = self.__validate_element(item,'url_pdf')
                                        url_html_item = self.__validate_element(item,'url_html')
                                        url_xml_item = self.__validate_element(item,'url_xml')

                                        ant_references,post_references=self.__get_references(url_xml_item)

                                        self.__listaboe.append(pd.DataFrame({'publicacion':publicacion,
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
                                        items_list = []
                                        self.__idx+=1

        file.close()


    def __boe_breakdown(self):

    
        for idx, record in enumerate(self.__listaboe):

            xmlItem = record['url_xml_item'][idx]

            response = requests.get(xmlItem, stream=True)
            self.__xmlContent = BeautifulSoup(response.content, "xml")

            referencias_anteriores = record['referencias_anteriores'][idx]
            referencias_posteriores = record['referencias_posteriores'][idx]


            if referencias_anteriores  or referencias_posteriores:

                identificador_item = record['identificador_item']
                fecha_publicacion = record['fecha_publicacion']
                url_html_item = record['url_html_item']
                nombre_departamento = record['nombre_departamento']
                nombre_epigrafe = record['nombre_epigrafe']
                nombre_seccion = record['nombre_seccion']
                titulo_item = record['titulo_item']

                for reference in referencias_anteriores:
                    reference_content = [] 
                    reference_content_aux = [] 
                    accion = reference[0]['accion']
                    texto= reference[0]['texto']
                    reference_content.append(texto)
                    reference_content_aux.append(texto)
                    
                    for content in reference_content:
                        
                        doc = self.__ner_model(content)

                        for word in doc.ents:

                            if ( accion=='MODIFICA' or accion=='AÑADE') and (word.label_ == 'ART' or word.label_  == 'DISP'):

                                for content_aux in reference_content_aux:

                                    doc_aux = self.__ner_model(content_aux)
                                    normativa = ''

                                    for wordaux in doc_aux.ents:
                                        
                                        if wordaux.label_ == 'LEYOR':
                                            normativa = wordaux.text 
                                            break
                                        elif wordaux.label_ == 'LEY':
                                            normativa = wordaux.text
                                            break
                                        elif wordaux.label_ == 'REALDE':
                                            normativa = wordaux.text
                                            break
                                        else:
                                            pass
                                    
                                if normativa == '':
                                    normativa = 'NORMATIVA NO IDENTIFICADA'
                            
                                boe_referencia = str(doc.ents[0][0])
                                link = 'https://www.boe.es/buscar/doc.php?id=' + boe_referencia
                                page = requests.get(link)
                                boeContent = BeautifulSoup(page.content, 'html.parser')
                                entity_type = word.label_

                                '''CLEANING'''
                                entidades = str(word.text).replace("arts. ","")
                                entidades = str(entidades).replace("Arts. ","")  
                                entidades = str(entidades).replace("art. ","")        
                                entidades = str(entidades).replace("Art. ","")  
                                entidades = str(entidades).replace("disposición ","")
                                entidades = str(entidades).replace("Disposición ","")
                                entidades = str(entidades).replace("disposiciones ","") 
                                entidades = str(entidades).replace("Disposiciones ","")

                                if word.label_ == 'ART':
                                    arts = re.split(',|y', entidades)
                                    
                                    for art in arts:
                                        
                                        artDetails,old_content,new_content = self.__art_processing(art,boeContent, normativa,nombre_departamento, nombre_epigrafe, identificador_item)
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
                                                                                'normativa': normativa,
                                                                                'entity_type': entity_type,
                                                                                'entities': entidades,
                                                                                'entity_detail': artDetails,
                                                                                'old_content': [old_content],
                                                                                'new_content': [new_content]}))

                                elif word.label_ == 'DISP':
                                    
                                    dispDetails,old_content,new_content=self.__disp_processing(entidades,boeContent,normativa,nombre_departamento, nombre_epigrafe, identificador_item)     
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
                                                                            'normativa': normativa,
                                                                            'entity_type': entity_type,
                                                                            'entities': entidades,
                                                                            'entity_detail': dispDetails,
                                                                            'old_content': [old_content],
                                                                            'new_content': [new_content]}))        
                                else:
                                    pass
                                     
                                      
            else:
                self.__append_log('-----------------------------------')

                normativa = 'NO HAY AL NO EXISTIR NI REFERENCIAS ANTERIORES NI POSTERIORES'

                df = record['nombre_departamento'].to_frame().T
                for index, row in df.iterrows():
                    nombre_departamento = row.values[0]

                df = record['nombre_epigrafe'].to_frame().T
                for index, row in df.iterrows():
                    nombre_epigrafe = row.values[0]

                df = record['identificador_item'].to_frame().T
                for index, row in df.iterrows():
                    identificador_item = row.values[0]

                line='SIN REFERENCIAS A TRATAR PARA: ' + normativa + ' / ' + nombre_departamento + ' / ' + nombre_epigrafe + ' / '  + identificador_item
                self.__append_log(line) 

        self.__append_log('-----------------------------------') 
        self.__append_log('\n')      
        self.__append_log('PROCESO FINALIZADO SIN ERRORES') 

    def __get_new_content(self,validation):

        '''
            <p class="parrafo_2">Tres. Con efectos de 1 de enero de 2023, la redacción actual de la disposición adicional cuadragésima quinta pasa a ser su primer apartado, añadiéndose un apartado segundo, con la siguiente redacción:</p>
            <blockquote class="sangrado">
            <p class="parrafo_2">«2. Sin perjuicio de las competencias que tiene atribuidas la Inspección de Trabajo y Seguridad Social en relación con la vigilancia en el cumplimiento de la normativa en materia de seguridad social, que incluye la correcta aplicación de las reducciones a que se refiere la Disposición adicional 47.ª, la Tesorería General de la Seguridad Social realizará sus funciones de control en la cotización de estas contribuciones empresariales y de las reducciones en la cotización u otros beneficios que se apliquen las empresas por tales contribuciones, en el marco de sus competencias en materia de gestión y control de la cotización y de la recaudación de las cuotas y demás recursos de financiación del sistema de la Seguridad Social.»</p>
            </blockquote>
            <p class="parrafo_2">Cuatro. Con efectos de 1 de enero de 2023, se añade una nueva disposición adicional cuadragésima séptima, con la siguiente redacción:</p>
            <blockquote class="sangrado">

            <p class="parrafo">Uno. Con efectos de 1 de enero de 2023, se añade una nueva letra k) en el apartado 1 del artículo 71, con la siguiente redacción:</p>
            <blockquote class="sangrado">
            <p class="parrafo_2">«k) Las promotoras de planes de pensiones, en su modalidad de sistema de empleo, en el marco del texto refundido de la Ley de Regulación de Planes y Fondos de Pensiones, aprobado por el Real Decreto Legislativo 1/2002, de 29 de noviembre, y de instrumentos de modalidad de empleo propios de previsión social establecidos por la legislación de las Comunidades Autónomas con competencia exclusiva en materia de mutualidades no integradas en la Seguridad Social facilitarán mensualmente a la Inspección de Trabajo y Seguridad Social y a la Tesorería General de la Seguridad Social la información sobre las contribuciones empresariales satisfechas a dichos planes de pensiones respecto de cada trabajador.»</p>
            </blockquote>

            <p class="parrafo_2">Dos. Con efectos de 1 de enero de 2023, se añade un párrafo final al apartado 3 del artículo 147, con la siguiente redacción:</p>
            <blockquote class="sangrado">
            <p class="parrafo_2">«Las contribuciones empresariales satisfechas a los planes de pensiones, en su modalidad de sistema de empleo, en el marco del texto refundido de la Ley de Regulación de Planes y Fondos de Pensiones, aprobada por el Real Decreto Legislativo 1/2002, de 29 de noviembre, y a instrumentos de modalidad de empleo propios establecidos por la legislación de las Comunidades Autónomas con competencia exclusiva en materia de mutualidades no integradas en la Seguridad Social se deberán comunicar, respecto de cada trabajador, código de cuenta de cotización y período de liquidación a la Tesorería General de la Seguridad Social antes de solicitarse el cálculo de la liquidación de cuotas correspondiente.»</p>
            </blockquote>

         IT LOOKS LIKE, MAINLY, THE CONTENT FOR THE ARTICLES & DISPOSICIONES ARE COMPOSED BY CLASS parrafo OR parrafo_2 AND THE CONTENT IS INSIDE A BLOCKQUOTE
        '''
        contenido = []
        new_content = ''

        possible_articles_and_disps = self.__xmlContent.find_all("p", class_=['parrafo','parrafo_2'])
        for c in possible_articles_and_disps:
            text=re.sub(self.__pattern, ' ', c.text)
            text = text.replace(',',' ')
            text = text.replace('.', ' ')
            
            result=re.findall(validation, text, flags=re.IGNORECASE)

            if result:
                contenido.append(c)

        if contenido:
            for c in contenido:
                for sibling in c.find_next_siblings():
                    if sibling.name=='blockquote':
                        for element in sibling:
                            self.__found = True
                            new_content = new_content + element.text
                    if sibling.name=='p':
                        break

        if self.__found == False:
            '''FURTHER PROCESSING IN CASE OTHER PATTERNS ARE FOUND FOR IDENTIFYING THE ARTICLES'''
            new_content = '\n' + 'NO HE PODIDO RECUPERAR CONTENIDO' + '\n'

        return new_content
                    
    def __disp_processing(self,entidades,boeContent,normativa,nombre_departamento, nombre_epigrafe, identificador_item):
        
        dispDetails = []
        old_content = ''

        '''Just interested in disposiciones with just 1 number'''
        numDisps=re.findall(r'[0-9]+', entidades)
        entidades_  = entidades
        if len(numDisps) == 1:
            try:
                entidades_ = entidades.replace(numDisps[0], self.__disposcionesDict[numDisps[0]])
            except:
                pass
            dispDetails.append(entidades_ + ' ' + normativa)
        else:
            dispDetails.append('NOT PROCESSED' + ' ' + normativa)

        validador = dispDetails[0]
        validation = r"(?<!\S)"+'{}'.format(validador)+r"(?!\S)"

        '''GET THE OLD CONTENT FOR THE DISPOSICONES IS NOT DONE'''
        old_content = normativa + ' ' + 'PENDIENTE PARA LAS DISPOSICIONES'

        new_content = self.__get_new_content(validation)
        new_content = normativa + ' ' + new_content

        df = nombre_departamento.to_frame().T
        for index, row in df.iterrows():
            nombre_departamento = row.values[0]

        df = nombre_epigrafe.to_frame().T
        for index, row in df.iterrows():
            nombre_epigrafe = row.values[0]

        df = identificador_item.to_frame().T
        for index, row in df.iterrows():
            identificador_item = row.values[0]

        self.__append_log('DISPOSICION ' + str(numDisps) + ' -> ' + normativa + ' / ' + nombre_departamento + ' / ' + nombre_epigrafe + ' / ' + identificador_item)
        self.__append_log('-----------------------------------')
        self.__append_log(new_content)

        self.__found = False


        return dispDetails,old_content,new_content

    def __art_processing(self,art,boeContent,normativa,nombre_departamento, nombre_epigrafe, identificador_item):

        artDetails = []
        contenido = []
        old_content = ''

        x = art.split(".")
        if len(x) == 1:
            articulo = x[0].strip()
            apartado = 0
            subapartado = 0
            normativa = normativa
        elif len(x) == 2:
            articulo = x[0].strip()
            apartado = x[1].strip()
            subapartado = 0
            normativa = normativa
        elif len(x) == 3:
            articulo = x[0].strip()
            apartado = x[1].strip()
            subapartado = x[2].strip()
            normativa = normativa

        '''THIS VARIABLE IS USED FOR FINDING THE CORRESPONDING ARTICLE'''
        validador = 'artículo ' + articulo
        validation = r"(?<!\S)"+'{}'.format(validador)+r"(?!\S)"

        artDetails.append({'articulo':articulo,
                        'apartado':apartado,
                        'subapartado':subapartado,
                        'normativa':normativa})
        
        '''GET THE OLD CONTENT FOR THE ARTICLES'''
        old_content = self.__get_old_content(boeContent.find_all('h5', class_='articulo'),artDetails,boeContent)
        old_content = normativa + ' ' + old_content

        new_content = self.__get_new_content(validation)
        new_content = normativa + ' ' + new_content

        df = nombre_departamento.to_frame().T
        for index, row in df.iterrows():
            nombre_departamento = row.values[0]

        df = nombre_epigrafe.to_frame().T
        for index, row in df.iterrows():
            nombre_epigrafe = row.values[0]

        df = identificador_item.to_frame().T
        for index, row in df.iterrows():
            identificador_item = row.values[0]

        self.__append_log('ARTICULO ' + str(art) + ' -> ' + normativa + ' / ' + nombre_departamento + ' / ' + nombre_epigrafe + ' / ' + identificador_item)
        self.__append_log('-----------------------------------')
        self.__append_log(new_content)

        self.__found = False


        return artDetails,old_content,new_content


    def __get_old_content(self, content,artDetails,soup):
        
        old_content_ = ''
        result_found = False

        for c in content:
            if result_found == True:
                break
            for x in artDetails:
                result = re.findall('\\b'+x['articulo']+'\\b', c.text, flags=re.IGNORECASE)
                if result:
                    h5 = soup.find('h5',string=c.text)
                    for s in h5.find_next_siblings():
                        if s.name == 'p':
                            old_content_  = old_content_ + s.get_text(strip=True) + '\n'
                            result_found = True
                        else:
                            break   

        return old_content_



    def __log_file_generation(self):
       
        file_path = self.__folder + 'log.txt'

        with open(file_path, "w", encoding="utf-8") as f:
            for line in self.__logList:
                f.write(line)

        f.close()

        
        
    def __append_log(self,line):
       
       line = str(line) + '\n'
       self.__logList.append(line)
       if self.__print_log:
          print(line)

    def __validate_element(self,item,element):
        return item[element]


    def __get_references(self,url_xml):

        ref_anteriores = []
        ref_posteriores = []

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