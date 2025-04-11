from unlok_next.rath import UnlokRath
from typing import AsyncIterator, Tuple, Optional, Iterator, Literal, Iterable, List
from pydantic import Field, ConfigDict, BaseModel
from unlok_next.funcs import aexecute, asubscribe, execute, subscribe
from rath.scalars import ID
from enum import Enum


class StructureInput(BaseModel):
    object: ID
    identifier: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DevelopmentClientInput(BaseModel):
    manifest: "ManifestInput"
    composition: Optional[ID] = None
    requirements: Tuple["Requirement", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ManifestInput(BaseModel):
    identifier: str
    version: str
    logo: Optional[str] = None
    scopes: Tuple[str, ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class Requirement(BaseModel):
    service: str
    optional: bool
    description: Optional[str] = None
    key: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateStreamInput(BaseModel):
    room: ID
    title: Optional[str] = None
    agent_id: Optional[str] = Field(alias="agentId", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MessageAgentRoom(BaseModel):
    """Room(id, title, description, creator)"""

    typename: Literal["Room"] = Field(alias="__typename", default="Room", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class MessageAgent(BaseModel):
    """Agent(id, room, name, app, user)"""

    typename: Literal["Agent"] = Field(
        alias="__typename", default="Agent", exclude=True
    )
    id: ID
    room: MessageAgentRoom
    model_config = ConfigDict(frozen=True)


class Message(BaseModel):
    """Message represent the message of an agent on a room"""

    typename: Literal["Message"] = Field(
        alias="__typename", default="Message", exclude=True
    )
    id: ID
    text: str
    "A clear text representation of the rich comment"
    agent: MessageAgent
    "The user that created this comment"
    model_config = ConfigDict(frozen=True)


class ListMessageAgent(BaseModel):
    """Agent(id, room, name, app, user)"""

    typename: Literal["Agent"] = Field(
        alias="__typename", default="Agent", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ListMessage(BaseModel):
    """Message represent the message of an agent on a room"""

    typename: Literal["Message"] = Field(
        alias="__typename", default="Message", exclude=True
    )
    id: ID
    text: str
    "A clear text representation of the rich comment"
    agent: ListMessageAgent
    "The user that created this comment"
    model_config = ConfigDict(frozen=True)


class StreamAgentRoom(BaseModel):
    """Room(id, title, description, creator)"""

    typename: Literal["Room"] = Field(alias="__typename", default="Room", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class StreamAgent(BaseModel):
    """Agent(id, room, name, app, user)"""

    typename: Literal["Agent"] = Field(
        alias="__typename", default="Agent", exclude=True
    )
    id: ID
    room: StreamAgentRoom
    model_config = ConfigDict(frozen=True)


class Stream(BaseModel):
    """Stream(id, agent, title, token)"""

    typename: Literal["Stream"] = Field(
        alias="__typename", default="Stream", exclude=True
    )
    id: ID
    title: str
    "The Title of the Stream"
    token: str
    agent: StreamAgent
    "The agent that created this stream"
    model_config = ConfigDict(frozen=True)


class Room(BaseModel):
    """Room(id, title, description, creator)"""

    typename: Literal["Room"] = Field(alias="__typename", default="Room", exclude=True)
    id: ID
    title: str
    "The Title of the Room"
    description: str
    model_config = ConfigDict(frozen=True)


class SendMutation(BaseModel):
    send: Message

    class Arguments(BaseModel):
        text: str
        room: ID
        agent_id: str = Field(alias="agentId")
        attach_structures: Optional[List[StructureInput]] = Field(
            alias="attachStructures", default=None
        )

    class Meta:
        document = "fragment Message on Message {\n  id\n  text\n  agent {\n    id\n    room {\n      id\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation Send($text: String!, $room: ID!, $agentId: String!, $attachStructures: [StructureInput!]) {\n  send(\n    input: {text: $text, room: $room, agentId: $agentId, attachStructures: $attachStructures}\n  ) {\n    ...Message\n    __typename\n  }\n}"


class CreateClientMutationCreatedevelopmentalclientOauth2client(BaseModel):
    """Application(id, client_id, user, redirect_uris, post_logout_redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, created, updated, algorithm)"""

    typename: Literal["Oauth2Client"] = Field(
        alias="__typename", default="Oauth2Client", exclude=True
    )
    client_id: str = Field(alias="clientId")
    model_config = ConfigDict(frozen=True)


class CreateClientMutationCreatedevelopmentalclient(BaseModel):
    """A client is a way of authenticating users with a release.
    The strategy of authentication is defined by the kind of client. And allows for different authentication flow.
    E.g a client can be a DESKTOP app, that might be used by multiple users, or a WEBSITE that wants to connect to a user's account,
    but also a DEVELOPMENT client that is used by a developer to test the app. The client model thinly wraps the oauth2 client model, which is used to authenticate users.
    """

    typename: Literal["Client"] = Field(
        alias="__typename", default="Client", exclude=True
    )
    token: str
    "The configuration of the client. This is the configuration that will be sent to the client. It should never contain sensitive information."
    oauth2_client: CreateClientMutationCreatedevelopmentalclientOauth2client = Field(
        alias="oauth2Client"
    )
    "The real oauth2 client that is used to authenticate users with this client."
    model_config = ConfigDict(frozen=True)


class CreateClientMutation(BaseModel):
    create_developmental_client: CreateClientMutationCreatedevelopmentalclient = Field(
        alias="createDevelopmentalClient"
    )

    class Arguments(BaseModel):
        input: DevelopmentClientInput

    class Meta:
        document = "mutation CreateClient($input: DevelopmentClientInput!) {\n  createDevelopmentalClient(input: $input) {\n    token\n    oauth2Client {\n      clientId\n      __typename\n    }\n    __typename\n  }\n}"


class CreateStreamMutation(BaseModel):
    create_stream: Stream = Field(alias="createStream")

    class Arguments(BaseModel):
        input: CreateStreamInput

    class Meta:
        document = "fragment Stream on Stream {\n  id\n  title\n  token\n  agent {\n    id\n    room {\n      id\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateStream($input: CreateStreamInput!) {\n  createStream(input: $input) {\n    ...Stream\n    __typename\n  }\n}"


class CreateRoomMutation(BaseModel):
    create_room: Room = Field(alias="createRoom")

    class Arguments(BaseModel):
        title: Optional[str] = Field(default=None)
        description: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment Room on Room {\n  id\n  title\n  description\n  __typename\n}\n\nmutation CreateRoom($title: String, $description: String) {\n  createRoom(input: {title: $title, description: $description}) {\n    ...Room\n    __typename\n  }\n}"


class GetStreamQuery(BaseModel):
    stream: Stream

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Stream on Stream {\n  id\n  title\n  token\n  agent {\n    id\n    room {\n      id\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetStream($id: ID!) {\n  stream(id: $id) {\n    ...Stream\n    __typename\n  }\n}"


class GetRoomQuery(BaseModel):
    room: Room

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Room on Room {\n  id\n  title\n  description\n  __typename\n}\n\nquery GetRoom($id: ID!) {\n  room(id: $id) {\n    ...Room\n    __typename\n  }\n}"


class WatchRoomSubscriptionRoom(BaseModel):
    typename: Literal["RoomEvent"] = Field(
        alias="__typename", default="RoomEvent", exclude=True
    )
    message: Optional[ListMessage] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchRoomSubscription(BaseModel):
    room: WatchRoomSubscriptionRoom

    class Arguments(BaseModel):
        room: ID
        agent_id: ID = Field(alias="agentId")

    class Meta:
        document = "fragment ListMessage on Message {\n  id\n  text\n  agent {\n    id\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchRoom($room: ID!, $agentId: ID!) {\n  room(room: $room, agentId: $agentId) {\n    message {\n      ...ListMessage\n      __typename\n    }\n    __typename\n  }\n}"


async def asend(
    text: str,
    room: ID,
    agent_id: str,
    attach_structures: Optional[List[StructureInput]] = None,
    rath: Optional[UnlokRath] = None,
) -> Message:
    """Send


    Arguments:
        text (str): No description
        room (ID): No description
        agent_id (str): No description
        attach_structures (Optional[List[StructureInput]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Message"""
    return (
        await aexecute(
            SendMutation,
            {
                "text": text,
                "room": room,
                "agentId": agent_id,
                "attachStructures": attach_structures,
            },
            rath=rath,
        )
    ).send


def send(
    text: str,
    room: ID,
    agent_id: str,
    attach_structures: Optional[List[StructureInput]] = None,
    rath: Optional[UnlokRath] = None,
) -> Message:
    """Send


    Arguments:
        text (str): No description
        room (ID): No description
        agent_id (str): No description
        attach_structures (Optional[List[StructureInput]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Message"""
    return execute(
        SendMutation,
        {
            "text": text,
            "room": room,
            "agentId": agent_id,
            "attachStructures": attach_structures,
        },
        rath=rath,
    ).send


async def acreate_client(
    manifest: ManifestInput,
    requirements: Iterable[Requirement],
    composition: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> CreateClientMutationCreatedevelopmentalclient:
    """CreateClient


    Arguments:
        manifest:  (required)
        composition: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        requirements:  (required) (list) (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateClientMutationCreatedevelopmentalclient"""
    return (
        await aexecute(
            CreateClientMutation,
            {
                "input": {
                    "manifest": manifest,
                    "composition": composition,
                    "requirements": requirements,
                }
            },
            rath=rath,
        )
    ).create_developmental_client


def create_client(
    manifest: ManifestInput,
    requirements: Iterable[Requirement],
    composition: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> CreateClientMutationCreatedevelopmentalclient:
    """CreateClient


    Arguments:
        manifest:  (required)
        composition: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        requirements:  (required) (list) (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateClientMutationCreatedevelopmentalclient"""
    return execute(
        CreateClientMutation,
        {
            "input": {
                "manifest": manifest,
                "composition": composition,
                "requirements": requirements,
            }
        },
        rath=rath,
    ).create_developmental_client


async def acreate_stream(
    room: ID,
    title: Optional[str] = None,
    agent_id: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> Stream:
    """CreateStream


    Arguments:
        room: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        agent_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Stream"""
    return (
        await aexecute(
            CreateStreamMutation,
            {"input": {"room": room, "title": title, "agent_id": agent_id}},
            rath=rath,
        )
    ).create_stream


def create_stream(
    room: ID,
    title: Optional[str] = None,
    agent_id: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> Stream:
    """CreateStream


    Arguments:
        room: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        agent_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Stream"""
    return execute(
        CreateStreamMutation,
        {"input": {"room": room, "title": title, "agent_id": agent_id}},
        rath=rath,
    ).create_stream


async def acreate_room(
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> Room:
    """CreateRoom


    Arguments:
        title (Optional[str], optional): No description.
        description (Optional[str], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Room"""
    return (
        await aexecute(
            CreateRoomMutation, {"title": title, "description": description}, rath=rath
        )
    ).create_room


def create_room(
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> Room:
    """CreateRoom


    Arguments:
        title (Optional[str], optional): No description.
        description (Optional[str], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Room"""
    return execute(
        CreateRoomMutation, {"title": title, "description": description}, rath=rath
    ).create_room


async def aget_stream(id: ID, rath: Optional[UnlokRath] = None) -> Stream:
    """GetStream


    Arguments:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Stream"""
    return (await aexecute(GetStreamQuery, {"id": id}, rath=rath)).stream


def get_stream(id: ID, rath: Optional[UnlokRath] = None) -> Stream:
    """GetStream


    Arguments:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Stream"""
    return execute(GetStreamQuery, {"id": id}, rath=rath).stream


async def aget_room(id: ID, rath: Optional[UnlokRath] = None) -> Room:
    """GetRoom


    Arguments:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Room"""
    return (await aexecute(GetRoomQuery, {"id": id}, rath=rath)).room


def get_room(id: ID, rath: Optional[UnlokRath] = None) -> Room:
    """GetRoom


    Arguments:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Room"""
    return execute(GetRoomQuery, {"id": id}, rath=rath).room


async def awatch_room(
    room: ID, agent_id: ID, rath: Optional[UnlokRath] = None
) -> AsyncIterator[WatchRoomSubscriptionRoom]:
    """WatchRoom


    Arguments:
        room (ID): No description
        agent_id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        WatchRoomSubscriptionRoom"""
    async for event in asubscribe(
        WatchRoomSubscription, {"room": room, "agentId": agent_id}, rath=rath
    ):
        yield event.room


def watch_room(
    room: ID, agent_id: ID, rath: Optional[UnlokRath] = None
) -> Iterator[WatchRoomSubscriptionRoom]:
    """WatchRoom


    Arguments:
        room (ID): No description
        agent_id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        WatchRoomSubscriptionRoom"""
    for event in subscribe(
        WatchRoomSubscription, {"room": room, "agentId": agent_id}, rath=rath
    ):
        yield event.room


DevelopmentClientInput.model_rebuild()
