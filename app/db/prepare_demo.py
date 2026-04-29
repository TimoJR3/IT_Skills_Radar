from app.db.init_db import init_schema
from app.db.init_db import seed_data


def prepare_demo() -> None:
    init_schema()
    seed_data()


if __name__ == "__main__":
    prepare_demo()
