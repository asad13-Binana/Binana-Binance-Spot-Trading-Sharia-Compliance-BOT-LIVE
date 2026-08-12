# BINANA Oracle Deployment Hardening Report — LIVE Package — 13 August 2026

## Release and review status

This is a **source-review package**, not a deployment, LIVE promotion, or
production approval. Publication in Git does not mean it has been deployed,
connected to real credentials, promoted, or validated on Oracle.

| Field | Value |
|---|---|
| Repository package | BINANA Binance Spot LIVE-capable package |
| Baseline branch | `origin/main` |
| Baseline and local HEAD | `4bd568e08e6bb8a5bbd8d73881d6090b7eda7aa3` |
| Local working branch | `local/oracle-hardening-v2-20260813` |
| Release label | `V10.3-LOCAL-SHARIA-2026-08-10A` |
| Package mode | `live` |
| Safe deployed default | `EXECUTION_MODE=simulation`, `BINANCE_TESTNET=true` |
| Target | Separate OCI A1 Flex VM, Ubuntu 24.04 ARM64, 1 OCPU, 6 GiB RAM, ~50 GiB boot volume, 4 GiB swap |
| Oracle state | Not deployed; not host-validated; not soaked |
| LIVE state | Prohibited |

## Scope and protected boundary

The change is infrastructure-only: host bootstrap, Docker/Compose hardening,
artifact deployment, monitoring, logging, backup/restore, operational identity,
diagnostics, CI controls, tests and documentation. No strategy indicator,
entry/exit condition, risk/position-size calculation, execution decision,
order lifecycle, Sharia rule/approval policy, package interlock, or LIVE evidence
gate was changed. Freqtrade remains signal-only and the execution sidecar
remains the only Binance order owner.

The LIVE package still defaults to simulation. Installing it does not unlock
LIVE. Existing release-hash, strategy, Sharia, TestNet/Oracle and signed LIVE
evidence gates remain mandatory and unchanged.

## Confirmed six-service architecture

The Compose project contains `universe`, `sharia-egress-proxy`,
`sharia-screener`, `freqtrade`, `execution-sidecar` and `telegram-broker`.
No service publishes a host port. Control traffic uses an internal network;
Sharia screening uses an internal-only network and governed egress proxy;
public exchange/provider access uses a separate runtime egress network.

The read-only monitor is a loopback systemd service, not a container. It has no
trading env, Docker socket, Docker group or sudo. LIVE and TestNet use separate
VM identities, monitor files, logs and instance IDs even though the code remains
paired.

## Security findings and fixes

| Severity | Finding | Resolution |
|---|---|---|
| High | Docker-group deployment access is root-equivalent. | Deployment, bot and monitoring identities are not Docker-group members. Only a fixed root-owned wrapper can install an approved artifact. |
| High | Sourcing `.env` permits shell command execution. | Root-owned `0600` configuration is parsed strictly as literal data; malformed records, unsupported keys, duplicate keys, insecure owner/mode, symlinks and open-file identity changes fail closed. |
| High | Artifact transfer and invocation alone did not provide independent host approval. | The archive must match a separately stored root-owned approved SHA-256. CI cannot write that approval. The wrapper re-hashes the artifact after copying it into a root-only stage. |
| High | Deployment pause/reconcile files were plain JSON but the protected sidecar requires HMAC envelopes. | The installer now signs `deploy-installer` commands with the command key and current release hash. The protected verifier is unchanged. |
| High | Legacy and new Compose/path identities could overlap. | Active resources use `binana-freqtrade-v101`. Bootstrap rejects an active legacy `binance-freqtrade-v101` release/stack; migration is explicit and backup-first. |
| High | Critical disk pressure could leave new entries armed. | At 90% usage the root disk guard records critical status and queues an authenticated pause-new-entries command. Exchange-native protection is not cancelled. |
| Medium | Root script path/UID overrides and symlinks could redirect privileged mutation. | Fixed app, persistent, secret, inbox, lock, backup, monitor and account boundaries are validated before use. |
| Medium | Existing swap was not fully proved safe. | Existing swap must be a root:root `0600` regular non-symlink file with a real swap signature; fstab updates are idempotent. |
| Medium | Service-active time status did not establish acceptable signed-request accuracy. | Bootstrap waits up to 60 seconds for NTP synchronisation, requires Chrony tracking and fails above 100 ms absolute last offset. |
| Medium | Disk/log growth and deployment capacity needed explicit bounds. | Docker logs are 10 MiB × 3, journald is bounded, application/audit retention remains controlled, deployment checks free space, and the periodic guard reports warning/critical thresholds. |
| Medium | Backup consistency and restore-member safety needed stronger controls. | Python's SQLite online backup API, integrity checks, no links/devices/special files, validated SHA-256 paths/checksums, root-only retention and non-mutating restore validation were added. Secrets are excluded. |
| Medium | Monitoring and unit names could collide with another bot. | Unique BINANA Compose, paths, systemd units, locks, logs and port collision checks were added; 8090 remains configurable and loopback-only. |
| Medium | SSH changes could cause lockout or follow a malicious target. | Key/owner/mode checks, symlink rejection, atomic write, `sshd -t`, rollback and post-validation reload were added. |

