#!/usr/bin/env sh

KUBEMASTER_ADDR='192.168.1.111'

scp root@${KUBEMASTER_ADDR}:/etc/rancher/k3s/k3s.yaml ~/.kube/sociedade-civil.yaml

kubectl --kubeconfig ~/.kube/sociedade-civil.yaml config rename-context default sociedade-civil

kubectl --kubeconfig ~/.kube/sociedade-civil.yaml config set-cluster default --server=https://${KUBEMASTER_ADDR}:6443

export KUBECONFIG=${KUBECONFIG}:${HOME}/.kube/sociedade-civil.yaml

echo 'KUBECONFIG=${KUBECONFIG}:${HOME}/.kube/sociedade-civil.yaml' >> ~/.zshrc

