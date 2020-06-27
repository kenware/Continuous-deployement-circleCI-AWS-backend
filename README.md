# favorite-things-api
This is an application that allows the user to track their favorite things

[![CircleCI](https://circleci.com/gh/kenware/favorite-things/tree/staging.svg?style=svg)](https://circleci.com/gh/kenware/favorite-things/tree/staging)
[![Maintainability](https://api.codeclimate.com/v1/badges/f8673a9f430135c62efb/maintainability)](https://codeclimate.com/github/kenware/favorite-things-api/maintainability)
[![Coverage Status](https://coveralls.io/repos/github/kenware/favorite-things-api/badge.svg?branch=staging)](https://coveralls.io/github/kenware/favorite-things-api?branch=staging)

* Base Api: http://ec2-34-221-201-174.us-west-2.compute.amazonaws.com/api/v1/
* view [Live App on AWS](http://ec2-34-221-201-174.us-west-2.compute.amazonaws.com/)
## Installation Guide and Django Setup
* check that python3 is installed
    ```bash
    python3 -V
    ```
* Install Postgres database

* Clone this project
    ```bash
    git clone https://github.com/kenware/favorite-things.git
    ```
* Enter project root directory
    ```bash
    cd apifavorite-things
    ```
* install virtual env in your terminal at the project root
    ```bash
    pip3 install virtualenv
    ```
* create virtualenv
    ```bash
    virtualenv env
    ```
* In the root directory, open `env/bin/activate` file and add the environmental variable at the bottom of the `activate` file accordingto the sample bellow:
    ```python
    export DATABASE_URL=<database_url>
    export SECRETE=<your secrete key>
    ```
* Inside the `deactivate` block of code in the `env/bin/activate` file add:
    ```python
    unset DATABASE_URL
    unset SECRETE
    ```
* Activate virtualenv 
    ```bass
    source env/bin/activate
    ```
* Install packages
    ```bash
    pip3 install -r requirements.txt
    ```
* Run test
    ```bash
    python3 manage.py test
    ```
* Migrate tables to postgres database
    ```bash
    python3 manage.py migrate
    ```

* Start the application
    ```bash
    python3 manage.py runserver
    ```
## Installation Guide and VueJs Setup
* in the root of the project
    ```bash
    cd client
    ```
* check that Nodejs or npm is installed
    ```bash
    node -V
    ```
* Install dependency
    ```bash
    npm install
    ```
* Start development server
    ```bash
    npm run serve
    ```
## Auto-linting with pylint, es-lint, pylint-django and autopep8
* This project follows Pep8 style guide.
* You can enable pylint on your code editor for python
* Es-lint for javascript with air-bnb style guide
* To auto fix javascript linting errors, run
    ```bash
    cd favorite_app/client

    npm run lint
    ```
* To show linting error in python, run this command
    ```bash
    pylint --load-plugins pylint_django favorite_app/
    ```
* To auto fix all linting errors in django, run
   ```bash
    autopep8 --in-place --aggressive --aggressive favorite_app/*.py
   ```

## Documentation
* This API is fully documented using openApi. The schema file if found in the root directory of this project named `openapi-shema.yml`
* To generate a new schema, run the command below
```
./manage.py generateschema > openapi-schema.yml
```

## AWS EC2 Deployment
* The deployment sript for this project is found in the root directory with a file named `deployment_script.sh`.
* Ensure you have setup AWS account and have launched an instance in the ubuntu machine with security groups, vpc etc.
* ssh into the instance and run the following commands
```bash
    git clone https://github.com/kenware/favorite-things.git
```
```bash
    chmod +x deployment_script.sh
```
```bash
    bash deployment_script.sh
```