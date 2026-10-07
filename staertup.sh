#!/bin/bash

echo "=== LOGOWANIE DO GOOGLE CLOUD ==="
gcloud auth login stubbamariuszgcp@gmail.com

echo "=== USTAWIAM WŁAŚCIWE KONTO ==="
gcloud config set account stubbamariuszgcp@gmail.com

echo "=== USTAWIAM WŁAŚCIWY PROJEKT ==="
gcloud config set project devops-project-510219

echo "=== SPRAWDZAM PROJEKT ==="
gcloud config get-value project

echo "=== LISTA KLASTRÓW W PROJEKCIE ==="
gcloud container clusters list

echo "=== POBIERAM POŚWIADCZENIA KLASTRA ==="
gcloud container clusters get-credentials demo-cluster --zone europe-central2-a

echo "=== SPRAWDZAM DOSTĘP DO KLASTRA ==="
kubectl get nodes

echo "=== GOTOWE ==="

