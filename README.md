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
├── homepage/<br/>
│-----|--NER_Custom_Model<br/>
│---------|--(Jupyter notebook for training the NER model and other necessary files ) <br/> 
├── webapp/<br/>  

