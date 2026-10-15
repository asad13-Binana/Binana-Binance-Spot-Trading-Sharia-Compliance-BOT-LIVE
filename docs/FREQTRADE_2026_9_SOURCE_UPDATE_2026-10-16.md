# Freqtrade 2026.9 source package update

The Docker wrapper, digest resolver, offline Compose recipe and CI probe now use official Freqtrade 2026.9, pinned to multi-platform index `sha256:989aff5636d8f0213ed44fe334c3314a194a51c0c755d16866960247aafd2eae`. This is a source/package update. No LIVE account, configuration, order or runtime was accessed or activated.

Official release: <https://github.com/freqtrade/freqtrade/releases/tag/2026.9>

Both the existing six-assertion strategy probe and the same assertions after loading IctSmc through the real 2026.9 StrategyResolver passed with no skips, network access or credentials. The deterministic fixture produced 14 entries over 6000 candles; the negative five-minute filter produced zero and the positive control 23. Repeated indicator/signal comparisons were identical. This checks compatibility, not strategy profitability.

IctSmcStrategy.py is unchanged (SHA256 `9f6bafc78c8cd0d9b9cbde615ddce89e304ab09738584b88d05bfdf92ff4e830`). Spot mode, its one-minute base and five-minute informative timeframe, simulation default, disabled native Freqtrade entry, no-short policy and LIVE interlocks remain unchanged.

The separately deployed AWS Testnet owner uses BinanaNfiSpot and a custom owner extension. Its flow-readmission repair belongs to the Testnet runtime_owner package and is not evidence that this LIVE package runs that owner. Copying Testnet owner state, credentials, certificates or deployment claims here would be inaccurate. LIVE deployment still requires its own approved configuration, acceptance evidence and separate authorization.
