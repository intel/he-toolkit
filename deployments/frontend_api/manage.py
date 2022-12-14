"""Manage"""
from flask.cli import FlaskGroup
from app import create_app
from app.models.db import db

cli = FlaskGroup(create_app)


@cli.command("create_db")
def create_db():
    # Use for clean start
    # db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    cli()
