# LIVE owner build and Oracle preparation

Use [the Oracle owner bundle guide](../../docs/ORACLE_OWNER_BUNDLE.md) to
materialize the separate Freqtrade 2026.10 / BinanaNfiSpot package. The bundle
uses verified public source and current owner patches; it does not depend on
an AWS image or AWS host paths. The legacy root Compose topology and alternative order engines are retired;
only the Oracle owner bundle is supported for a new installation.

The LIVE configuration starts stopped with `allow_live=false` and an empty
activation acknowledgement. Owner startup rejection is expected until a
separate, authorized activation supplies the required account-bound evidence
and certificate. A successful source check or image build does not authorize
trading, certify the Oracle host, or allow reuse of an old Testnet certificate.

The pinned NFI vendor snapshot contains 15 existing Ruff F821 diagnostics:
13 string annotations referring to `Orders`, and `derisk_4_threshold` /
`derisk_4_stake` in a position-adjustment path disabled by the selected owner
wrapper. The narrow per-file entry in `ruff.toml` preserves the verified vendor
bytes; it does not suppress other files or other correctness checks. Enabling
position adjustment requires separate upstream validation and acceptance.

[Host issuance and renewal](../../docs/recovery/RELEASE_RENEWAL_HOST.md) requires
an explicit Oracle host profile, an issuer key outside runtime mounts, and
fresh evidence for the exact image, account, configuration and dependency
set. Native Oracle install, reboot, expiry-crossing renewal and restore/soak
checks remain host-specific release gates.
