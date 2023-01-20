
- [Python based Kubernetes Resource (CPU and RAM) Limits REST Service](#python-based-kubernetes-resource-cpu-and-ram-limits-rest-service)
  - [Quick Start](#quick-start)
    - [Ingress](#ingress)
  - [Building](#building)
  - [Pushing the build to a registry](#pushing-the-build-to-a-registry)
- [Testing](#testing)

# Python based Kubernetes Resource (CPU and RAM) Limits REST Service

The is a Python application exposing a REST API that simplifies the collection of CPU and RAM Node stats from a Kubernetes cluster. This application is intended to be deployed inside a Kubernetes cluster

> If you intend to use this project, you also have to install the [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server) in your target cluster.

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

### Ingress

Only expose the API service to the outside world if you use the *least privileged* configuration shown above.

Below is an example manifest that was tested with [Traefik Proxy](https://traefik.io/traefik/) acting as Ingress Controller:

```json
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pykles-ingress
  namespace: pykles
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.ingress.kubernetes.io/router.middlewares: pykles-pykles-stripprefix@kubernetescrd
spec:
  rules:
    - host: ingress.saf-ci-sandbox.eu-central-1.aws.int.kn
      http:
        paths:
          - path: /pykles
            pathType: Prefix
            backend:
              service:
                name:  pykles-app-service
                port:
                  number: 8099
---
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: pykles-stripprefix
  namespace: pykles
spec:
  stripPrefix:
    prefixes:
    - /pykles
    forceSlash: false
```

## Building

The Python application is build using Docker and can be done with the command below:

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

# Testing

TODO

