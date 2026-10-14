import datetime
from email.message import EmailMessage
from email.utils import formataddr
import json
import logging
from pathlib import Path
import smtplib
import subprocess


LOCAL_PATH = Path(r"E:\Backup\github")
LOG_PATH = Path(__file__).with_name("backup-git.log")
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def run_command(command, cwd=None):
    if cwd is not None:
        logging.info("Running command in %s: %s", cwd, subprocess.list2cmdline(command))
    else:
        logging.info("$ %s", subprocess.list2cmdline(command))
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        logging.info("%s", result.stdout.rstrip())
    if result.stderr:
        logging.warning("%s", result.stderr.rstrip())
    if result.returncode:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def backup_repositories():
    local_folders = [
        entry.name for entry in LOCAL_PATH.iterdir() if entry.is_dir()
    ]
    logging.info("local_folders: %s", local_folders)

    result = run_command(
        ["gh", "repo", "list", "--limit", "999", "--json", "name,updatedAt", "phoenixlam"]
    )
    remote_folders = [repo["name"] for repo in json.loads(result.stdout)]
    logging.info("remote_folders: %s", remote_folders)

    diff_list = list(set(remote_folders) - set(local_folders))
    logging.info("diff_list: %s", diff_list)
    for repo in diff_list:
        run_command(
            ["gh", "repo", "clone", f"phoenixlam/{repo}", str(LOCAL_PATH / repo)]
        )

    for repo in remote_folders:
        if repo in local_folders:
            run_command(["git", "pull", "origin"], cwd=LOCAL_PATH / repo)


def read_mail_config():
    config = {}
    with ENV_PATH.open(encoding="utf-8") as env_file:
        for line_number, raw_line in enumerate(env_file, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()

            key, separator, value = line.partition("=")
            if not separator:
                raise ValueError(f"Invalid .env entry on line {line_number}")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            config[key] = value

    required_keys = (
        "MAIL_HOST",
        "MAIL_PORT",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_FROM_EMAIL",
        "MAIL_FROM_NAME",
        "MAIL_TO"
    )
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        raise ValueError(f"Missing .env settings: {', '.join(missing_keys)}")

    try:
        config["MAIL_PORT"] = int(config["MAIL_PORT"])
    except ValueError as error:
        raise ValueError("MAIL_PORT must be an integer") from error
    return config


def send_log_email():
    config = read_mail_config()

    msg = EmailMessage()
    msg["Subject"] = f"GitHub backup log - {datetime.date.today().isoformat()}"
    msg["From"] = formataddr(
        (config["MAIL_FROM_NAME"], config["MAIL_FROM_EMAIL"])
    )
    msg["To"] = config["MAIL_TO"]
    msg.set_content(LOG_PATH.read_text(encoding="utf-8"))

    with smtplib.SMTP_SSL(config["MAIL_HOST"], config["MAIL_PORT"], timeout=30) as server:
        server.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
        server.send_message(msg)
    logging.info("Email sent successfully!")


def main():
    configure_logging()
    logging.info("Starting Git repository backup")

    backup_error = None
    try:
        backup_repositories()
    except Exception as error:
        logging.exception("Git repository backup failed")
        backup_error = error

    try:
        logging.info("Sending backup log email")
        send_log_email()
    except Exception:
        logging.exception("Failed to email the backup log")
        raise

    if backup_error is not None:
        raise backup_error


if __name__ == "__main__":
    main()
