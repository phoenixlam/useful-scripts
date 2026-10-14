# useful-scripts

## Git repository backup

`python/backup-git.py` writes the backup output to
`python/backup-git.log` and emails it to `MAIL_TO`. Configure
the SMTP connection in the repository-root `.env` file using `MAIL_HOST`,
`MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM_EMAIL`, and
`MAIL_FROM_NAME`. Keep `.env` private; it is ignored by Git.