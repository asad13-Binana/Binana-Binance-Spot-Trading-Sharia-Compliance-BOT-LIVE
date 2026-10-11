# October 12 LIVE maintenance candidate

This change fixes two maintenance defects independently reproduced from the audit. No LIVE deployment, exchange access, orders or trading-state change is included.

1. `deploy/backup_state.sh` now excludes the rotating `runtime/db_backups` subtree when selecting authoritative SQLite databases for online snapshots. The regression executes the script's actual `find` expression against a temporary tree containing current and rotating database copies.
2. Shell and Python API preflight now default `SHARIA_AUTO_SOURCE_DISCOVERY_ENABLED` to false. Manual registry operation does not unexpectedly require provider keys. Explicit discovery still requires its provider credentials.

Twenty-eight focused tests passed locally, including backup selection, manual provider defaults and existing related preflight tests. Full GitHub checks remain the merge gate. No secrets are committed.

LIVE retains its existing positive 24-hour price-change eligibility rule. Testnet's recovered NFI owner is a different, Testnet-only runtime; neither that owner nor its release evidence is copied into LIVE. A mismatch between these policies is not proof that either policy should be changed.
