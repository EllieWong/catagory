## Item Catalog Readme ##

- This is a flask application that will start a webserver
serving at Localhost:5001
- Data is persisted in a SqLite database hosted on the local machine
- Users can login via OAuth2.0 using Google Api, and perform CRUD operations
via the frontend being delivered by flask. 


## How to Start Application ##

1. Via Command Line, traverse to the root directory of this git repo 
4. In SSH, execute 'cd catalog'
5. Run 'python models.py'
6. Run 'python initDB.py'
7. Run 'python views.py'
8. Visit localhost:5001 on a web browser on same machine to visit Item Catalog


## Design ##

- The backend is sqlite, the database is mapped to ORM using SQLAlchemy
- Flask is the webserver framework
- It follows the PEP8 style guide.
- All raw_data for playing around is in raw_data folder in JSON form
