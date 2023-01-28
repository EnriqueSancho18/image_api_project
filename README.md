# image_api_project
Creación de una aplicación apificada basada en microservicios.

En este proyecto se ha creado una aplicación basada en microservicios, utilizando la tecnología Docker para ejecutar cada microservicio en un entorno reproducible.

La aplicación permite subir fotos, las cuales se etiquetan automáticamente y se almacenan en una carpeta además de crear una base de datos donde existe toda esta información (paths a imágenes y etiquetas asignadas). Esta información será utilizada para permitir también buscar imágenes por una etiqueta concreta.

Esta apliación consta de los siguientes microservicios:

 - API: implementada en Flask y servida mediante waitress. 
 - Base de datos: se utiliza una base de datos MySQL 8.0.
