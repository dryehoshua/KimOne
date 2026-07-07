# IGNIS Clients

This folder documents how IGNIS separates financial memory by client.

The portable live registry is outside the repo, inside BIFROST memory:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS/clients/client_registry.json
```

The first active client is:

```text
sr_eli
```

Before any portfolio operation, resolve the client and read the manifest:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS/clients/sr_eli/client_manifest.json
```

Future clients must be added to the registry and must have their own manifest,
ledger events, funding events, positions, snapshots and reporting rules.

Do not store one client's portfolio in another client's folder. Do not use Sr.
Eli as a fallback for missing client context.
