import click

@click.group()
def cli():
    pass


@click.command()
@click.confirmation_option(
    prompt='This will erase everything in the database. Do you want to continue?')
def reset_db():
    """Resets the database to the original state using alembic downgrade and upgrade commands"""
    from alembic.command import downgrade, upgrade
    from alembic.config import Config as AlembicConfig
    config = AlembicConfig('alembic.ini')
    downgrade(config, 'base')
    upgrade(config, 'head')
    click.echo('Database has been reset')


cli.add_command(reset_db)

if __name__ == '__main__':
    cli()