## Users, secrets and host controls

- Hostname: `binana-live-tokyo`.
- Identity: `BOT_PRODUCT=BINANA`, `BOT_ENVIRONMENT=LIVE`, configurable default
  `BOT_INSTANCE_ID=BINANA-LIVE-TYO-01`.
- `binanabot`: no-login service account and writable-state owner; no Docker group.
- `botmon`: monitor-only service account; no trading secrets, Docker socket, sudo or Docker group.
- Deployment account: owns only the artifact inbox and may invoke only the narrow deployment wrapper through sudo.
- Trading/provider/Telegram secrets: root:root `0600` at `/etc/binana-freqtrade-v101/.env` only.
- Monitoring token/optional report bot: separate root:botmon `0640` LIVE monitor file.

Bootstrap requires Ubuntu 24.04, ARM64 or explicitly supported AMD64, Python
3.12, ≥5 GiB physical RAM, ≥35 GiB free disk, valid package mode, official
Docker CE/Compose and synchronized Chrony. A 1 GiB E2 micro is rejected.

## Docker, network and OCI hardening

- Docker CE comes from Docker's official signed Ubuntu repository; no
  convenience script or `docker.io` fallback.
- Daemon settings: live-restore, bounded JSON logs, no userland proxy.
- A persistent `DOCKER-USER` guard blocks new external container ingress and
  container access to OCI metadata TCP/80 without blocking OCI link-local NTP,
  DNS or volume services on their own ports.
- Every service has a memory/PID bound, dropped capabilities,
  `no-new-privileges`, health check, restart policy and bounded logs.
- Read-only roots/tmpfs/non-root users are used where compatible. Freqtrade's
  minimum writable image behaviour is preserved pending a real container run.
- Docker's default seccomp profile remains. No custom seccomp/AppArmor profile
  is claimed without observed ARM64 runtime evidence.
- OCI NSG/Security List guidance exposes SSH/22 only from the operator CIDR.
  Freqtrade, monitoring, sidecar, Sharia, database and Docker ports remain private.
- IMDSv2-only is recommended; containers are blocked from metadata TCP/80.

## Time, memory, updates and logging

- Chrony uses OCI `169.254.169.254`, bounded sync, active tracking and a 100 ms offset limit.
- Four GiB swap headroom, root:root `0600`, real swap signature, no duplicate fstab record, `vm.swappiness=10`.
- Ubuntu security updates remain automatic; automatic reboot is disabled.
- Docker updates are manual, exact-version selected and cannot automatically cross a major version.
- Docker/journal/application/audit log growth is bounded without deleting required reconciliation evidence.

## Backup, restore and rollback

The root timer backs up application state, SQLite databases, audit evidence and
release metadata to `/var/backups/binana-freqtrade-v101`. It excludes plaintext
secrets and all links/devices/special files. SQLite copies are online and
integrity-checked; a validated `SHA256SUMS` covers regular files.

`deploy/restore_validate.sh` verifies root containment, timestamp naming,
member types, checksum paths/checksums and database integrity without changing
the running state.

Automatic deployment rollback restores the prior immutable release, checks all
six old containers, reinstalls matching monitoring and leaves entries paused.
An unhealthy prior release is reported critical. Manual rollback requires a
maintenance window, pause, reconciliation, fresh backup, an existing release
beneath `/opt/binana-freqtrade-v101/releases`, atomic `current` switch, health
check, monitor reinstall and `oracle_validate.sh`. LIVE must remain disabled.

## CI and release-security decision

No permanent self-hosted runner is installed on the trading VM. GitHub-hosted
CI builds/verifies an immutable artifact. LIVE deployment is manual
`workflow_dispatch` and additionally requires the protected enable variable.
Even then, CI can only transfer and invoke the wrapper; it cannot approve the
archive digest, read the root env or enable LIVE execution.

Branch protection, a real CODEOWNER, required protected-environment reviewers,
deployment branch restrictions and retained signed provenance remain owner-side
GitHub configuration. Manifest verification, protected fingerprints, supply-
chain checks, secret scanning, deployment lock, immutable directories, atomic
switch and verified rollback remain in the artifact transaction.

