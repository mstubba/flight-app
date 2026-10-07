helm upgrade --install my-ingress-nginx ingress-nginx/ingress-nginx \
  --version 4.15.1 -f k8s/ingress-nginx-values.yaml