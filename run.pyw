from datetime import datetime
from os import system as run

while True:
    # if True:
    entries = ['git add .',
               'git commit -m "Added files through python program at %s"' % datetime.now(),
               'git push', ]
    for i in entries:
        run('cmd.exe /C' + i)