## Exact local changed-file inventory

Modified:

- `.env.example`; `.github/workflows/ci.yml`; `ARCHITECTURE.md`; `README.md`
- `deploy/install_artifact.sh`; `deploy/install_monitoring.sh`; `deploy/oracle_setup.sh`; `deploy/verify_release.sh`
- `docker-compose.yml`; `scripts/healthcheck.sh`; `services/telegram_broker/bot.py`
- `docs/GITHUB_ORACLE_DEPLOYMENT.md`; `docs/GITHUB_RELEASE_AND_ROLLBACK_GUIDE.md`; `docs/ORACLE_DEPLOYMENT_GUIDE.md`; `docs/SECURITY_AND_SECRETS_GUIDE.md`; `docs/SHARIA_LOCAL_SCREENING.md`
- `monitoring/.env.monitor.live.example`; `monitoring/.env.monitor.testnet.example`; `monitoring/INSTALL.md`
- `monitoring/api/app.py`; `monitoring/api/configuration.py`; `monitoring/control.py`; `monitoring/snapshot.py`; `monitoring/tests/test_monitoring.py`
- `tests/test_sharia_egress_proxy.py`
- generated `docs/audit/FILE_REVIEW_LEDGER.csv`; `docs/audit/FUNCTION_CALLBACK_LEDGER.csv`; `docs/audit/TEST_EVIDENCE_LEDGER.csv`; `RELEASE_MANIFEST.json`; `RELEASE_SHA256.txt`

Added:

- `ORACLE_SETUP_GUIDE.md`; `ORACLE_DEPLOYMENT_HARDENING_REPORT_2026-08-13.md`; `ORACLE_HARDENING_V2_CHANGES_2026-08-13.txt`
- `deploy/lib/secure_env.sh`; `deploy/binana-deploy-wrapper.sh`; `deploy/binana-approve-release.sh`
- `deploy/oracle_validate.sh`; `deploy/docker_firewall.sh`; `deploy/disk_guard.sh`; `deploy/backup_state.sh`; `deploy/restore_validate.sh`; `deploy/harden_ssh.sh`; `deploy/update_docker.sh`
- `monitoring/systemd/binana-disk-guard.service`; `monitoring/systemd/binana-disk-guard.timer`
- `monitoring/systemd/binana-monitor-live.service`; `monitoring/systemd/binana-monitor-testnet.service`
- `monitoring/systemd/binana-monitor-report-live.service`; `monitoring/systemd/binana-monitor-report-live.timer`
- `monitoring/systemd/binana-monitor-report-testnet.service`; `monitoring/systemd/binana-monitor-report-testnet.timer`
- `monitoring/systemd/binana-monitor-snapshot.service`; `monitoring/systemd/binana-monitor-snapshot.timer`
- `monitoring/systemd/binana-state-backup.service`; `monitoring/systemd/binana-state-backup.timer`
- `tests/test_oracle_hardening_v2.py`

Removed/replaced:

- Eight legacy `monitoring/systemd/binance-bot-monitor-*` service/timer files,
  replaced by the collision-free BINANA units listed above.

## Protected-file evidence

| Protected item | Baseline SHA-256 | Local result |
|---|---|---|
| `freqtrade/user_data/strategies/IctSmcStrategy.py` | `9f6bafc78c8cd0d9b9cbde615ddce89e304ab09738584b88d05bfdf92ff4e830` | unchanged — PASS |
| `legacy_core/binance_bot_V4.9.16_ALL_IN_ONE.py` | `70b1d67cc0092b5b8db4a68b343cf893641bde1aae580e9ef51e2adec1062459` | unchanged — PASS |
| `services/common/sharia_v19.py` | `5eb9fd5338d80fcaf0d39bb3f4935a75b57dd91136c72a83a7551b659b04d865` | unchanged — PASS |
| V19.1 controller JSON | `07106bb8bfc1924d8d0c6f61ced4e0c51c2ac2054988423f42c1fd67f3b2ba78` | unchanged — PASS |
| Complete frozen set | 41 files inventoried | every non-empty protected file pinned by the hardening regression test — PASS |

## Validation classification

### Executed and passed locally

- Focused monitoring/Oracle hardening suite: 69 passed and 49 subtests passed.
- Complete repository unittest suite after final audit-ledger generation: PASS.
- All deployment/library/operational shell scripts parse with Bash `-n`.
- Python compilation/import, secret scan, manifest, audit-ledger parity,
  deployment supply chain, JSON/YAML, protected hashes, legacy self-tests,
  workflow graph and release gate: PASS.
- Git whitespace/error check: PASS.

