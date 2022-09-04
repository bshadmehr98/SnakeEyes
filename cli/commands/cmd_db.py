import logging

import click

from snakeeyes.app import create_app
from snakeeyes.extentions import db
from snakeeyes.blueprints.users.models import User
from snakeeyes.blueprints.platforms.models import Platform
import uuid
import secrets
import bcrypt

# Create an app context for the database connection.
app = create_app()
db.app = app

@click.group()
def cli():
    """Run MongoDB related tasks."""
    pass


@click.command()
def seed():
    for email in app.config["SEED_ADMIN_EMAIL"]:
        if User.find_by_identity(email) is not None:
            continue

        params = {"role": User.ROLES_ADMIN, "email": email, "timezone": "Asia/Tehran"}

        user = User(**params)
        user.save()

        logging.info(f"New admin created -> email: {email}, token: {user.token}")

    for name in app.config["SEED_PLATFORM_NAME"]:
        if Platform.objects(name=name).count() > 0:
            continue
        secret = secrets.token_urlsafe(32)
        params = {"name": name, "secret": secret}
        platform = Platform(**params)
        click.echo(f"Platform {name} added with the secret of {secret}")
        platform.save()

    return True


cli.add_command(seed)
