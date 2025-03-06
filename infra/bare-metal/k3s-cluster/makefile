.PHONY: default dev-install container-build test deploy

default: test

dev-install:
	pip install -r requirements.txt
	ansible-galaxy collection install -r requirements.yml

container-build:
	docker pull archlinux:base
	docker build -f instances/archlinux.Dockerfile -t docker.sociedadecivil.local/ansible/molecule/archlinux:base .

test: container-build dev-install
	docker network create molecule_network || true
	molecule test

deploy: test
	ansible-playbook playbook.yml -i ../inventory
