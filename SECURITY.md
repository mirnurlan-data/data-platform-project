# Security policy

This repository is a **synthetic, local education project**. Do not import real customer, financial, personal, or production data. It is not a hardened deployment template.

If you find a security issue, avoid publishing exploit details in a public GitHub issue. Use GitHub's private vulnerability reporting feature if enabled for this repository; otherwise contact the maintainer privately using their [GitHub profile](https://github.com/mirnurlan-data).

Supported demo environment: Python 3.10+ and SQLite via Python's standard library. Older revisions, production installations and downstream forks are not covered by any security support SLA.

Security expectations: keep GitHub Actions dependencies reviewed, avoid secrets in commits, run workflows with least-privilege permissions, and use disposable databases only.
