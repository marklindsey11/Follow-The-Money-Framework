import orjson
import yaml
import click
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI
from uvicorn import Config, Server  # type: ignore
from typing import Iterable, Optional, Tuple
from followthemoney.cli.util import path_writer, InPath, OutPath
from followthemoney.cli.util import path_entities, write_entity
from followthemoney.cli.aggregate import sorted_aggregate

from nomenklatura import __version__
from nomenklatura.cache import Cache
from nomenklatura.matching.train import train_matcher
from nomenklatura.loader import FileLoader
from nomenklatura.resolver import Resolver
from nomenklatura.dataset import Dataset
from nomenklatura.entity import CompositeEntity as Entity
from nomenklatura.enrich import Enricher, make_enricher, match, enrich
from nomenklatura.resolver.db import DatabaseResolver
from nomenklatura.senzing import senzing_record
from nomenklatura.xref import xref as run_xref
from nomenklatura.tui import DedupeApp
from nomenklatura.server.api import create_router


log = logging.getLogger(__name__)

ResPath = click.Path(dir_okay=False, writable=True, path_type=Path)


@click.group(help="Nomenklatura API server")
def cli() -> None:
    logging.basicConfig(level=logging.INFO)


@cli.command("serve", help="Run the nomenklatura API")
@click.argument("entities", type=InPath)
def serve(entities: Path) -> None:
    resolver: Resolver[Entity] = DatabaseResolver.make_default()
    loader = FileLoader(entities, resolver)

    app = FastAPI(title="Nomenklatura", version=__version__)
    router = create_router(loader, resolver)
    app.include_router(router)

    server = Server(
        Config(
            app,
            host="0.0.0.0",
            port=9090,
            proxy_headers=True,
            # reload=settings.DEBUG,
            # reload_dirs=[code_dir],
            debug=True,
            log_level=logging.INFO,
            server_header=False,
        ),
    )
    server.run()


if __name__ == "__main__":
    cli()
