# AIED Prototype

## Development
Ensure you have Docker installed and run the following commands  
`docker build -t aied-app .`  
`docker run -p 8501:8501 aied-app`  

## AWS Deployment
### Cloud9
1. Pull latest updates from Github repository
2. Login to ECR. `aws ecr get-login-password | docker login --username AWS --password-stdin <AWS account number>.dkr.ecr.ap-southeast-1.amazonaws.com`
3. Build application image. `docker build -t aied-app .`
4. `docker tag <image ID> <AWS account number>.dkr.ecr.ap-southeast-1.amazonaws.com/<ECR repository name>:<tag name>`
5. `docker push <AWS account number>.dkr.ecr.ap-southeast-1.amazonaws.com/<ECR repository name>:<tag name>`

### Elastic Container Service
In the existing Cluster, stop the currently running task. This will deploy the latest image. Thats's it.
