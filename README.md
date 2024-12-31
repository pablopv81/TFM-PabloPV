# Data extraction from BOE (Boletín Oficial del Estado), which is the Spanish Gazzete for legislation, about labour topics affecting Spanish payroll
## Overview
This project focuses on data extraction from the following State Departments and BOE sections that, overtime, have been in charge of releasing the legislation affecting labour topics linked with Spanish Payroll.

<ins>State Departments</ins><br/>
Jefatura del Estado<br/>
Ministerio de Trabajo y Asuntos Sociales<br/>
Ministerio de Trabajo y Seguridad Social<br/>
Ministerio de Trabajo y Economía Social<br/>
Ministerio de Empleo y Seguridad Social<br/>
Ministerio de Inclusión, Seguridad Social y Migraciones<br/>

<ins>BOE Sections</ins><br/>
I. Disposiciones generales<br/>
III. Otras disposiciones<br/>

The final objective is trying to provide the last situation of an article or provision. Next figure shows the modifications done over article 80.4 by BOE-A-2024-6086 (https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-6086). Highlighted in grey what it has not changed. In yellow the new content for paragraph 4<br/>.
![2024-10-30 162612 (002)](https://github.com/user-attachments/assets/b27f4213-390e-4896-aa66-ad061644f4d0)
<br/>
To be considered that some decisions have been taken under my criteria. It is just recovered information, once the filter for departments and sections is applied, when the action is 'MODIFICACION' or 'AÑADE', and just when there are previous or future references. Then, it is possible that some important information can be skipped and not recovered.For that reason, it would be extremly helpfull count on the assistance of an expert on BOE, in order to find the correct extraction process, with the correct criterias to be applied, and data base modeling.

## Table of Contents
1. [Project Description](#project-description)
2. [Motivation](#motivation)
3. [Methodology](#methodology)
4. [Project Structure](#project-structure)
5. [Results](#results)
6. [Future Work](#future-work)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

## Project Description
This project extracts BOE data from a specific field (labour topics affecting Spanish payroll), applies a NER custom model for detecting entites, such as laws, dates, BOE id, articles, provisions and royal decrees (see next figure, where it has been highlighted the elements that should be detected by the NER model).  <br/>
![image](https://github.com/user-attachments/assets/25924145-9e7e-49d3-a936-a708d3df1fd2)

Per each article or provision detected, an entity linking is applied in order to obtain the original content and the new content of the article or provision. Finally, once the information is collected, it is save within a graph data base Neo4j (you can find a short demo here https://www.youtube.com/watch?v=3K3vLK8h-90). <br/>

Additionally, a basic web application has been developed (see next figure) in order to follow up the data extraction process. <br/>
![Captura de pantalla 2024-12-31 120909](https://github.com/user-attachments/assets/17937f2d-ad45-4ee8-8dd8-bcbf87339bbe)

## Motivation
Several motivations are behind this project. One of them is trying to provide a better understanding of BOE content, with specific focus on Spanish payroll topics.

## Methodology

CRISP-DM methodology, which includes the following phases:<br/>

Business Understanding<br/>
Data Understanding<br/>
Data Preparation<br/>
Modeling<br/>
Evaluation<br/>
Deployment<br/>

## Project Structure

TFM-PabloPV/<br/>
-------homepage/<br/>
----------core/<br/>
--------------(Python files for data extraction & data base management)<br/> 
--------------(Django necessary elements)<br/> 
--------------NER_Custom_Model/<br/>
-----------------(Jupyter notebook for training the NER model and other necessary files ) <br/> 
-------webapp/<br/>
----------(Django settings and static files) <br/> 
-------.gitattributes<br/> 
-------.gitignore<br/> 
-------LICENSE<br/> 
-------README.md <br/> 
-------manage.py (for starting the Django server) <br/> 

## Results

The project provides a new vision a much clear understanding of BOE. The NER model has performed well when it comes identifying the entities of interest. However, some errors, related with the entity linking, have been detected. You can check these videos showing 2 main errores detected during the evaluation. <br/> 
https://www.youtube.com/watch?v=mQJ_v8_Gc80 <br/> 
https://www.youtube.com/watch?v=MC2_Gxzo9RQ <br/> 

The final objective has been covered partially. With the current modeling of the data base it can be difficult to get the last situation of an article or provision.

## Future Work
In order to obtain the last version of an article or provision, it can be necessary to study a new modeling for the data base, where each article or provision is linked with the paragraphs that make it up.<br/>
Train the NER model in a different way, where each article or provision is detected as an unique element. Currenty the model detects articles as a group (see next figure), which causes a split process during the extraction.<br/>
![2024-12-29 165550 (002)](https://github.com/user-attachments/assets/070e728c-e9cd-4a29-a03d-1b7c46123039)
Improvement of the entity linking process.<br/>
Check the feasibility of building an Q&A application, where the user asks a question with natural language, this language is translated to a Cypher query, and a response is provided based on the information contained in the data base.<br/>
As a big and challenging project, expand this application to other regions, as I think other countries/regions might have their own gazzete for releasing legislation.<br/>

## Contributing
Contributions are more than welcome!
## License
This project is licensed under the MIT License - see the LICENSE file for details.
## Acknowledgments
    Universitat Oberta de Catalunya (UOC)
    Nadjet Bouayad-Agha (Tutor)
    Josep Anton Mir Tutusaus (Professor)
