# docker run -it --rm --publish=127.0.0.1:8000:8000 centos
# yum install -y git
# yum install -y make
# cd ~
# git clone https://github.com/ivango812/hasker.git
# cd ./hasker/deployment
# yum install -y git make && cd ~ && git clone https://github.com/ivango812/hasker.git && cd ./hasker/deployment

HOST=0.0.0.0:8000
PYTHON=python3.6
MANAGE=$(PYTHON) ../manage.py

all: prepare install createsuperuser test

prepare:
	yum install -y https://centos7.iuscommunity.org/ius-release.rpm
	yum install -y python36u python36u-devel python36u-pip
	pip3.6 install --upgrade pip
	pip install django==2.1.5

install:
	pip install -r requirements.txt
	$(MANAGE) migrate
	$(MANAGE) loaddata fixtures.json

createsuperuser:
	echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'adminadmin')" | $(MANAGE) shell

test:
	$(MANAGE) test

run:
	$(MANAGE) runserver $(HOST)
