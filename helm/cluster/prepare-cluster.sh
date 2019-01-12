#/bin/sh

kubectl create -f rbac-config.yaml
helm init --upgrade --service-account tiller