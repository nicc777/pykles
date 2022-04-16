
- [Python based Kubernetes Resource (CPU and RAM) Limits REST Service](#python-based-kubernetes-resource-cpu-and-ram-limits-rest-service)
  - [Building](#building)
    - [Initial Setup](#initial-setup)
    - [Creating a Python Package](#creating-a-python-package)
  - [Pushing the build to a registry](#pushing-the-build-to-a-registry)
  - [Deployment in Kubernetes](#deployment-in-kubernetes)
    - [Cleanup](#cleanup)

# Python based Kubernetes Resource (CPU and RAM) Limits REST Service

The is a Python application exposing a REST API that simplifies the collection of CPU and RAM Node stats from a Kubernetes cluster. This application is intended to be deployed inside a Kubernetes cluster

This project is referred to in [my blog](https://www.nicc777.com/) with the first reference in the article of [2022-04-16](https://www.nicc777.com/blog/2022/2022-04-16.html).

## Building

### Initial Setup

Run:

```
pip3 install --upgrade setuptools 
pip3 install build
```

### Creating a Python Package

Run:

```shell
python3 -m build
```

This will create the Python package.

Next, build the docker image:

```shell
docker build --no-cache -t pykles .
```

## Pushing the build to a registry

Create the following environment variables:

* `REGISTRY_URL` - contains the ECR or similar Docker container registry URL
* `VERSION_TAG` - The version number, for example `1.0`
* `APP_TAG` - The application tag, for example `node_explorer_rest`
* `LOCAL_IMAGE_ID` - The ID of the local container image to use as reference

Get the latest image:

```shell
docker image list
```

Update the environment variable `LOCAL_IMAGE_ID`

Ensure a login token for ECR is still valid:

```shell
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $REGISTRY_URL
```

Then tag and push:

```shell
docker tag $LOCAL_IMAGE_ID $REGISTRY_URL/$APP_TAG\:latest
docker tag $LOCAL_IMAGE_ID $REGISTRY_URL/$APP_TAG\:$VERSION_TAG
docker push $REGISTRY_URL/$APP_TAG\:latest
docker push $REGISTRY_URL/$APP_TAG\:$VERSION_TAG
```

## Deployment in Kubernetes

The manifests are all located in the `kubernetes_manifests/` directory of this project and commands will be run from within this directory.

To deploy the application, run the following command:

```shell
kubectl apply -f pykles.yaml
```

After a minute or so, when the command `kubectl get all` is run, expect the following output:

```text
TODO...

```

For more info, try running `kubectl get all -o wide` or for maximum information, try running `kubectl get all -o yaml`

### Cleanup

To delete the deployment, simply run `kubectl delete -f pykles.yaml` (or whatever manifest file was used to create the deployment)

To verify, wait a minute or so and run `kubectl get all`. The output should be something similar to `No resources found in test namespace.`


