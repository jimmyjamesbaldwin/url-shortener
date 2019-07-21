# url-shortener
A reasonably simple solution for the common 'design a tinyurl-like url shortener service' interview question. Currently a work in progress, also quite untested.

<img src="https://azurecomcdn.azureedge.net/mediahandler/acomblog/media/Default/blog/fd7cc81b-8f38-472b-b7b8-6c8da0057a89.png" width="100"><img src="https://i0.wp.com/codeblog.dotsandbrackets.com/wp-content/uploads/2016/10/compose-logo.jpg?resize=262%2C285" width="100"><img src="https://qph.fs.quoracdn.net/main-qimg-28cadbd02699c25a88e5c78d73c7babc" width="100">



![screenshot](https://i.imgur.com/qsERkqI.png)

## Features
- Local development with docker-compose
- Live deployment with Azure Kubernetes Service (AKS)
- Python flask API shortening service, memcached cache and mysql database

## Things that might be nice in future :
- half decent unit tests and testing config for sqlite
- some metrics, maybe prometheus integration
- a helm chart for deployment

### Local Development
#### Docker-compose
To spin up the code locally, simply run:
```
docker-compose up
```

#### Create virtualenv and install local dependencies
```
virtualenv venv
source venv/bin/activate
pip install -r url-shortener/url_shortener/src/requirements.txt
```

### Live Deployment to AKS
Below are some instructions for spinning up the project on AKS, based on the files in the ./kube directory. These commands will create a container registry, upload container images to acr, create a kubernetes cluster and deploy the application. 

#### Create Azure Container Registry and service principal
```
# create a resource group to use for the demo
az acr create --name myregistry123 --resource-group myResourceGroup --sku Basic

# grab subscription ID from this command
az acr list 

# create a service principal with 'Contributor' role for ACR. Note the appId and password given in the response
az ad sp create-for-rbac --name acr-sp --role contributor --scopes /subscriptions/<subscription_id>/resourceGroups/myResourceGroup
```

#### Upload container images to ACR
These steps can't be completed from Azure Cloud Shell as it doesn't have docker installed:
```
# build images locally
cd url-shortener
docker-compose build

# tag images with ACR registry details
docker tag urlshortener_url_shortener myregistry123.azurecr.io/james/urlshortener_url_shortener

# login to acr registry
docker login --username <service_principal_appid> --password <service_principal_password>

# push to ACR
docker push myregistry123.azurecr.io/james/urlshortener_url_shortener
```

#### Provision Kubernetes Cluster
```
# create aks cluster. this will take a min...
az aks create \
   --resource-group myResourceGroup \
   --name myAKSCluster \
   --node-count 1 \
   --service-principal <service_principal_appid> \
   --client-secret <service_principal_password> \
   --generate-ssh-keys

# download credentials and configure kube cli
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```

#### Deploy application
```
# deploy!
cd url-shortener/kube
kubectl apply -f db-deployment.yaml
kubectl apply -f memcached-deployment.yaml
kubectl apply -f url-shortener-deployment.yaml

# get IP of external load balancer
kubectl get svc url-shortener -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

##### If you want to view the Kubernetes dashboard...
```
kubectl create clusterrolebinding kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
az aks browse --resource-group myResourceGroup --name myAKSCluster
```
