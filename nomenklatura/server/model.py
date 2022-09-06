from typing import Dict, List, Union
from pydantic import BaseModel, Field

from nomenklatura.entity import CE

EntityProperties = Dict[str, List[Union[str, "EntityResponse"]]]


class ErrorResponse(BaseModel):
    detail: str


class EntityResponse(BaseModel):
    id: str = Field(..., example="NK-A7z....")
    caption: str = Field(..., example="John Doe")
    schema_: str = Field(..., example="LegalEntity", alias="schema")
    properties: EntityProperties = Field(..., example={"name": ["John Doe"]})
    datasets: List[str] = Field([], example=["us_ofac_sdn"])
    referents: List[str] = Field([], example=["ofac-1234"])

    @classmethod
    def from_entity(cls, entity: CE) -> "EntityResponse":
        return cls(
            id=entity.id,
            caption=entity.caption,
            schema=entity.schema.name,
            properties=dict(entity.properties),
            datasets=list(entity.datasets),
            referents=list(entity.referents),
        )


EntityResponse.update_forward_refs()
