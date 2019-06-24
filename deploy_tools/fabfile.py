import random
from patchwork.files import append, exists
from fabric2 import task
import subprocess

REPO_URL = "https://github.com/ForisTale/Django_TDD.git"


@task
def deploy(conn):
    site_folder = f"/home/{conn.user}/sites/{conn.host}"
    conn.run(f"mkdir -p {site_folder}")
    with conn.cd(site_folder):
        _get_latest_source(conn)
        # print(1, "done")
        _update_virtualenv(conn)
        # print(2, "done")
        _create_or_update_dotenv(conn)
        # print(3, "done")
        _update_static_files(conn)
        # print(4, "done")
        _update_database(conn)
        # print(5, "done")


def _get_latest_source(connection):
    if exists(connection, ".git"):
        connection.run("git fetch")
    else:
        connection.run(f"git clone {REPO_URL} .")
    current_commit = subprocess.run("git log -n 1 --format=%H", shell=True, capture_output=True)
    current_commit = str(current_commit.stdout)[2:-3]
    connection.run(f"git reset --hard {current_commit}")


def _update_virtualenv(connection):
    if not exists(connection, "virtualenv/bin/pip"):
        connection.run(f"python3.6 -m venv virtualenv")
    connection.run("./virtualenv/bin/pip install -r requirements.txt")


def _create_or_update_dotenv(connection):
    append(connection, ".env", "DJANGO_DEBUG_FALSE=y")
    append(connection, ".env", f"SITENAME={connection.host}")
    current_contents = connection.run("cat .env")
    if "DJANGO_SECRET_KEY" not in str(current_contents):
        new_secret = "".join(random.SystemRandom().choices(
            "abcdefghijklmnopqrstuvwxyz0123456789", k=50
        ))
        append(connection, ".env", f"DJANGO_SECRET_KEY={new_secret}")


def _update_static_files(connection):
    connection.run("./virtualenv/bin/python manage.py collectstatic --noinput")


def _update_database(connection):
    connection.run("./virtualenv/bin/python manage.py migrate --noinput")

