.PHONY: default dev-install container-build test deploy

default: test

dev-install:
	pip install -r ../requirements.txt
	ansible-galaxy collection install -r meta/requirements.yml

container-build:
	docker build -f instances/archlinux.Dockerfile -t docker.sociedadecivil.local/ansible/molecule/archlinux:base .

test: container-build dev-install
	cd roles/cluster_node_base; molecule test

deploy: test
	ansible-playbook playbook.yml -i ../inventory
