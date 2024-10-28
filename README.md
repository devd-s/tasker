# tasker

## Steps I followed

1. I have created a yaml file for the creating the different resources for K8s cluster in single file for backend and also attaching screenshots.

2. I have created a kind cluster using 

´´´
kind create cluster --name ton --image kindest/node:v1.24.0 --config <(cat <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF
)
´´´

3. Then using this command to create the deployment 'kubectl apply -f FOLDER_NAME/coomponent.yaml 

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api-ingress
spec:
  rules:
  - host: ton.example.com  # Use your domain or set up a local host for testing
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-api
            port:
              number: 80
EOF

and for hpa 'kubectl autoscale deployment backend --cpu-percent=70 --min=3 --max=10' can be scaled like this but there is already a kind named HPA is mentioned in deploy.yaml


5. Security contexts can be mentioned based on the need and also other security aspects which include like capabilities etc. can be added.

6. Few things I have kept commented in yaml to show that these things are also necessary depending upon case to case but for the simplicity , I have for now commented them. 

7. Assumption related to Db is done for which I have added another readme inside postgres folder.

## To create helm chart for an app 

1. Command to create the chart : helm create desired-name-of-chart
2. Customize based on the needs like image repository resources and so on.
3. To install 'helm install desird-app-name ./desired-name-of-chart'
4. To upgrade 'helm upgrade desird-app-name ./desired-name-of-chart'

#To add products in api

```
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","price":99.99,"stock":100}'
{"id":10,"name":"Test Product","price":99.99,"stock":100}
```

# To see products you have added only once you are port forwarding  
curl http://localhost:8000/products/ or http://localhost:8000/products/
