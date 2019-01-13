HOST=127.0.0.1:8001
MANAGE=python manage.py

.PHONY: pipenv
pipenv:
	pipenv shell

help:
	$(MANAGE) help

deps:
	pip install -r requirements.txt

run:
	$(MANAGE) runserver $(HOST)

exit:
	exit


