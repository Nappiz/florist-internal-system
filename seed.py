from getpass import getpass

from sqlalchemy.orm import Session

from configs.database import get_engine
from configs.settings import get_settings
from use_cases.users.seed_superadmin import seed_superadmin


def main() -> None:
    configured = get_settings().seed_superadmin_password
    password = configured.get_secret_value() if configured else getpass("Initial superadmin password: ")
    with Session(get_engine()) as db:
        user = seed_superadmin(db, password)
        print(f"Superadmin ready; user ID: {user.id}. Existing password is never reset by this seed.")


if __name__ == "__main__":
    main()
