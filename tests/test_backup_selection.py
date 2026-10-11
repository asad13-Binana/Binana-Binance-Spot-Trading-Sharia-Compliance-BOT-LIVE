"""Execute the deployed script's actual find expression on a fixture tree."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest


class BackupSelection(unittest.TestCase):
    def test_rotating_backups_are_excluded_but_authoritative_databases_remain(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/'deploy/backup_state.sh').read_text()
        command=re.search(r'done < <\((find[\s\S]*?)\)\nfor metadata',source).group(1)
        shell=r'C:\Program Files\Git\bin\bash.exe' if os.name=='nt' else shutil.which('bash')
        with tempfile.TemporaryDirectory() as tmp:
            paths=['owner/main.sqlite','runtime/state.db','runtime/db_backups/rotating.sqlite',
                   'runtime/db_backups/old/nested.db']
            for name in paths:
                p=Path(tmp)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture')
            env=dict(os.environ,PERSIST=Path(tmp).as_posix())
            out=subprocess.check_output([shell,'-c',command],env=env)
            selected={Path(s.decode()).relative_to(tmp).as_posix() for s in out.split(b'\0') if s}
            self.assertEqual(selected,{'owner/main.sqlite','runtime/state.db'})
