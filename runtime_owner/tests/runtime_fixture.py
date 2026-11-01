"""Explicit LIVE fixtures; never enables a runtime or reaches a network."""
from copy import deepcopy

def live_config(value):
    result=deepcopy(value)
    policy=result['binana']
    policy.update(environment='live', allow_live=True, live_activation='I_AUTHORIZE_BINANA_LIVE_SPOT')
    epoch=policy.pop('testnet_epoch_id', policy.get('exchange_epoch_id', 'fixture-epoch'))
    policy['exchange_epoch_id']=epoch if len(epoch)>=8 else 'fixture-'+epoch
    policy.setdefault('account_scope','fixture-live-account')
    result.update(initial_state='stopped', dry_run=False)
    result.setdefault('exchange',{})['binana_testnet']=False
    return result
