# Badapple2-API
API code for Badapple2. Currently in beta. 

The `compose-production.yml` file will spin up the Badapple2 website (DB, API, and UI). 

## Requirements

* Docker
* Docker Compose

## Setup (Development)
1. Copy `.env.example` to `.env` (in the `/app` folder)
2. Edit the `.env` credentials as needed
3. Run `docker-compose --env-file ./app/.env -f compose-development.yml up --build`
    * Note: Depending on your version of docker, you may instead want to use: `docker compose --env-file ./app/.env -f compose-development.yml up --build`
4. The API should now be accessible from `localhost:8000`
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
4. Run `docker-compose -f compose-production.yml up --build -d`

