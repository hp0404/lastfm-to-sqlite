"""Command-line interface: export Last.fm listening history to SQLite."""

from __future__ import annotations

import datetime as dt

import click
from sqlite_utils import Database

from lastfm.client import DATE_FORMAT, LastFM

api_key_option = click.option(
    "--api-key",
    envvar="LASTFM_API_KEY",
    required=True,
    help="Last.fm API key (or set LASTFM_API_KEY).",
)
user_option = click.option(
    "--user",
    envvar="LASTFM_USERNAME",
    required=True,
    help="Last.fm username (or set LASTFM_USERNAME).",
)
database_argument = click.argument(
    "database", type=click.Path(dir_okay=False, writable=True)
)


@click.group()
@click.version_option(package_name="lastfm-to-sqlite")
def cli() -> None:
    """Export Last.fm listening history to SQLite."""


@cli.command()
@database_argument
@api_key_option
@user_option
@click.option("--table", default="scrobbles", show_default=True, help="Table name.")
@click.option(
    "--start-date",
    type=click.DateTime([DATE_FORMAT]),
    help="Only export scrobbles on or after this date (YYYY-MM-DD, UTC).",
)
@click.option(
    "--end-date",
    type=click.DateTime([DATE_FORMAT]),
    help="Only export scrobbles on or before this date (YYYY-MM-DD, UTC).",
)
def export(
    database: str,
    api_key: str,
    user: str,
    table: str,
    start_date: dt.datetime | None,
    end_date: dt.datetime | None,
) -> None:
    """Export a user's scrobbles (played tracks) to DATABASE."""
    db = Database(database)
    with LastFM(api_key) as client:
        total = client.scrobble_count(user, start_date=start_date, end_date=end_date)
        tracks = client.recent_tracks(user, start_date=start_date, end_date=end_date)
        with click.progressbar(
            tracks, length=total, label=f"Exporting {total} scrobbles"
        ) as bar:
            db.table(table).upsert_all(bar, pk="uts_timestamp", batch_size=200)


@cli.command()
@database_argument
@api_key_option
@user_option
@click.option("--table", default="loved_tracks", show_default=True, help="Table name.")
def loved(database: str, api_key: str, user: str, table: str) -> None:
    """Export a user's loved tracks to DATABASE."""
    db = Database(database)
    with LastFM(api_key) as client:
        total = client.loved_count(user)
        tracks = client.loved_tracks(user)
        with click.progressbar(
            tracks, length=total, label=f"Exporting {total} loved tracks"
        ) as bar:
            db.table(table).upsert_all(bar, pk="uts_timestamp", batch_size=200)


if __name__ == "__main__":
    cli()
