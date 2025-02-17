.PHONY: default dev-install container-build test deploy

default: test

dev-install:
	pip install -r Requirements.txt
	ansible-galaxy collection install -r requirements.yml

container-build:
	docker build -f instances/archlinux.Dockerfile -t docker.sociedadecivil.local/ansible/molecule/archlinux:base .

test: container-build dev-install
	cd roles/cluster_node_base; molecule test

deploy: test
	ansible-playbook initial-config.yml -i ../inventory