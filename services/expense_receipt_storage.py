from pathlib import Path
from uuid import UUID
from configs.settings import get_settings


def receipt_path(storage_name):
    # Only generated UUID storage keys may resolve into the private directory.
    if str(UUID(storage_name))!=storage_name:
        raise ValueError('Invalid storage key')
    return Path(get_settings().private_receipt_dir).resolve()/storage_name


def save_receipt(storage_name,content):
    path=receipt_path(storage_name); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream: stream.write(content)
    return path


def remove_receipt(storage_name):
    receipt_path(storage_name).unlink(missing_ok=True)
