# -*- coding: utf-8 -*-
import click
from sqlite_utils import Database
from lastfm.export import get_users_recent_tracks, DATE_FORMAT


formats = [DATE_FORMAT]


@click.group()
@click.version_option()
def cli():
    "Scrape LASTFM playlists to SQLite"


@cli.command("export")
@click.argument(
    "database",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option("-t", "--table", default="playlist", type=click.STRING)
@click.option("--user", type=click.STRING)
@click.option("--first_page", type=click.INT, default=1)
@click.option("--limit_per_page", type=click.INT, default=200)
@click.option("--extended", type=click.INT, default=0)
@click.option("--start_date", type=click.DateTime(formats))
@click.option("--end_date", type=click.DateTime(formats))
def export_playlist(
    database, 
    table, 
    user, 
    first_page=None, 
    limit_per_page=None,
    extended=None,
    start_date=None,
    end_date=None
):
    """
    Export user's lastfm playlist
    """        
    if not isinstance(database, Database):
        database = Database(database)

    table = database.table(table)
    data = get_users_recent_tracks(
        user=user, first_page=first_page, limit_per_page=limit_per_page,
        extended=extended, start_date=start_date, end_date=end_date
    )
    for item in data:
        table.upsert(item, pk="uts_timestamp")


if __name__ == "__main__":
    cli()