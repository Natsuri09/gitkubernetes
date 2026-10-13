# CTE412 Practical 6 — Campus Notice Board releases on Kubernetes

**Student number:** 02230137  **Name:** REPLACE WITH YOUR FULL NAME
**Repository:** REPLACE WITH REPOSITORY URL

## Purpose

Deploy the Campus Notice Board API to a local kind cluster, build an
availability monitor, and release new versions with three strategies
(Recreate, RollingUpdate, blue/green) plus a feature flag. For every release the
number of failed requests is **measured** by the monitor, not assumed.
The measured results and analysis are in `report/p06-report.md`; all captured
output is in `evidence/`.

## Software versions

| Software | Version |
| --- | --- |
| Operating system | Windows (commands run in Git Bash) — *fill in build* |
| Docker Desktop / Engine | 4.94.0 / 29.8.2 |
| kind | v0.33.0 |
| kubectl client | v1.37.0 |
| Kubernetes in the cluster | *fill in: `kubectl version` → Server Version* |
| Git | *fill in: `git --version`* |
| Application | Python 3.13 (standard library only), image `python:3.13-alpine` |
| Monitor image | `busybox:1.37` |

## Repository layout

| Path | Contents |
| --- | --- |
| `cluster/kind-cluster.yaml` | 3-node kind cluster, host port 30090 on 127.0.0.1 |
| `app/` | `app.py` and the one `Dockerfile` that builds all three images |
| `manifests/base/` | Namespace, ResourceQuota, LimitRange, availability monitor |
| `manifests/rolling/` | Single Deployment and Services (Tasks 3, 5, 6) |
| `manifests/bluegreen/` | Blue and green Deployments, Services, feature-flag ConfigMap (Tasks 7, 8) |
| `scripts/summarise.sh` | Monitor-log summariser (Task 4) |
| `evidence/` | Captured command output, named `tN-<description>.txt` |
| `report/p06-report.md` | The assessed report |

## Rebuild the final state (end of Task 8) from an empty machine

Run in a bash shell from the repository root (Git Bash on Windows). Docker must
be running. On Git Bash first run `export MSYS_NO_PATHCONV=1`.

### A. One-time: cluster and images

```bash
# 1. Create the cluster (context kind-cte412-02230137 becomes current)
kind create cluster --config cluster/kind-cluster.yaml
kubectl config use-context kind-cte412-02230137

# 2. Create the namespace first and make it the default for this context
kubectl apply -f manifests/base/00-namespace.yaml
kubectl config set-context --current --namespace=nb-02230137

# 3. Build the three images locally and load them into the nodes (no registry)
docker build --build-arg APP_VERSION=1.0.0 -t notice-board:02230137-1.0.0 app/
docker build --build-arg APP_VERSION=1.1.0 -t notice-board:02230137-1.1.0 app/
docker build --build-arg APP_VERSION=1.2.0-broken --build-arg BROKEN=true \
             -t notice-board:02230137-1.2.0-broken app/
kind load docker-image notice-board:02230137-1.0.0 \
                       notice-board:02230137-1.1.0 \
                       notice-board:02230137-1.2.0-broken \
                       --name cte412-02230137
```

### B. Deploy (the part Task 9 repeats after deleting the workloads)

```bash
# 4. Namespace, quota, limit range and the monitor
kubectl apply -f manifests/base/

# 5. Blue, green, flag ConfigMap, production and preview Services
kubectl apply -f manifests/bluegreen/
kubectl rollout status deployment/notice-board-blue
kubectl rollout status deployment/notice-board-green

# 6. Check: production serves green (1.1.0) with the pinned flag on
kubectl get deployments,services,pods,configmaps
curl -s http://127.0.0.1:30090/version
curl -s http://127.0.0.1:30090/notices
```

The manifests in `manifests/rolling/` are **not** part of the final state; they
belong to Tasks 3, 5 and 6 and are replaced by `manifests/bluegreen/` in Task 7.

## Clean-up

```bash
kubectl config set-context --current --namespace=default   # reset the default namespace
kind delete cluster --name cte412-02230137                  # removes the cluster and its context
kind get clusters                                           # must not list cte412-02230137
```
