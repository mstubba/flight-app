TAG=v1.1.2
docker build -t mariuszstubba/flight-app:$TAG .
docker push mariuszstubba/flight-app:$TAG

kubectl apply -f k8s/flask.yaml
kubectl rollout status deployment/flask-app