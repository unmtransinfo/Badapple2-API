# Badapple2-API
API code for Badapple2. Currently in beta. 

The `compose-production.yml` file will spin up the Badapple2 website (DB, API, and UI). 

## Requirements

* Docker
* Docker Compose

## Setup (Development)
1. Install the badapple_classic and badapple2 DBs by following the instructions [here](https://github.com/unmtransinfo/Badapple2/blob/main/README.md)
2. Copy `.env.example` to `.env` (in the `/app` folder)
3. Edit the `.env` credentials as needed
4. Run `docker-compose --env-file ./app/.env -f compose-development.yml up --build`
    * Note: Depending on your version of docker, you may instead want to use: `docker compose --env-file ./app/.env -f compose-development.yml up --build`
5. The API should now be accessible from `localhost:8000`
   * A full set of Swagger documentation can be found at http://localhost:8000/apidocs

## Setup (Production on Chiltepin)
1. Copy `production_env.example` to `.env`
2. Fill in/edit the `.env` credentials as needed
3. Update apache2 config:
    * Create a new file for apache2 config: `/etc/apache2/sites-available/badapple2api.conf`
    * Add the following line to `/etc/apache2/apache2.conf`: 
        ```
        Include /etc/apache2/sites-available/badapple2api.conf
        ```
    * Update the apache2 virtual config file: `/etc/apache2/sites-enabled/000-default.conf`
    * Run config check: `sudo apachectl configtest`
    * (If config check passed) reload apache: `sudo systemctl reload apache2`
4. (If server was previously up): `docker-compose -f compose-production.yml down`
5. Run `docker-compose -f compose-production.yml up --build -d`

### Production notes
* If you are noticing some UI changes not showing up you may need to clear your browser cache
* You will likely need to clear the docker cache if you've made changes to the DB
* If you've pushed changes to the UI and docker is still using the cached github context, try changing UI build context to either a specific branch or commit. See https://docs.docker.com/reference/compose-file/build/#attributes for more info.
* In extreme cases you may need to go in and manually override the DB. I still do not know what the reason is for this, but there are times when even after updating the .pgdump file the DB state will not be changed (even after clearing cache etc). These steps are what I've found work:
1. Connect to the DB container: `docker exec -it <container_id> sh`
2. (If necessary) re-download the .pgdump file. For example:
```
wget --no-cache -O /tmp/badapple_classic.pgdump https://unmtid-dbs.net/download/Badapple2/badapple_classic.pgdump
```
3. Change to postgres user: `sudo -i -u postgres`
4. Run pg_restore on the DB with the .pgdump file: 
```
pg_restore --clean -O -x -v -d ${DB_NAME} <PATH_TO_PGDUMP_FILE>
```
5. Grant privileges back to DB_USER:
```
psql -p ${DB_PORT} -d ${DB_NAME} -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${DB_USER}" 
psql -p ${DB_PORT} -d ${DB_NAME} -c "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER}"
psql -p ${DB_PORT} -d ${DB_NAME} -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ${DB_USER}"
```
6. Exit DB container.


## Acknowledgment
Originally forked from the CFChemAPI repo:
[https://github.com/unmtransinfo/CFChemAPI](https://github.com/unmtransinfo/CFChemAPI)
