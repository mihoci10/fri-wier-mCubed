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

