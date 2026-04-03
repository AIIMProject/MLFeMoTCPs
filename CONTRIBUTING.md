# Contributing & Branching Strategy

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Active development — may be incomplete or experimental |
| `notebooks_publish` | **Publication branch** — the clean, reproducible version of the pipeline accompanying the paper |
| `feature/<name>` or `fix/<name>` | Working branches for individual notebook cleanup or fixes; merged into `notebooks_publish` once verified |
| `nomad_integration` | *(future)* Wiring notebooks 00–02 to the NOMAD data repository |

## Workflow for publication cleanup

1. Create a working branch from `notebooks_publish`:
   ```bash
   git checkout notebooks_publish
   git checkout -b feature/cleanup-notebook-07
   ```
2. Make changes and verify that the refactored notebook still runs correctly and produces the expected outputs.
3. Merge back into `notebooks_publish` once verified:
   ```bash
   git checkout notebooks_publish
   git merge --no-ff feature/cleanup-notebook-07
   git branch -d feature/cleanup-notebook-07
   ```
4. Never force-push to `notebooks_publish` after tagging `v1.0`.

## Branch rules

- `notebooks_publish` is the integration target for all publication-ready changes.
- `main` stays available for ongoing development and experimentation — no cleanup requirements.
- Each merge into `notebooks_publish` should be a clean, descriptive commit or merge commit.

## Release

The Zenodo archive is created from a GitHub Release tagged `v1.0` on the `notebooks_publish` branch.

## Syncing with Aberdeen

The repository is also maintained at `aberdeen:/home/users/fortimtb/storage/DatasetsML_2.0`.  
To sync:

```bash
# Push from local machine
git push origin notebooks_publish

# On Aberdeen
cd /home/users/fortimtb/storage/DatasetsML_2.0
git fetch origin
git checkout notebooks_publish
git pull origin notebooks_publish
```
