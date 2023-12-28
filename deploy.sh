#!/bin/bash
rsync -av --exclude-from=.gitignore --exclude .git ./ web@nuke:/web/punch-through/
scp config/prod.json web@nuke:/web/punch-through/config/prod.json
ssh web@nuke -f "ps aux | grep gunicorn | grep "punch:app" | awk '{ print \$2 }' | xargs kill -HUP"