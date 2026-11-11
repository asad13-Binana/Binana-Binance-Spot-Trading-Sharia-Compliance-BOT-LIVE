# Oracle LIVE owner bundle — preparation only

The LIVE package uses Freqtrade **2026.10** and the `BinanaNfiSpot` five-minute
owner with four 250-USDT slots, the existing Sharia policy, market freshness,
native protection, recovery and signed release gates. Freqtrade is the sole
order owner. The read-only monitor cannot place orders; the old executable
sidecar and root legacy Compose deployment are absent from the bundle.

The template deliberately has `initial_state=stopped`, `allow_live=false` and
empty `live_activation`. The LIVE owner rejects startup while activation is
disabled. Preparing this package does not authorize production startup,
authenticated account access, certificate issuance, or trading.

## Immutable source package

The final images use a minimal Debian runtime with pinned patched native
libraries. Runtime pip and shells are absent; rebuild through the supplied
Dockerfiles for dependency updates. Follow the offline image gates and
remaining host acceptance requirements in [the image security review](IMAGE_SECURITY_20261112.md).

From the reviewed LIVE checkout, create a new output directory:

```sh
python runtime_owner/deployment/materialize_oracle_bundle.py /tmp/binana-live-owner-bundle
python /tmp/binana-live-owner-bundle/oracle_preflight.py --bundle /tmp/binana-live-owner-bundle
```

For offline packaging, append `--archive /path/to/freqtrade-2026.10.tar.gz` to
the first command. The required upstream commit is
`4cf0351e08d26e96a6429ef48103b726bb230cf8`, with archive SHA-256
`e7e83e139f0d7b01f337dfb2e0c4ff13d895431615886b3c8570e99bb139476a`.
Wrong archives, symlinks, incomplete manifests and existing output directories
are rejected. The complete output file manifest binds the separate LIVE
package profile and mode. No retained AWS image is needed.

The historical policy snapshot, scanner, market source and monitor are public
build inputs. They provide provenance, not evidence that an AWS or Oracle host
is currently running. No database, account state or private acceptance receipt
belongs in the public bundle.

## Isolated private inputs

Use `oracle.env.example` as the field list, stored outside the bundle at
`/etc/binana-oracle-live/runtime.env`, mode 600. The LIVE environment fields
are `BINANCE_LIVE_API_KEY` and `BINANCE_LIVE_API_SECRET`. Compose passes them
only to the owner. Never reuse Testnet keys, account epoch, issuer material,
configuration directory, state directory, Compose project or certificate.

| Input | LIVE path and requirement |
| --- | --- |
| Config | `/etc/binana-oracle-live/config`: only `config.json` and raw 32-byte `release-authority.ed25519.pub` |
| State | `/var/lib/binana-oracle-live/shared`: `freqtrade/`, `freqtrade/logs/`, `sharia/`, `universe/`, `runtime/` |
| Release | `/etc/binana-oracle-live/release`: only signed `certificate.json` and `deployment.json` when properly issued |
| Authority | Separate host-only storage, outside every container mount |

Use the fixed container UID 999/GID 987 and limit write permissions to the
intended state. The configuration example requires both a real reconciled
`exchange_epoch_id` and a unique `account_scope`. Its `REPLACE_WITH_...`
placeholders cannot pass private-input validation. LIVE never falls back to a
Testnet epoch or ledger scope. Restore a consistent, verified owner database
and inventory baseline before migrating any account with existing orders or
inventory; a fresh empty database is not a reconciliation.

File-only preflight checks the disabled preparation configuration:

```sh
python /opt/binana-live-owner-bundle/oracle_preflight.py \
  --bundle /opt/binana-live-owner-bundle \
  --env-file /etc/binana-oracle-live/runtime.env
```

This does not verify credentials or authorize activation. The preflight
rejects enabled LIVE activation, custom CCXT transport overrides, another
strategy, changed allocation, duplicate native Telegram polling, and embedded
secrets. The owner profile binds the approved production transport separately
from public market-data transport. The API binds only `127.0.0.1:8091`.

## Build and offline verification

On an appropriately prepared build host, Compose configuration and build do
not start services:

```sh
cd /opt/binana-live-owner-bundle
docker compose --env-file /etc/binana-oracle-live/runtime.env -f compose.json config -q
docker compose --env-file /etc/binana-oracle-live/runtime.env -f compose.json build
```

Do not run `up` or Resume from this preparation guide. Production activation
requires a separate reviewed change to private inputs and authenticated
acceptance for the exact image/account/environment/configuration bindings.
The existing certificate has a seven-day lifetime and does not permit missing,
expired or mismatched evidence. Host issuance/renewal tooling is in
`maintenance/README.md`, with explicit Oracle paths and Compose identity.
The issuer key and acceptance receipts must remain outside runtime mounts.

Default services are owner, universe, manual Sharia projector, Telegram broker
and read-only owner monitor. Research and its restricted proxy are optional,
disabled by default; a research result never updates the operational registry
without existing owner approval. The scanner defaults to all eligible pairs,
not a fixed 120, while all current screening, exclusions and liquidity gates
remain in place.

## Capacity and acceptance limits

Oracle currently allows an aggregate A1 equivalent of 2 OCPUs and 12 GB memory,
with 200 GB combined boot/block storage. One default owner stack has limits of
1.8 CPUs and 6,272 MiB; research raises these to 2 CPUs and 7,168 MiB. These are
limits, not native performance or build-headroom proof. Plan one Testnet OR
one LIVE stack within this envelope. Both default stacks total 3.6 CPUs and
12,544 MiB before Docker and the OS, exceeding one free allowance.

Native ARM64 execution, sustained resources, clean-host startup, reboot,
network loss, disk/OOM recovery, online SQLite backup and verified restore,
single-owner exclusion, certificate renewal, correct image/state rollback and
soak remain host acceptance gates. Preserve known-good images and consistent
backups. Do not use the root legacy installer as rollback for this owner.
No deletion of old files, containers, volumes or backups is performed by the
bundle builder. Local or emulated checks do not certify an Oracle host.

Official references:

- [Freqtrade 2026.10 Docker deployment](https://www.freqtrade.io/en/2026.10/docker_quickstart/)
- [Freqtrade 2026.10 ARM64 installation guidance](https://www.freqtrade.io/en/2026.10/installation/)
- [Oracle Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Binance official documentation index](https://developers.binance.com/en/docs/llms.txt)
