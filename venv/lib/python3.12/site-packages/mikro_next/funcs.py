"""This module provides helpers for the mikro rath api
they are wrapped functions for the turms generated api"""

from .rath import MikroNextRath, current_mikro_next_rath
from koil.helpers import unkoil, unkoil_gen
from typing import Optional, Protocol, Type, Dict, Any, TypeVar, Iterator, AsyncIterator
from pydantic import BaseModel
import json


class MetaProtocol(Protocol):
    document: str


class Operation(Protocol):
    Meta: MetaProtocol
    Arguments: Type[BaseModel]


T = TypeVar("T")



async def arun_query(
    document: str,
    variables: Dict[str, Any],
    rath: Optional[MikroNextRath] = None,
) -> Dict[str, Any]:
    rath = rath or current_mikro_next_rath.get()
    return await rath.aquery(document, variables)


async def aexecute(
    operation: Type[T],
    variables: Dict[str, Any],
    rath: Optional[MikroNextRath] = None,
) -> T:
    try:
        
        x = await arun_query(
            operation.Meta.document,  # type: ignore
            {
                key: value
                for key, value in operation.Arguments(**variables)
                .dict(by_alias=True, exclude_unset=True)
                .items()
                if value is not None
            },  # type: ignore
            rath=rath,
        )

        try:
            return operation(**x.data)
        except Exception as e:
            raise Exception(
                f"Error serializing return from data: {json.dumps(x.data, indent=4)}"
            ) from e
    except Exception as e:
        raise e


def execute(
    operation: Type[T],
    variables: Dict[str, Any],
    rath: Optional[MikroNextRath] = None,
) -> T:
    
    try:
        
        x = unkoil(arun_query,
                   operation.Meta.document,  # type: ignore
                {
                    key: value
                    for key, value in operation.Arguments(**variables)
                    .dict(by_alias=True, exclude_unset=True)
                    .items()
                    if value is not None
                },  # type: ignore
                rath=rath,)
                
        
        try:
            return operation(**x.data)
        except Exception as e:
                raise Exception(
                    f"Error serializing return from data: {json.dumps(x.data, indent=4)}"
                ) from e
    except Exception as e:
        raise e
        
    
    
    


def subscribe(
    operation: Type[T],
    variables: Dict[str, Any],
    rath: Optional[MikroNextRath] = None,
) -> Iterator[T]:
    return unkoil_gen(asubscribe, operation, variables, rath=rath)


async def asubscribe(
    operation: Type[T],
    variables: Dict[str, Any],
    rath: Optional[MikroNextRath] = None,
) -> AsyncIterator[T]:
    rath = rath or current_mikro_next_rath.get()
    async for event in rath.asubscribe(
        operation.Meta.document,
        operation.Arguments(**variables).dict(by_alias=True),  # type: ignore
    ):
        yield operation(**event.data)
