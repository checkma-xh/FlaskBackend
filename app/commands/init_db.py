import click

from app import app
from app import db


@app.cli.command()  
@click.option('--drop', is_flag=True, prompt=True, help='Create after Drop.')
def init_db(drop):
    if drop:
        db.drop_all()
        click.echo('Deleted database.')

    db.create_all()
    click.echo('Initialized database.')