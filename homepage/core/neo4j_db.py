
from neo4j import GraphDatabase,RoutingControl
from yfiles_jupyter_graphs import GraphWidget
from networkx import florentine_families_graph

class Neo4jDB:

    def __init__(self):
        self.__uri = 'neo4j+s://21e8a473.databases.neo4j.io'
        self.__user = 'neo4j'
        self.__pwd = 'L2nKM9w6uzDqpUjMJcammBMFbB3baKu4baurry6V_1A'
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

        """
        (:Departament)-[:RELEASES]->(:Boe)
        (:Boe)-[:BY]->(:Date)
        (:Boe)-[:BELONGS]->(:Epigrafe)
        """


    def delete_record(self,date):


        pass

    def get_record(self,date,department_name,entity):


        p1='MATCH P1=(D:Department)-[:RELEASES]-(B:Boe), '
        p2='P2=(B:Boe)-[:BY]-(F:Date), '
        p3='P3=(B:Boe)-[:BELONGS]-(EPI:Epigrafe), '
        p4='P4=(B:Boe)-[:MODIFIES|:ADDS]-(ENT:Entitydetail), '
        p5='P5=(ENT:Entitydetail)-[:FROM]-(NORM:Normativa), '
        p6='P6=(ENT:Entitydetail)-[:`OLD_CONTENT`]-(OLD:Oldcontent), '
        p7='P7=(ENT:Entitydetail)-[:`NEW_CONTENT`]-(NEW:Newcontent) '
        p8= "WHERE F.date = $date AND D.department_name = $department_name AND ENT.entity CONTAINS $entity"
        p9 = ' RETURN P1,P2,P3,P4,P5,P6,P7'

        query = p1+p2+p3+p4+p5+p6+p7+p8+p9
        print(query)
        
        records, summary,keys= self.__driver.execute_query(query,
            date=date, department_name=department_name, entity=entity,database_="neo4j", routing_=RoutingControl.READ,
        )
        '''
        for record in records:
            print(record)
        '''

        self.__driver.close()

        return self.__generate_graph(self.__driver,query,date,department_name,entity)
        '''
            MATCH P1=(D:Department)-[:RELEASES]-(B:Boe), 
            P2=(B:Boe)-[:BY]-(F:Date), 
            P3=(B:Boe)-[:BELONGS]-(EPI:Epigrafe), 
            P4=(B:Boe)-[:MODIFIES]-(ENT:Entitydetail),
            P5=(ENT:Entitydetail)-[:`OLD_CONTENT`]-(OLD:Oldcontent),
            P6=(ENT:Entitydetail)-[:`NEW_CONTENT`]-(NEW:Newcontent)
            WHERE F.date = '20240327' 
            RETURN P1,P2,P3,P4,P5,P6
        '''
    def add_record(self,lista):

        nombre_departamento =''
        identificador_item = ''
        fecha_publicacion = ''
        nombre_epigrafe = ''
        accion = ''
        entity_type =''
        entitydetail =''
        old_content = ''
        new_content = ''
        normativa = ''
        old_boe = ''
        link_boe_anterior = ''
        link_boe_actual = ''

        for record in lista:
            '''DEPARTAMENTO QUE LIBERA EL BOE'''
            df = record['nombre_departamento'].to_frame().T
            for index, row in df.iterrows():
                nombre_departamento = row.values[0]
            '''IDENTIFICADOR DEL BOE'''
            df = record['identificador_item'].to_frame().T
            for index, row in df.iterrows():
                identificador_item= row.values[0]
            '''FECHA PUBLICACION'''
            df = record['fecha_publicacion'].to_frame().T
            for index, row in df.iterrows():
                fecha_publicacion= row.values[0]
            '''EPIGRAFE'''
            df = record['nombre_epigrafe'].to_frame().T
            for index, row in df.iterrows():
                nombre_epigrafe= row.values[0]
            '''ACCION'''
            df = record['accion'].to_frame().T
            for index, row in df.iterrows():
                accion = row.values[0]
            '''ENTITY TYPE'''
            df = record['entity_type'].to_frame().T
            for index, row in df.iterrows():
                entity_type = row.values[0]
            '''ENTITY DETAILS'''
            df = record['entity_detail'].to_frame().T
            for index, row in df.iterrows():
                if entity_type == 'ART':
                    entitydetail = 'ARTICULO ' + str(row.values[0]['articulo']) + '.' + str(row.values[0]['apartado']) + '.' + str(row.values[0]['subapartado']) + '.' + str(row.values[0]['normativa'])
                else:
                    entitydetail = row.values[0].upper()
            '''OLD CONTENT'''
            df = record['old_content'].to_frame().T
            for index, row in df.iterrows():
                old_content = row.values[0]
            '''NEW CONTENT'''
            df = record['new_content'].to_frame().T
            for index, row in df.iterrows():
                new_content = row.values[0]
            '''NORMATIVA'''
            df = record['normativa'].to_frame().T
            for index, row in df.iterrows():
                normativa = row.values[0]
            '''BOE ANTERIOR'''
            df = record['boe_anterior'].to_frame().T
            for index, row in df.iterrows():
                old_boe = row.values[0]
            '''LINK BOE ANTERIOR'''
            df = record['link_boe_anterior'].to_frame().T
            for index, row in df.iterrows():
                link_boe_anterior = row.values[0]
            '''LINK BOE ACTUAL'''
            df = record['url_html_item'].to_frame().T
            for index, row in df.iterrows():
                link_boe_actual = row.values[0]            

            p1="MERGE (department:Department{department_name:$department}) "
            p2="MERGE (epigrafe:Epigrafe{epigrafe_name:$epigrafe}) "
            p3="MERGE (date:Date{date:$date}) "
            p4="MERGE (boe:Boe{boe_id:$boe}) "
            p5="MERGE (entitydetail:Entitydetail{entity:$entitydetail}) "
            p6="MERGE (oldboe:Oldboe{oldboe:$old_boe}) "
            p7="SET entitydetail.oldcontent =$old_content "
            p8="SET entitydetail.oldcontent_url =$link_boe_anterior "
            p9="SET entitydetail.newcontent =$new_content "
            p10="SET entitydetail.newcontent_url =$link_boe_actual "
            p11="MERGE (normativa:Normativa{normativa_desc:$normativa}) "
            p12="MERGE (department)-[:EPIGRAPH]->(epigrafe)"
            p13="MERGE (department)-[:RELEASES]->(boe)"
            p14="MERGE (boe)-[:TOPIC]->(epigrafe)"
            p15="MERGE (boe)-[:BY]->(date)"
            p16="MERGE (entitydetail)-[:FROM]->(normativa)"
            p17="MERGE (entitydetail)-[:INCLUDED]->(oldboe)"
            if accion == 'MODIFICA':
                p18="MERGE (boe)-[:MODIFIES]->(entitydetail)"
            elif accion == 'AÑADE':
                p18="MERGE (boe)-[:ADDS]->(entitydetail)"



            query = p1+p2+p3+p4+p5+p6+p7+p8+p9+p10+p11+p12+p13+p14+p15+p16+p17+p18

            self.__driver.execute_query(query,
                department=nombre_departamento, 
                epigrafe=nombre_epigrafe,
                date=fecha_publicacion,
                boe=identificador_item,
                entitydetail=entitydetail, 
                old_boe = old_boe,
                old_content = old_content,
                link_boe_anterior = link_boe_anterior,
                new_content = new_content,
                link_boe_actual = link_boe_actual,
                normativa = normativa,
                database_="neo4j",
            )

            self.__driver.close()
            '''
            p1="MERGE (department:Department{department_name:$department}) "
            p2="MERGE (boe:Boe{boe_id:$boe}) "
            p3="MERGE (date:Date{date:$date}) "
            p4="MERGE (epigrafe:Epigrafe{epigrafe_name:$epigrafe}) "
            p5="MERGE (normativa:Normativa{normativa_desc:$normativa}) "
            p6="MERGE (oldboe:Oldboe{oldboe:$old_boe}) "
            p7="MERGE (oldcontent:Oldcontent{oldcontent:$old_content}) " 
            p8="SET oldcontent.url =$link_boe_anterior "
            p9="MERGE (entitydetail:Entitydetail{entity:$entitydetail}) "
            p10="MERGE (newcontent:Newcontent{newcontent:$new_content}) " 
            p11="SET newcontent.url =$link_boe_actual "
            p12="MERGE (department)-[:RELEASES]->(boe)"
            p13="MERGE (boe)-[:BY]->(date)"
            p14="MERGE (boe)-[:BELONGS]->(epigrafe)"
            p15="MERGE (entitydetail)-[:FROM]->(normativa)" 
            p16="MERGE (entitydetail)-[:OLD_CONTENT]->(oldcontent)"
            p17="MERGE (oldcontent)-[:INCLUDED]->(oldboe)"
            p18="MERGE (entitydetail)-[:NEW_CONTENT]->(newcontent)"
            if accion == 'MODIFICA':
                p19="MERGE (boe)-[:MODIFIES]->(entitydetail)"
            elif accion == 'AÑADE':
                p19="MERGE (boe)-[:ADDS]->(entitydetail)"
            

            query = p1+p2+p3+p4+p5+p6+p7+p8+p9+p10+p11+p12+p13+p14+p15+p16+p17+p18+p19

            self.__driver.execute_query(query,
                department=nombre_departamento, 
                boe=identificador_item, 
                date=fecha_publicacion, 
                epigrafe=nombre_epigrafe, 
                normativa = normativa,
                entitydetail=entitydetail,
                old_content = old_content,
                link_boe_anterior = link_boe_anterior,
                old_boe = old_boe,
                new_content = new_content,
                link_boe_actual = link_boe_actual,
                database_="neo4j",
            )

            self.__driver.close()

            '''


    def __generate_graph(self,driver,query,date,department_name,entity):

        with driver.session(database="neo4j") as session:
            graph=session.run(query,date=date,department_name=department_name,entity=entity,routing_=RoutingControl.READ).graph()

        w=GraphWidget(graph=graph)
        w.directed = False
        w.set_graph_layout("hierarchic")

        return w


        