A local full-suite pass detected a temporary porting corruption in this LIVE
Telegram module (a truncation marker and encoding damage). It was restored to
byte-identical parity with the verified TestNet counterpart before the final
suite and is not present in this handoff. The monitoring tests emit one
non-failing Starlette/httpx deprecation warning.

### Statically verified

- Ubuntu 24.04/ARM64 and official Docker CE installer branches.
- Compose network/resource/privilege structure and no public application ports.
- systemd service/timer pairing and hardening directives.
- Hosted CI, manual LIVE workflow and owner-digest separation.
- OCI NSG, IMDSv2, NTP and maintenance guidance.

### Unavailable on this Windows audit host

- Docker Engine/Compose config using the actual engine, image pull/build and six-container execution.
- Installed-host `systemd-analyze verify`, Linux ownership/mode enforcement and iptables/DOCKER-USER execution.
- `shellcheck`; Bash `-n` and repository static tests passed, but shellcheck remains external.

### Requires the real Oracle host

- Fresh Ubuntu 24.04 A1 install, Docker/Compose/ARM64 image build and reboot persistence.
- Chrony tracking/offset under OCI; OCI NSG/IMDS/firewall/listening-socket proof.
- Ten real Binance HTTPS DNS/TCP/TLS/TTFB/total samples from the actual region.
- Authenticated Telegram and configured CoinGecko/CMC checks.
- This LIVE package must remain simulation-only; authenticated Binance TestNet
  lifecycle evidence belongs to the paired TestNet package and must precede any LIVE review.
- Docker/container/VM restart, network/DNS/provider interruption, disk critical pause,
  OOM, backup, staged restore, rollback and invalid artifact drills.
- Minimum 72-hour initial Oracle soak and the repository's longer qualification soak.

## Three QA passes

1. **Functional:** host, artifact, six-service, monitoring, backup and rollback paths were traced; local gates passed. Oracle execution remains pending.
2. **Adversarial security:** compromised deployment account/CI, malicious env, symlink/path redirection, artifact substitution, Docker privilege, exposed ports, secret leakage, bad rollback, disk exhaustion, OOM and legacy collision were challenged. Unsigned deployment-control and privileged-path/backup issues were found and fixed.
3. **Regression:** protected hashes are unchanged; LIVE remains simulation-safe by default; Freqtrade is signal-only; order ownership, risk, execution and Sharia policy are unchanged. The temporary LIVE copy corruption was caught, repaired to paired-file parity and re-tested.

## Residual risks and external work

- Infrastructure hardening does not establish strategy profitability or financial edge.
- No static/local test proves exchange lifecycle correctness, Oracle capacity, regional latency or long-run recovery.
- Shared runtime egress is a residual lateral surface among services requiring Internet access; Sharia egress remains separately isolated. Further segmentation requires actual-container compatibility testing.
- Custom seccomp/AppArmor requires ARM64 syscall evidence and remains unclaimed.
- OCI capacity/home-region availability and provider quotas are external.
- GitHub branch protections/reviewers/CODEOWNER/provenance and Oracle runtime secrets/permissions/IP allowlists remain owner configuration.
- Sharia source review and research-not-fatwa limitations remain unchanged.

## Final status

- **INFRASTRUCTURE HARDENING: PASS** — local implementation/static scope only
- **LOCAL TESTS: PASS**
- **PROTECTED TRADING CORE UNCHANGED: PASS**
- **TESTNET ENFORCEMENT: PASS** — verified in the paired TestNet repository
- **REAL ORACLE VALIDATION: PENDING**
- **ORACLE SOAK: PENDING**
- **LIVE PROMOTION: PROHIBITED**

This LIVE-capable package is suitable only for further review and later
simulation deployment. It is not evidence or permission for real-money trading.

## Primary references

- [Oracle Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Oracle instance creation](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm)
- [Oracle NTP configuration](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/configuringntpservice.htm)
- [Oracle instance metadata](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/gettingmetadata.htm)
- [Oracle Compute security](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/compute_security.htm)
- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker firewall behaviour](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
- [Docker iptables and `DOCKER-USER`](https://docs.docker.com/engine/network/firewall-iptables/)
- [Docker JSON log rotation](https://docs.docker.com/engine/logging/drivers/json-file/)
- [Docker live restore](https://docs.docker.com/engine/daemon/live-restore/)
- [Ubuntu Chrony guidance](https://documentation.ubuntu.com/server/how-to/networking/chrony-client/)
- [Ubuntu automatic security updates](https://documentation.ubuntu.com/server/how-to/software/automatic-updates/)
- [Binance Spot REST timing security](https://developers.binance.com/en/docs/products/spot/rest-api)
- [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub self-hosted runner guidance](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners)
