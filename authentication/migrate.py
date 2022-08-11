from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User
from sqlalchemy_utils import database_exists, create_database, drop_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

while True:
    try:

        if database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            drop_database(application.config["SQLALCHEMY_DATABASE_URI"])

        create_database(application.config["SQLALCHEMY_DATABASE_URI"])
        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()

            customerRole = Role(role="customer")
            storekeeperRole = Role(role="storekeeper")
            adminRole = Role(role="admin")

            database.session.add(customerRole)
            database.session.add(storekeeperRole)
            database.session.add(adminRole)

            database.session.commit()

            admin = User(
                email="admin@admin.com",
                password="1",
                forename="admin",
                surname="admin",
                my_role=adminRole.id
            )

            database.session.add(admin)
            database.session.commit()
            break
    except Exception:
        print("Error!")


