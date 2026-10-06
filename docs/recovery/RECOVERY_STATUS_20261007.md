# LIVE package status — 7 October 2026

LIVE PR #25 was merged at f346a7a91f6a228e048e34ba9da5f9a92c5ff66a. Its merged-main CI run 36645110522 passed. The registry remains 375 owner-listed symbols, preserving the prior 305 and adding the 70 missing from the latest 177-symbol list. Existing dates, simulation defaults and signed live-evidence gates remain unchanged.

This update records verification, recovery status and dependency security fixes. No LIVE code was deployed and no real-money orders or acceptance certificates were produced. The LIVE package remains uncertified for real-money operation.

On AWS Testnet, the research service now loads the exact supplied v19.3 controller. The startup configuration was repaired and historical exchange accounting was rechecked. The Testnet owner remains paused pending authenticated lifecycle, retained-inventory, restart and soak acceptance. Its recovery owner and host-specific image overlays are intentionally confined to the Testnet repository.

Research limitations remain: typed adverse verdicts and per-item retry evidence are incomplete, autonomous official-domain traversal is absent, and the AWS research service still lacked CoinGecko/CoinMarketCap keys at verification. A healthy service is not complete controller certification.

See the [Testnet recovery record](https://github.com/asad13-Binana/Binana-Binance-Spot-Trading-Sharia-Compliance-BOT-TestNet/blob/codex/runtime-recovery-20261007/docs/recovery/RECOVERY_STATUS_20261007.md) for deployment evidence, cleanup and outstanding work. Historical validation statements do not certify this LIVE package.

## Dependency audit follow-up

The new CI run detected newly published advisories affecting existing pins. Both packages now pin multidict 6.9.1, pypdf 6.19.0, urllib3 2.8.0 and monitoring PyJWT 2.15.0 with upstream PyPI distribution hashes. Both exact lock-file audits pass after the updates. Upstream references: [multidict](https://github.com/aio-libs/multidict/security/advisories/GHSA-54p9-h82j-f925), [pypdf](https://github.com/py-pdf/pypdf/releases/tag/6.19.0), [urllib3](https://github.com/urllib3/urllib3/releases/tag/2.8.0), [PyJWT](https://github.com/jpadilla/pyjwt/security/advisories/GHSA-x33g-cr3x-6449). A passing source audit does not update older running images.
