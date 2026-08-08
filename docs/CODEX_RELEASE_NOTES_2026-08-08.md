# Codex revision 2026-08-08C release notes

This is the live-capable package for revision `2026-08-08C`; its internal
release identifier is `V10.2-CODEX-2026-08-08C`. It remains disarmed by
default in simulation mode and is not certified for real-money trading.

## Runtime and release repairs

- The Sharia screener now receives `EXECUTION_MODE` from Compose and applies
  the same immutable package/execution matrix as the execution sidecar.
- The live package can start its safe simulation path without a production
  Sharia approval record. `EXECUTION_MODE=live` still fails closed unless
  `VALIDATION_STATUS.json` contains an explicitly approved immutable HTTPS
  host/model policy that exactly matches the runtime configuration.
- Cross-mode `EXECUTION_MODE=testnet` remains blocked in the live package.
- Regression coverage now exercises every permitted and forbidden package /
  execution combination, verifies the Compose propagation, and prevents
  drift between `RELEASE_VERSION`, `RELEASE_MODE`, validation metadata and the
  generated release manifest.
- Release and validation metadata have been advanced together to remove the
  stale revision mismatch.
- All 62 exact service and monitoring runtime requirement records are now
  SHA-256 hash-locked. CI, the service image build and the Oracle monitoring
  installer enforce them with separate `pip --require-hashes` invocations.
- The Oracle preflight now accepts the Python dependency closures and remains
  fail-closed on the two unresolved container-image digest pins.
- Live-package simulation no longer accepts an environment-selected screening
  destination: it uses an approved policy host, or the fixed official default
  when no policy is approved. Simulation does not require a production model
  approval; live execution still requires the exact approved host and model.

## Protected behaviour

- `IctSmcStrategy.py` was not modified. Its required SHA-256 remains
  `9f6bafc78c8cd0d9b9cbde615ddce89e304ab09738584b88d05bfdf92ff4e830`.
- The preserved all-in-one legacy core was not modified. Its required
  SHA-256 remains
  `70b1d67cc0092b5b8db4a68b343cf893641bde1aae580e9ef51e2adec1062459`.
- No production Sharia policy, credential, deployment secret, validation
  result or trading-performance claim has been invented or embedded.

## Evidence and remaining gates

Exact local results for this revision are recorded in
`docs/audit/TEST_EVIDENCE_LEDGER.csv`; the file set and hashes are bound by
`RELEASE_MANIFEST.json` and `RELEASE_SHA256.txt`.

The local full release gate passed 356 of 361 core tests with five documented
skips, 50 monitoring tests and 33 of 33 preserved legacy self-tests. Secret,
controller-integrity, audit-ledger, JSON, YAML and service-unit checks passed.
One Starlette/httpx deprecation warning remains disclosed. Docker was not
available on the local host, so container execution remains a GitHub gate.

The source package remains a real-money **NO-GO** until all external gates in
`VALIDATION_STATUS.json` are completed. In particular, this exact revision
still requires successful GitHub container CI, protected-branch/environment
controls, immutable container digests, authenticated Binance Spot Testnet
lifecycle evidence, Oracle soak and
rollback evidence, reconciliation evidence, performance review and explicit
manual production approval.
