import logging
import os
import sys
from pathlib import Path
from datetime import datetime

import requests
from packaging.version import parse as parse_version

logger = logging.getLogger(__name__)


def get_appdata_root():

    home_dir = Path.home()

    if os.getenv("XDG_CONFIG_HOME"):
        appdata_dir = Path(os.getenv("XDG_CONFIG_HOME"))
    elif os.getenv("APPDATA"):
        appdata_dir = Path(os.getenv("APPDATA"))
    elif sys.platform.startswith('darwin'):
        appdata_dir = home_dir / 'Library' / 'Application Support'
    else:
        appdata_dir = home_dir / '.config'

    return appdata_dir


def get_appdata_dir():
    """
    Get appdata directory where configuration and data is stored
    """
    return get_appdata_root() / 'deemon'


def get_backup_dir():
    return Path(get_appdata_dir() / "backups")


def init_appdata_dir(appdata):
    Path(appdata / 'logs').mkdir(parents=True, exist_ok=True)
    Path(appdata / 'backups').mkdir(exist_ok=True)


def delete_appdata(appdata):
    import shutil
    try:
        shutil.rmtree(appdata)
    except OSError as e:
        logger.info(f"Error while deleting path: {e}")

def reinit_appdata_dir(appdata):
    if appdata.exists():
        logger.info("Deleting existing application data directory (config, database, etc.)")
        delete_appdata(appdata)
    logger.info("Initializing new application data directory...")
    init_appdata_dir(appdata)


def get_config():
    return get_appdata_dir() / 'config.json'


def get_database():
    return get_appdata_dir() / 'deemon.db'


def get_log_file():
    """
    Get path to log file with the current date in the filename.
    """
    current_date = datetime.now().strftime('%d-%m-%Y')
    log_filename = f'{current_date}-deemon.log'
    return Path(get_appdata_dir() / 'logs' / log_filename)


def get_latest_version(release_type):
    latest_ver = "https://pypi.org/pypi/deemon/json"

    try:
        response = requests.get(latest_ver)
    except requests.exceptions.ConnectionError:
        return

    latest_stable = parse_version(response.json()['info']['version'])

    if release_type == "beta":
        all_releases = [parse_version(x) for x in response.json()['releases']]
        sorted_releases = sorted(all_releases, reverse=True)
        for release in sorted_releases:
            if "b" in str(release) or "rc" in str(release):
                if release > latest_stable:
                    return release
                else:
                    return latest_stable
    else:
        return latest_stable

def get_changelog(ver: str):
    try:
        response = requests.get("https://api.github.com/repos/digitalec/"
                                "deemon/releases")
    except requests.exceptions.ConnectionError:
        return print("Unable to reach GitHub API")

    for release in response.json():
        if release['name'] == ver:
            return print(release['body'])
    return print(f"Changelog for v{ver} was not found.")
