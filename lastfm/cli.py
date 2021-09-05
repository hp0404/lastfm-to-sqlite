# -*- coding: utf-8 -*-
import click
from sqlite_utils import Database
from lastfm import LastFM


formats = [LastFM.DATE_FORMAT]


@click.group()
@click.version_option()
def cli():
    "Scrape LASTFM playlists to SQLite"


@cli.command("export")
@click.argument("api", type=click.STRING, required=True)
@click.argument(
    "database",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option("-t", "--table", default="playlist", type=click.STRING)
@click.option("--user", type=click.STRING, required=True)
@click.option("--first_page", type=click.INT, default=1)
@click.option("--limit_per_page", type=click.INT, default=200)
@click.option("--extended", type=click.INT, default=0)
@click.option("--start_date", type=click.DateTime(formats))
@click.option("--end_date", type=click.DateTime(formats))
def export_playlist(
    api,
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
    api = LastFM(
        api=api, username=user, first_page=first_page, 
        limit_per_page=limit_per_page, extended=extended, 
        start_date=start_date, end_date=end_date
    )
    api.ensure_context_created()
    data = api.fetch()
    with click.progressbar(length=api.total_pages, label="Fetching data") as bar:
        for idx, item in enumerate(data):
            table.upsert(item, pk="uts_timestamp")
            bar.pos = int(idx / api.total_pages * 100)
            bar.update(0)


if __name__ == "__main__":
    cli()