# yum install -y git
# git clone https://github.com/ivango812/hasker.git

HOST=127.0.0.1:8000
PYTHON=python3.6
MANAGE=cd .. && $(PYTHON) manage.py

all: prepare install

prepare:
	yum install -y https://centos7.iuscommunity.org/ius-release.rpm
	yum install -y python36u python36u-devel python36u-pip
	pip3.6 install --upgrade pip
	pip install django==2.1.5

install:
	pip install -r requirements.txt
	$(MANAGE) migrate
	$(MANAGE) loaddata fixtures.json

test:
	$(MANAGE) test

run:
	$(MANAGE) runserver $(HOST)
