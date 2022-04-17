
- [Python based Kubernetes Resource (CPU and RAM) Limits REST Service](#python-based-kubernetes-resource-cpu-and-ram-limits-rest-service)
  - [Quick Start](#quick-start)
  - [Building](#building)
    - [Initial Setup](#initial-setup)
    - [Creating a Python Package](#creating-a-python-package)
  - [Pushing the build to a registry](#pushing-the-build-to-a-registry)
  - [Deployment in Kubernetes](#deployment-in-kubernetes)
    - [Cleanup](#cleanup)

# Python based Kubernetes Resource (CPU and RAM) Limits REST Service

The is a Python application exposing a REST API that simplifies the collection of CPU and RAM Node stats from a Kubernetes cluster. This application is intended to be deployed inside a Kubernetes cluster

This project is referred to in [my blog](https://www.nicc777.com/) with the first reference in the article of [2022-04-16](https://www.nicc777.com/blog/2022/2022-04-16.html).

## Quick Start

Since this application is intended for running in a Kubernetes cluster, and a prebuilt image [is available on Docker Hub](https://hub.docker.com/r/nicc777/pykles), you can deploy this application quickly with the following commands:

```shell
kubectl create namespace pykles

kubectl apply -f https://raw.githubusercontent.com/nicc777/pykles/main/kubernetes_manifests/pykles.yaml -n pykles
```

_**Important**_: The default configuration above uses the equivalent of administrator privileges for the [ServiceAccount](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/).

To deploy the same applications with least privileged access, run the following command:

```shell
kubectl apply -f https://raw.githubusercontent.com/nicc777/pykles/main/kubernetes_manifests/pykles_least_privileged.yaml -n pykles
```

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
NAME                                     READY   STATUS    RESTARTS   AGE
pod/pykles-deployment-6fdc5cfdbb-66mgs   1/1     Running   0          108s

NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/pykles-app-service   ClusterIP   10.43.191.111   <none>        8080/TCP   108s

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/pykles-deployment   1/1     1            1           108s

NAME                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/pykles-deployment-6fdc5cfdbb   1         1         1       108s
```

For more info, try running `kubectl get all -o wide` or for maximum information, try running `kubectl get all -o yaml`

### Cleanup

To delete the deployment, simply run `kubectl delete -f pykles.yaml` (or whatever manifest file was used to create the deployment)

To verify, wait a minute or so and run `kubectl get all`. The output should be something similar to `No resources found in test namespace.`


