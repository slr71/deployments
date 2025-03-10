## Deleting longhorn
```bash
$ kubectl delete ValidatingWebhookConfiguration longhorn-webhook-validator
$ kubectl delete MutatingWebhookConfiguration longhorn-webhook-mutator
$ for i in (kubectl -n longhorn-system get daemonsets -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete daemonsets $i; end
$ for i in (kubectl -n longhorn-system get deployments -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete deployments $i; end
$ for i in (kubectl -n longhorn-system get configmaps -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete configmaps $i --force; end
$ for i in (kubectl -n longhorn-system get secrets -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete secrets $i; end
$ for i in (kubectl -n longhorn-system get serviceaccounts -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete serviceaccounts $i; end
$ for i in (kubectl -n longhorn-system get poddisruptionbudgets.policy -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete poddisruptionbudgets.policy $i; end
$ for i in (kubectl -n longhorn-system get settings.longhorn.io -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete settings.longhorn.io $i --force; end
$ for i in (kubectl -n longhorn-system get events -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete events $i --force; end
$ for i in (kubectl -n longhorn-system get lease.coordination.k8s.io -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete lease.coordination.k8s.io $i; end
$ for i in (kubectl -n longhorn-system get backuptarget.longhorn.io -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete backuptarget.longhorn.io $i; end
$ for i in (kubectl -n longhorn-system get instancemanager.longhorn.io -o custom-columns=:.metadata.name --no-headers); kubectl -n longhorn-system delete instancemanager.longhorn.io $i; end
$ for crd in (kubectl get crd -o custom-columns=:.metadata.name --no-headers | grep longhorn); kubectl -n longhorn-system delete $crd --all; kubectl delete crd/$crd; end
$ kubectl delete namespace longhorn-system
```

## Installing OpenEBS

```bash
helm install openebs --namespace openebs openebs/openebs --set engines.replicated.mayastor.enabled=false --create-namespace
```
