# Project Description
This project contains our implemented web crawler from Assignment 1. 
- Source code of the crawler is located in the _src_ folder with classes _main.py_, which is the main file to run, _crawler.py_ which controls the whole webcrawling, extraction and queries to database, _extraction.py_ where the actual extraction happens, _database.py_ where different queries are written and file _utils.py_ which contains utility functions.
- _db\_link.txt_ file contains a link to the crawldb databse dump (without images) custom file on MS OneDrive
- _report.pdf_ file contains our written report of this Assignment

# Crawler setup and run
1. Install Python
2. In the _Assignment1_ folder, run command `pip install -r requirements.txt` to install required libraries
3. Go to _src_ folder and run command `python main.py` or just run _main.py_ file if you're using an IDE


# Local Database and Docker Container Initialization

1. Go to empty folder, create folders "init-scripts" and "pgdata".
2. Copy initialization script "database.sql" from folder "Database Scripts" into folder "init-scripts".
3. Open Powershell and go to location where folders "init-scripts" and "pgdata" are located.
4. Copy, paste and run the following command: 
`docker run --name postgresql-wier -e POSTGRES_PASSWORD=crawling -e POSTGRES_USER=mCubed -v $PWD/pgdata:/var/lib/postgresql/data -v $PWD/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2`
where "postgresql-wier" is the name of the container, "mCubed" is the name of the user and database, "crawling" is the password for databse and "5432" is the port through which we connect to database.
5. After command has been processed and container and database created, you can connect to databse using the following command:
`docker exec -it postgresql-wier psql -U mCubed`
or by using a database manager like DBeaver (eases the management of database). 

- You can check the logs using the following command:
`docker logs -f postgresql-wier`
- DBeaver usage: Go to "New Database Connection" (Ctrl + Shift + N), select PostgreSQL, leave the defaults, but change Database and Username fields to "mCubed" and Password field to "crawling", then Test Connection and Finish.

