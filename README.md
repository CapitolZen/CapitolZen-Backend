# CapitolZen / Application Backend

## Information
This Django app is used for the generic multi-tenant SaaS solution used by the primary frontend application.

## Branch Details
| Branch  | Used For |
| ------------- | ------------- |
| master  | MVP?  |


## Local Development

**Getting the Environment**
You'll need to get the env file from someone who has it. (See Matt Wisner) Rename it to '.env' and add it to your repo locally.

**Starting w/ Docker For Mac**
```bash
docker-compose build
docker-compose up
```

### Working With
You'll need to get the env file from someone who has it. (See Matt Wisner)

You can run management commands using:
```bash
docker-compose run pycharm python manage.py
```

**Running Tests**
```bash
docker-compose run pycharm sh utilities/tests.sh
```

**Rebuilding Search Index**:
```bash
docker-compose run pycharm python manage.py search_index --rebuild
```

**Connecting To DB w/ CLI**
```bash
docker-compose run postgres psql -h postgres -U capitolzen
```

**Code Quality**
```bash
docker-compose run pycharm coverage run --source='/app' manage.py test --failfast
docker-compose run pycharm flake8 /app/capitolzen. --ignore C901
```

**Email Stuff**
```bash
npm install -g mjml
```

```bash
cd capitolzen/templates/emails
mjml mjml/welcome.mjml -o content/welcome.html
```

**Connecting To Pycharm**
For docker-machine instructions see: https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/docs/pycharm/configuration.rst
From there the instructions for setting up the python remote interrupters are the same for both docker for mac and docker-machine.

### Start From Scratch
The following process should be used if you're having difficulty getting the
application up and running due to docker errors. These commands will remove
all of the containers, images, and volumes that docker has created.
```bash
docker stop $(docker ps -a -q)
docker rm --force $(docker ps -a -q)
docker rmi --force $(docker images -a -q)
docker volume rm --force $(docker volume ls -f dangling=true -q)
```

### References
- [PyCharm Setup] https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/docs/pycharm/configuration.rst
- [Docker Docs] https://docs.docker.com/
- [Docker Compose] https://docs.docker.com/compose/overview/

