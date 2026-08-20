#!/usr/bin/env bash
# Immutable, non-secret host identity for this repository package.
# Keep this file release-controlled; real credentials remain in PRIVATE_ROOT/.env.
readonly INSTANCE_SLUG=binana-live
readonly INSTANCE_MODE=live
readonly COMPOSE_PROJECT_NAME=binana-live
readonly SERVICE_IMAGE=binana-live-services
readonly APP_ROOT=/opt/binana-live
readonly PRIVATE_ROOT=/etc/binana-live
readonly PERSIST_PARENT=/var/lib/binana-live
readonly PERSIST=/var/lib/binana-live/shared
readonly MONITOR_LOG_DIR=/var/log/binana-live/monitor
readonly DEPLOY_INBOX=/var/lib/binana-live/deploy-inbox
readonly INSTALL_LOCK=/var/lock/binana-live.install.lock
readonly BACKUP_LOCK=/var/lock/binana-live.backup.lock
readonly ACTIONS_LOCK=/var/lock/binana-live.actions-deploy.lock
readonly BOT_USER=binanalive
readonly MONITOR_USER=binanalivemon
readonly SYSTEMD_PREFIX=binana-live
readonly EXPECTED_MONITOR_PORT=8092
readonly OCI_OBJECT_PREFIX=binana-live
readonly GITHUB_RUNNER_LABEL=oracle-binana-live
