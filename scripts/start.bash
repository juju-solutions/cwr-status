INI=production /usr/local/bin/gunicorn -w 3 --access-logfile \
  $HOME/logs/gunicorn-access.log --error-logfile $HOME/logs/gunicorn.log \
  cwrstatus.main:app -b 0.0.0.0:8000 &
