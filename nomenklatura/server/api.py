# /nk/entities/X
# /nk/pair?offset=X
# /nk/judgements/XXXX
# POST /nk/decide {}
from typing import Union
from fastapi import APIRouter, Query
from fastapi import HTTPException, Path

from nomenklatura.dataset import DS
from nomenklatura.entity import CE
from nomenklatura.loader import Loader
from nomenklatura.resolver.resolver import Resolver

from nomenklatura.server.model import EntityResponse, ErrorResponse


def create_router(loader: Loader[DS, CE], resolver: Resolver[CE]):
    router = APIRouter()

    @router.get(
        "/entities/{entity_id}",
        response_model=EntityResponse,
        responses={
            307: {"description": "The entity is merged into another ID"},
            404: {"model": ErrorResponse, "description": "Entity not found"},
        },
    )
    def fetch_entity(
        entity_id: str = Path(None, description="ID of the entity to retrieve"),
        nested: bool = Query(True, title="Include adjacent entities in response"),
    ) -> EntityResponse:
        entity = loader.get_entity(entity_id)
        if entity is None:
            raise HTTPException(404, detail="No such entity!")
        return EntityResponse.from_entity(entity)

    @router.get(
        "/judgements/{entity_id}",
        response_model=EntityResponse,
        responses={
            307: {"description": "The entity is merged into another ID"},
            404: {"model": ErrorResponse, "description": "Entity not found"},
        },
    )
    def fetch_judgements(
        entity_id: str = Path(None, description="ID of the entity to retrieve"),
    ) -> EntityResponse:
        entity = loader.get_entity(entity_id)
        if entity is None:
            raise HTTPException(404, detail="No such entity!")
        return EntityResponse.from_entity(entity)

    return router
