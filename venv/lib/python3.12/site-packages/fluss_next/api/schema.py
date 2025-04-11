from typing import List, Annotated, Iterable, Union, Literal, Any, Optional, Dict, Tuple
from pydantic import ConfigDict, BaseModel, Field
from rath.scalars import ID
from fluss_next.funcs import execute, aexecute
from fluss_next.scalars import EventValue, ValidatorFunction
from fluss_next.rath import FlussRath
from fluss_next.traits import MockableTrait
from datetime import datetime
from enum import Enum


class GraphNodeKind(str, Enum):
    REACTIVE = "REACTIVE"
    ARGS = "ARGS"
    RETURNS = "RETURNS"
    REKUEST = "REKUEST"
    REKUEST_FILTER = "REKUEST_FILTER"


class PortScope(str, Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"


class PortKind(str, Enum):
    INT = "INT"
    STRING = "STRING"
    STRUCTURE = "STRUCTURE"
    LIST = "LIST"
    BOOL = "BOOL"
    DICT = "DICT"
    FLOAT = "FLOAT"
    DATE = "DATE"
    UNION = "UNION"
    MODEL = "MODEL"


class EffectKind(str, Enum):
    MESSAGE = "MESSAGE"
    HIDE = "HIDE"
    CUSTOM = "CUSTOM"


class AssignWidgetKind(str, Enum):
    SEARCH = "SEARCH"
    CHOICE = "CHOICE"
    SLIDER = "SLIDER"
    CUSTOM = "CUSTOM"
    STRING = "STRING"
    STATE_CHOICE = "STATE_CHOICE"


class ReturnWidgetKind(str, Enum):
    CHOICE = "CHOICE"
    CUSTOM = "CUSTOM"


class NodeKind(str, Enum):
    FUNCTION = "FUNCTION"
    GENERATOR = "GENERATOR"


class GraphEdgeKind(str, Enum):
    VANILLA = "VANILLA"
    LOGGING = "LOGGING"


class ReactiveImplementation(str, Enum):
    ZIP = "ZIP"
    COMBINELATEST = "COMBINELATEST"
    WITHLATEST = "WITHLATEST"
    BUFFER_COMPLETE = "BUFFER_COMPLETE"
    BUFFER_UNTIL = "BUFFER_UNTIL"
    DELAY = "DELAY"
    DELAY_UNTIL = "DELAY_UNTIL"
    CHUNK = "CHUNK"
    SPLIT = "SPLIT"
    OMIT = "OMIT"
    ENSURE = "ENSURE"
    SELECT = "SELECT"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"
    JUST = "JUST"
    PREFIX = "PREFIX"
    SUFFIX = "SUFFIX"
    FILTER = "FILTER"
    GATE = "GATE"
    TO_LIST = "TO_LIST"
    FOREACH = "FOREACH"
    IF = "IF"
    AND = "AND"
    ALL = "ALL"


class RunEventKind(str, Enum):
    NEXT = "NEXT"
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"
    UNKNOWN = "UNKNOWN"


class MapStrategy(str, Enum):
    MAP = "MAP"
    MAP_TO = "MAP_TO"
    MAP_FROM = "MAP_FROM"


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateWorkspaceInput(BaseModel):
    workspace: ID
    graph: "GraphInput"
    title: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphInput(BaseModel):
    nodes: Tuple["GraphNodeInput", ...]
    edges: Tuple["GraphEdgeInput", ...]
    globals: Tuple["GlobalArgInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphNodeInput(BaseModel):
    hello: Optional[str] = None
    path: Optional[str] = None
    id: str
    kind: GraphNodeKind
    position: "PositionInput"
    parent_node: Optional[str] = Field(alias="parentNode", default=None)
    ins: Tuple[Tuple["PortInput", ...], ...]
    outs: Tuple[Tuple["PortInput", ...], ...]
    constants: Tuple["PortInput", ...]
    voids: Tuple["PortInput", ...]
    constants_map: Dict = Field(alias="constantsMap")
    globals_map: Dict = Field(alias="globalsMap")
    description: Optional[str] = None
    title: Optional[str] = None
    retries: Optional[int] = None
    retry_delay: Optional[int] = Field(alias="retryDelay", default=None)
    node_kind: Optional[NodeKind] = Field(alias="nodeKind", default=None)
    next_timeout: Optional[int] = Field(alias="nextTimeout", default=None)
    hash: Optional[str] = None
    map_strategy: Optional[MapStrategy] = Field(alias="mapStrategy", default=None)
    allow_local_execution: Optional[bool] = Field(
        alias="allowLocalExecution", default=None
    )
    binds: Optional["BindsInput"] = None
    implementation: Optional[ReactiveImplementation] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PositionInput(BaseModel):
    x: float
    y: float
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PortInput(BaseModel):
    validators: Optional[Tuple["ValidatorInput", ...]] = None
    key: str
    scope: PortScope
    label: Optional[str] = None
    kind: PortKind
    description: Optional[str] = None
    identifier: Optional[str] = None
    nullable: bool
    effects: Optional[Tuple["EffectInput", ...]] = None
    default: Optional[Any] = None
    children: Optional[Tuple["ChildPortInput", ...]] = None
    assign_widget: Optional["AssignWidgetInput"] = Field(
        alias="assignWidget", default=None
    )
    return_widget: Optional["ReturnWidgetInput"] = Field(
        alias="returnWidget", default=None
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ValidatorInput(BaseModel):
    function: ValidatorFunction
    dependencies: Optional[Tuple[str, ...]] = None
    label: Optional[str] = None
    error_message: Optional[str] = Field(alias="errorMessage", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EffectInput(BaseModel):
    function: ValidatorFunction
    dependencies: Tuple[str, ...]
    message: Optional[str] = None
    kind: EffectKind
    hook: Optional[str] = None
    ward: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChildPortInput(BaseModel):
    default: Optional[Any] = None
    key: str
    label: Optional[str] = None
    kind: PortKind
    scope: PortScope
    description: Optional[str] = None
    identifier: Optional[str] = None
    nullable: bool
    children: Optional[Tuple["ChildPortInput", ...]] = None
    effects: Optional[Tuple[EffectInput, ...]] = None
    assign_widget: Optional["AssignWidgetInput"] = Field(
        alias="assignWidget", default=None
    )
    return_widget: Optional["ReturnWidgetInput"] = Field(
        alias="returnWidget", default=None
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AssignWidgetInput(BaseModel):
    as_paragraph: Optional[bool] = Field(alias="asParagraph", default=None)
    kind: AssignWidgetKind
    query: Optional[str] = None
    choices: Optional[Tuple["ChoiceInput", ...]] = None
    state_choices: Optional[str] = Field(alias="stateChoices", default=None)
    follow_value: Optional[str] = Field(alias="followValue", default=None)
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    placeholder: Optional[str] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    fallback: Optional["AssignWidgetInput"] = None
    filters: Optional[Tuple[ChildPortInput, ...]] = None
    dependencies: Optional[Tuple[str, ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChoiceInput(BaseModel):
    value: Any
    label: str
    image: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReturnWidgetInput(BaseModel):
    kind: ReturnWidgetKind
    query: Optional[str] = None
    choices: Optional[Tuple[ChoiceInput, ...]] = None
    min: Optional[int] = None
    max: Optional[int] = None
    step: Optional[int] = None
    placeholder: Optional[str] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BindsInput(BaseModel):
    templates: Optional[Tuple[str, ...]] = None
    clients: Optional[Tuple[str, ...]] = None
    desired_instances: int = Field(alias="desiredInstances")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphEdgeInput(BaseModel):
    label: Optional[str] = None
    level: Optional[str] = None
    kind: GraphEdgeKind
    id: str
    source: str
    target: str
    source_handle: str = Field(alias="sourceHandle")
    target_handle: str = Field(alias="targetHandle")
    stream: Tuple["StreamItemInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StreamItemInput(BaseModel):
    kind: PortKind
    label: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GlobalArgInput(BaseModel):
    key: str
    port: PortInput
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateWorkspaceInput(BaseModel):
    graph: Optional[GraphInput] = None
    title: Optional[str] = None
    description: Optional[str] = None
    vanilla: bool
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateRunInput(BaseModel):
    flow: ID
    snapshot_interval: int = Field(alias="snapshotInterval")
    assignation: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SnapshotRunInput(BaseModel):
    run: ID
    events: Tuple[ID, ...]
    t: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TrackInput(BaseModel):
    reference: str
    t: int
    kind: RunEventKind
    value: Optional[EventValue] = None
    run: ID
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    message: Optional[str] = None
    exception: Optional[str] = None
    source: Optional[str] = None
    handle: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RunFlow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    title: str
    model_config = ConfigDict(frozen=True)


class RunEvents(BaseModel):
    """RunEvent(id, created_at, reference, run, kind, t, caused_by, source, handle, value, exception)"""

    typename: Literal["RunEvent"] = Field(
        alias="__typename", default="RunEvent", exclude=True
    )
    kind: RunEventKind
    "The type of event"
    t: int
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    created_at: datetime = Field(alias="createdAt")
    value: Optional[EventValue] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class Run(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    assignation: ID
    flow: RunFlow
    events: Tuple[RunEvents, ...]
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(frozen=True)


class FlussStringAssignWidget(BaseModel):
    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    placeholder: str
    as_paragraph: bool = Field(alias="asParagraph")
    model_config = ConfigDict(frozen=True)


class FlussSliderAssignWidget(BaseModel):
    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    min: Optional[float] = Field(default=None)
    max: Optional[float] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussSearchAssignWidget(BaseModel):
    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    query: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussCustomAssignWidget(BaseModel):
    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )
    ward: str
    hook: str
    model_config = ConfigDict(frozen=True)


class FlussChoiceAssignWidgetChoices(BaseModel):
    typename: Literal["Choice"] = Field(
        alias="__typename", default="Choice", exclude=True
    )
    value: str
    label: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussChoiceAssignWidget(BaseModel):
    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    choices: Optional[Tuple[FlussChoiceAssignWidgetChoices, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussCustomEffect(BaseModel):
    typename: Literal["CustomEffect"] = Field(
        alias="__typename", default="CustomEffect", exclude=True
    )
    kind: EffectKind
    hook: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussMessageEffect(BaseModel):
    typename: Literal["MessageEffect"] = Field(
        alias="__typename", default="MessageEffect", exclude=True
    )
    kind: EffectKind
    message: str
    model_config = ConfigDict(frozen=True)


class Validator(BaseModel):
    typename: Literal["Validator"] = Field(
        alias="__typename", default="Validator", exclude=True
    )
    function: ValidatorFunction
    dependencies: Optional[Tuple[str, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussCustomReturnWidget(BaseModel):
    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )
    kind: ReturnWidgetKind
    hook: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussChoiceReturnWidgetChoices(BaseModel):
    typename: Literal["Choice"] = Field(
        alias="__typename", default="Choice", exclude=True
    )
    label: str
    value: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussChoiceReturnWidget(BaseModel):
    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )
    choices: Optional[Tuple[FlussChoiceReturnWidgetChoices, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class BaseRekuestMapNode(BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )
    hello: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussBinds(BaseModel):
    typename: Literal["Binds"] = Field(
        alias="__typename", default="Binds", exclude=True
    )
    templates: Tuple[ID, ...]
    model_config = ConfigDict(frozen=True)


class RetriableNodeBase(BaseModel):
    retries: Optional[int] = Field(default=None)
    retry_delay: Optional[int] = Field(default=None, alias="retryDelay")


class RetriableNodeCatch(RetriableNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    retries: Optional[int] = Field(default=None)
    retry_delay: Optional[int] = Field(default=None, alias="retryDelay")


class RetriableNodeRekuestFilterNode(RetriableNodeBase, BaseModel):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class RetriableNodeRekuestMapNode(RetriableNodeBase, BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class AssignableNodeBase(BaseModel):
    next_timeout: Optional[int] = Field(default=None, alias="nextTimeout")


class AssignableNodeCatch(AssignableNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    next_timeout: Optional[int] = Field(default=None, alias="nextTimeout")


class AssignableNodeRekuestFilterNode(AssignableNodeBase, BaseModel):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class AssignableNodeRekuestMapNode(AssignableNodeBase, BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class StreamItem(MockableTrait, BaseModel):
    typename: Literal["StreamItem"] = Field(
        alias="__typename", default="StreamItem", exclude=True
    )
    kind: PortKind
    label: str
    model_config = ConfigDict(frozen=True)


class ListFlowWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ListFlow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    title: str
    created_at: datetime = Field(alias="createdAt")
    workspace: ListFlowWorkspace
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenAssignwidgetBase(BaseModel):
    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenReturnwidgetBase(BaseModel):
    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortNestedChildrenReturnwidgetBase, BaseModel
):
    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortNestedChildrenReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortNestedChildrenReturnwidgetBase, BaseModel
):
    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPortNestedChildren(BaseModel):
    typename: Literal["ChildPort"] = Field(
        alias="__typename", default="ChildPort", exclude=True
    )
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    scope: PortScope
    assign_widget: Optional[
        Annotated[
            Union[
                FlussChildPortNestedChildrenAssignwidgetBaseSliderAssignWidget,
                FlussChildPortNestedChildrenAssignwidgetBaseChoiceAssignWidget,
                FlussChildPortNestedChildrenAssignwidgetBaseSearchAssignWidget,
                FlussChildPortNestedChildrenAssignwidgetBaseStateChoiceAssignWidget,
                FlussChildPortNestedChildrenAssignwidgetBaseStringAssignWidget,
                FlussChildPortNestedChildrenAssignwidgetBaseCustomAssignWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Annotated[
            Union[
                FlussChildPortNestedChildrenReturnwidgetBaseCustomReturnWidget,
                FlussChildPortNestedChildrenReturnwidgetBaseChoiceReturnWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="returnWidget")
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedAssignwidgetBase(BaseModel):
    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortNestedReturnwidgetBase(BaseModel):
    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortNestedReturnwidgetBase, BaseModel
):
    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortNestedReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortNestedReturnwidgetBase, BaseModel
):
    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPortNested(BaseModel):
    typename: Literal["ChildPort"] = Field(
        alias="__typename", default="ChildPort", exclude=True
    )
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    children: Optional[Tuple[FlussChildPortNestedChildren, ...]] = Field(default=None)
    scope: PortScope
    assign_widget: Optional[
        Annotated[
            Union[
                FlussChildPortNestedAssignwidgetBaseSliderAssignWidget,
                FlussChildPortNestedAssignwidgetBaseChoiceAssignWidget,
                FlussChildPortNestedAssignwidgetBaseSearchAssignWidget,
                FlussChildPortNestedAssignwidgetBaseStateChoiceAssignWidget,
                FlussChildPortNestedAssignwidgetBaseStringAssignWidget,
                FlussChildPortNestedAssignwidgetBaseCustomAssignWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Annotated[
            Union[
                FlussChildPortNestedReturnwidgetBaseCustomReturnWidget,
                FlussChildPortNestedReturnwidgetBaseChoiceReturnWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="returnWidget")
    model_config = ConfigDict(frozen=True)


class EvenBasierGraphNodeBase(BaseModel):
    parent_node: Optional[str] = Field(default=None, alias="parentNode")


class EvenBasierGraphNodeCatch(EvenBasierGraphNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    parent_node: Optional[str] = Field(default=None, alias="parentNode")


class EvenBasierGraphNodeRekuestFilterNode(EvenBasierGraphNodeBase, BaseModel):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class EvenBasierGraphNodeRekuestMapNode(
    BaseRekuestMapNode, EvenBasierGraphNodeBase, BaseModel
):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class EvenBasierGraphNodeArgNode(EvenBasierGraphNodeBase, BaseModel):
    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class EvenBasierGraphNodeReturnNode(EvenBasierGraphNodeBase, BaseModel):
    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class EvenBasierGraphNodeReactiveNode(EvenBasierGraphNodeBase, BaseModel):
    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class RekuestNodeBase(BaseModel):
    hash: str
    map_strategy: str = Field(alias="mapStrategy")
    allow_local_execution: bool = Field(alias="allowLocalExecution")
    binds: FlussBinds
    node_kind: NodeKind = Field(alias="nodeKind")


class RekuestNodeCatch(RekuestNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    hash: str
    map_strategy: str = Field(alias="mapStrategy")
    allow_local_execution: bool = Field(alias="allowLocalExecution")
    binds: FlussBinds
    node_kind: NodeKind = Field(alias="nodeKind")


class RekuestNodeRekuestFilterNode(RekuestNodeBase, BaseModel):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class RekuestNodeRekuestMapNode(RekuestNodeBase, BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class BaseGraphEdgeBase(BaseModel):
    id: ID
    source: str
    source_handle: str = Field(alias="sourceHandle")
    target: str
    target_handle: str = Field(alias="targetHandle")
    kind: GraphEdgeKind
    stream: Tuple[StreamItem, ...]


class BaseGraphEdgeCatch(BaseGraphEdgeBase):
    typename: str = Field(alias="__typename", exclude=True)
    id: ID
    source: str
    source_handle: str = Field(alias="sourceHandle")
    target: str
    target_handle: str = Field(alias="targetHandle")
    kind: GraphEdgeKind
    stream: Tuple[StreamItem, ...]


class BaseGraphEdgeVanillaEdge(BaseGraphEdgeBase, BaseModel):
    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )


class BaseGraphEdgeLoggingEdge(BaseGraphEdgeBase, BaseModel):
    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )


class ListWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    title: str
    description: Optional[str] = Field(default=None)
    latest_flow: Optional[ListFlow] = Field(default=None, alias="latestFlow")
    model_config = ConfigDict(frozen=True)


class FlussChildPortAssignwidgetBase(BaseModel):
    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortReturnwidgetBase(BaseModel):
    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortReturnwidgetBase, BaseModel
):
    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortReturnwidgetBase, BaseModel
):
    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPort(BaseModel):
    typename: Literal["ChildPort"] = Field(
        alias="__typename", default="ChildPort", exclude=True
    )
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    scope: PortScope
    children: Optional[Tuple[FlussChildPortNested, ...]] = Field(default=None)
    assign_widget: Optional[
        Annotated[
            Union[
                FlussChildPortAssignwidgetBaseSliderAssignWidget,
                FlussChildPortAssignwidgetBaseChoiceAssignWidget,
                FlussChildPortAssignwidgetBaseSearchAssignWidget,
                FlussChildPortAssignwidgetBaseStateChoiceAssignWidget,
                FlussChildPortAssignwidgetBaseStringAssignWidget,
                FlussChildPortAssignwidgetBaseCustomAssignWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Annotated[
            Union[
                FlussChildPortReturnwidgetBaseCustomReturnWidget,
                FlussChildPortReturnwidgetBaseChoiceReturnWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="returnWidget")
    nullable: bool
    model_config = ConfigDict(frozen=True)


class LoggingEdge(BaseGraphEdgeLoggingEdge, BaseModel):
    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )
    level: str
    model_config = ConfigDict(frozen=True)


class VanillaEdge(BaseGraphEdgeVanillaEdge, BaseModel):
    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )
    label: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussPortEffectsBase(BaseModel):
    kind: EffectKind
    function: ValidatorFunction
    dependencies: Tuple[str, ...]
    model_config = ConfigDict(frozen=True)


class FlussPortEffectsBaseCustomEffect(
    FlussCustomEffect, FlussPortEffectsBase, BaseModel
):
    typename: Literal["CustomEffect"] = Field(
        alias="__typename", default="CustomEffect", exclude=True
    )


class FlussPortEffectsBaseMessageEffect(
    FlussMessageEffect, FlussPortEffectsBase, BaseModel
):
    typename: Literal["MessageEffect"] = Field(
        alias="__typename", default="MessageEffect", exclude=True
    )


class FlussPortAssignwidgetBase(BaseModel):
    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussPortAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseStateChoiceAssignWidget(
    FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussPortReturnwidgetBase(BaseModel):
    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussPortReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussPortReturnwidgetBase, BaseModel
):
    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussPortReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussPortReturnwidgetBase, BaseModel
):
    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussPort(BaseModel):
    typename: Literal["Port"] = Field(alias="__typename", default="Port", exclude=True)
    key: str
    label: Optional[str] = Field(default=None)
    nullable: bool
    description: Optional[str] = Field(default=None)
    scope: PortScope
    effects: Optional[
        Tuple[
            Annotated[
                Union[
                    FlussPortEffectsBaseCustomEffect, FlussPortEffectsBaseMessageEffect
                ],
                Field(discriminator="typename"),
            ],
            ...,
        ]
    ] = Field(default=None)
    assign_widget: Optional[
        Annotated[
            Union[
                FlussPortAssignwidgetBaseSliderAssignWidget,
                FlussPortAssignwidgetBaseChoiceAssignWidget,
                FlussPortAssignwidgetBaseSearchAssignWidget,
                FlussPortAssignwidgetBaseStateChoiceAssignWidget,
                FlussPortAssignwidgetBaseStringAssignWidget,
                FlussPortAssignwidgetBaseCustomAssignWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Annotated[
            Union[
                FlussPortReturnwidgetBaseCustomReturnWidget,
                FlussPortReturnwidgetBaseChoiceReturnWidget,
            ],
            Field(discriminator="typename"),
        ]
    ] = Field(default=None, alias="returnWidget")
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    children: Optional[Tuple[FlussChildPort, ...]] = Field(default=None)
    default: Optional[Any] = Field(default=None)
    nullable: bool
    validators: Optional[Tuple[Validator, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ReactiveTemplate(BaseModel):
    """ReactiveTemplate(id, title, description, implementation, ins, outs, voids, constants)"""

    typename: Literal["ReactiveTemplate"] = Field(
        alias="__typename", default="ReactiveTemplate", exclude=True
    )
    id: ID
    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    implementation: ReactiveImplementation
    "Check async Programming Textbook"
    title: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class BaseGraphNodePosition(BaseModel):
    typename: Literal["Position"] = Field(
        alias="__typename", default="Position", exclude=True
    )
    x: float
    y: float
    model_config = ConfigDict(frozen=True)


class BaseGraphNodeBase(BaseModel):
    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    voids: Tuple[FlussPort, ...]
    id: ID
    position: BaseGraphNodePosition
    parent_node: Optional[str] = Field(default=None, alias="parentNode")
    globals_map: Dict = Field(alias="globalsMap")
    constants_map: Dict = Field(alias="constantsMap")
    title: str
    description: str
    kind: GraphNodeKind


class BaseGraphNodeCatch(BaseGraphNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    voids: Tuple[FlussPort, ...]
    id: ID
    position: BaseGraphNodePosition
    parent_node: Optional[str] = Field(default=None, alias="parentNode")
    globals_map: Dict = Field(alias="globalsMap")
    constants_map: Dict = Field(alias="constantsMap")
    title: str
    description: str
    kind: GraphNodeKind


class BaseGraphNodeRekuestFilterNode(
    EvenBasierGraphNodeRekuestFilterNode, BaseGraphNodeBase, BaseModel
):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class BaseGraphNodeRekuestMapNode(
    EvenBasierGraphNodeRekuestMapNode, BaseGraphNodeBase, BaseModel
):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class BaseGraphNodeArgNode(EvenBasierGraphNodeArgNode, BaseGraphNodeBase, BaseModel):
    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class BaseGraphNodeReturnNode(
    EvenBasierGraphNodeReturnNode, BaseGraphNodeBase, BaseModel
):
    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class BaseGraphNodeReactiveNode(
    EvenBasierGraphNodeReactiveNode, BaseGraphNodeBase, BaseModel
):
    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GlobalArg(BaseModel):
    typename: Literal["GlobalArg"] = Field(
        alias="__typename", default="GlobalArg", exclude=True
    )
    key: str
    port: FlussPort
    model_config = ConfigDict(frozen=True)


class RekuestMapNode(
    RekuestNodeRekuestMapNode,
    AssignableNodeRekuestMapNode,
    RetriableNodeRekuestMapNode,
    BaseGraphNodeRekuestMapNode,
    BaseModel,
):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )
    hello: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class RekuestFilterNode(
    RekuestNodeRekuestFilterNode,
    AssignableNodeRekuestFilterNode,
    RetriableNodeRekuestFilterNode,
    BaseGraphNodeRekuestFilterNode,
    BaseModel,
):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )
    path: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ReactiveNode(BaseGraphNodeReactiveNode, BaseModel):
    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )
    implementation: ReactiveImplementation
    model_config = ConfigDict(frozen=True)


class ArgNode(BaseGraphNodeArgNode, BaseModel):
    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )
    model_config = ConfigDict(frozen=True)


class ReturnNode(BaseGraphNodeReturnNode, BaseModel):
    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )
    model_config = ConfigDict(frozen=True)


class GraphNodeBase(BaseModel):
    kind: GraphNodeKind


class GraphNodeCatch(GraphNodeBase):
    typename: str = Field(alias="__typename", exclude=True)
    kind: GraphNodeKind


class GraphNodeRekuestFilterNode(RekuestFilterNode, GraphNodeBase, BaseModel):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class GraphNodeRekuestMapNode(RekuestMapNode, GraphNodeBase, BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class GraphNodeArgNode(ArgNode, GraphNodeBase, BaseModel):
    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class GraphNodeReturnNode(ReturnNode, GraphNodeBase, BaseModel):
    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class GraphNodeReactiveNode(ReactiveNode, GraphNodeBase, BaseModel):
    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GraphNodesBase(BaseModel):
    pass
    model_config = ConfigDict(frozen=True)


class GraphNodesBaseRekuestFilterNode(
    GraphNodeRekuestFilterNode, GraphNodesBase, BaseModel
):
    typename: Literal["RekuestFilterNode"] = Field(
        alias="__typename", default="RekuestFilterNode", exclude=True
    )


class GraphNodesBaseRekuestMapNode(GraphNodeRekuestMapNode, GraphNodesBase, BaseModel):
    typename: Literal["RekuestMapNode"] = Field(
        alias="__typename", default="RekuestMapNode", exclude=True
    )


class GraphNodesBaseArgNode(GraphNodeArgNode, GraphNodesBase, BaseModel):
    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class GraphNodesBaseReturnNode(GraphNodeReturnNode, GraphNodesBase, BaseModel):
    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class GraphNodesBaseReactiveNode(GraphNodeReactiveNode, GraphNodesBase, BaseModel):
    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GraphEdgesBase(BaseModel):
    pass
    model_config = ConfigDict(frozen=True)


class GraphEdgesBaseVanillaEdge(VanillaEdge, GraphEdgesBase, BaseModel):
    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )


class GraphEdgesBaseLoggingEdge(LoggingEdge, GraphEdgesBase, BaseModel):
    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )


class Graph(BaseModel):
    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    nodes: Tuple[
        Annotated[
            Union[
                GraphNodesBaseRekuestFilterNode,
                GraphNodesBaseRekuestMapNode,
                GraphNodesBaseArgNode,
                GraphNodesBaseReturnNode,
                GraphNodesBaseReactiveNode,
            ],
            Field(discriminator="typename"),
        ],
        ...,
    ]
    edges: Tuple[
        Annotated[
            Union[GraphEdgesBaseVanillaEdge, GraphEdgesBaseLoggingEdge],
            Field(discriminator="typename"),
        ],
        ...,
    ]
    globals: Tuple[GlobalArg, ...]
    model_config = ConfigDict(frozen=True)


class FlowWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class Flow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    graph: Graph
    title: str
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(alias="createdAt")
    workspace: FlowWorkspace
    model_config = ConfigDict(frozen=True)


class Workspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    title: str
    latest_flow: Optional[Flow] = Field(default=None, alias="latestFlow")
    model_config = ConfigDict(frozen=True)


class CreateRunMutationCreaterun(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class CreateRunMutation(BaseModel):
    """Start a run on fluss"""

    create_run: CreateRunMutationCreaterun = Field(alias="createRun")

    class Arguments(BaseModel):
        input: CreateRunInput

    class Meta:
        document = "mutation CreateRun($input: CreateRunInput!) {\n  createRun(input: $input) {\n    id\n    __typename\n  }\n}"


class CloseRunMutationCloserun(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class CloseRunMutation(BaseModel):
    """Start a run on fluss"""

    close_run: CloseRunMutationCloserun = Field(alias="closeRun")

    class Arguments(BaseModel):
        run: ID

    class Meta:
        document = "mutation CloseRun($run: ID!) {\n  closeRun(input: {run: $run}) {\n    id\n    __typename\n  }\n}"


class SnapshotMutationSnapshot(BaseModel):
    """Snapshot(id, created_at, run, t, status)"""

    typename: Literal["Snapshot"] = Field(
        alias="__typename", default="Snapshot", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class SnapshotMutation(BaseModel):
    """Snapshot the current state on the fluss platform"""

    snapshot: SnapshotMutationSnapshot

    class Arguments(BaseModel):
        input: SnapshotRunInput

    class Meta:
        document = "mutation Snapshot($input: SnapshotRunInput!) {\n  snapshot(input: $input) {\n    id\n    __typename\n  }\n}"


class TrackMutationTrack(BaseModel):
    """RunEvent(id, created_at, reference, run, kind, t, caused_by, source, handle, value, exception)"""

    typename: Literal["RunEvent"] = Field(
        alias="__typename", default="RunEvent", exclude=True
    )
    id: ID
    kind: RunEventKind
    "The type of event"
    value: Optional[EventValue] = Field(default=None)
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    model_config = ConfigDict(frozen=True)


class TrackMutation(BaseModel):
    """Track a new event on the fluss platform"""

    track: TrackMutationTrack

    class Arguments(BaseModel):
        input: TrackInput

    class Meta:
        document = "mutation Track($input: TrackInput!) {\n  track(input: $input) {\n    id\n    kind\n    value\n    causedBy\n    __typename\n  }\n}"


class UpdateWorkspaceMutation(BaseModel):
    update_workspace: Workspace = Field(alias="updateWorkspace")

    class Arguments(BaseModel):
        input: UpdateWorkspaceInput

    class Meta:
        document = "fragment BaseRekuestMapNode on RekuestMapNode {\n  hello\n  __typename\n}\n\nfragment FlussBinds on Binds {\n  templates\n  __typename\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n  ...BaseRekuestMapNode\n}\n\nfragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment RekuestNode on RekuestNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  nodeKind\n  __typename\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment RekuestFilterNode on RekuestFilterNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment RekuestMapNode on RekuestMapNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterNode\n  ...RekuestMapNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateWorkspace($input: UpdateWorkspaceInput!) {\n  updateWorkspace(input: $input) {\n    ...Workspace\n    __typename\n  }\n}"


class CreateWorkspaceMutation(BaseModel):
    create_workspace: Workspace = Field(alias="createWorkspace")

    class Arguments(BaseModel):
        input: CreateWorkspaceInput

    class Meta:
        document = "fragment BaseRekuestMapNode on RekuestMapNode {\n  hello\n  __typename\n}\n\nfragment FlussBinds on Binds {\n  templates\n  __typename\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n  ...BaseRekuestMapNode\n}\n\nfragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment RekuestNode on RekuestNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  nodeKind\n  __typename\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment RekuestFilterNode on RekuestFilterNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment RekuestMapNode on RekuestMapNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterNode\n  ...RekuestMapNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nmutation CreateWorkspace($input: CreateWorkspaceInput!) {\n  createWorkspace(input: $input) {\n    ...Workspace\n    __typename\n  }\n}"


class RunQuery(BaseModel):
    run: Run

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Run on Run {\n  id\n  assignation\n  flow {\n    id\n    title\n    __typename\n  }\n  events {\n    kind\n    t\n    causedBy\n    createdAt\n    value\n    __typename\n  }\n  createdAt\n  __typename\n}\n\nquery Run($id: ID!) {\n  run(id: $id) {\n    ...Run\n    __typename\n  }\n}"


class SearchRunsQueryOptions(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    value: ID
    label: ID
    model_config = ConfigDict(frozen=True)


class SearchRunsQuery(BaseModel):
    options: Tuple[SearchRunsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchRuns($search: String, $values: [ID!]) {\n  options: runs(filters: {search: $search, ids: $values}) {\n    value: id\n    label: assignation\n    __typename\n  }\n}"


class WorkspaceQuery(BaseModel):
    workspace: Workspace

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment BaseRekuestMapNode on RekuestMapNode {\n  hello\n  __typename\n}\n\nfragment FlussBinds on Binds {\n  templates\n  __typename\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n  ...BaseRekuestMapNode\n}\n\nfragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment RekuestNode on RekuestNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  nodeKind\n  __typename\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment RekuestFilterNode on RekuestFilterNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment RekuestMapNode on RekuestMapNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterNode\n  ...RekuestMapNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nquery Workspace($id: ID!) {\n  workspace(id: $id) {\n    ...Workspace\n    __typename\n  }\n}"


class WorkspacesQuery(BaseModel):
    workspaces: Tuple[ListWorkspace, ...]

    class Arguments(BaseModel):
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment ListFlow on Flow {\n  id\n  title\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment ListWorkspace on Workspace {\n  id\n  title\n  description\n  latestFlow {\n    ...ListFlow\n    __typename\n  }\n  __typename\n}\n\nquery Workspaces($pagination: OffsetPaginationInput) {\n  workspaces(pagination: $pagination) {\n    ...ListWorkspace\n    __typename\n  }\n}"


class ReactiveTemplatesQuery(BaseModel):
    reactive_templates: Tuple[ReactiveTemplate, ...] = Field(alias="reactiveTemplates")

    class Arguments(BaseModel):
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ReactiveTemplate on ReactiveTemplate {\n  id\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  implementation\n  title\n  description\n  __typename\n}\n\nquery ReactiveTemplates($pagination: OffsetPaginationInput) {\n  reactiveTemplates(pagination: $pagination) {\n    ...ReactiveTemplate\n    __typename\n  }\n}"


class ReactiveTemplateQuery(BaseModel):
    reactive_template: ReactiveTemplate = Field(alias="reactiveTemplate")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ReactiveTemplate on ReactiveTemplate {\n  id\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  implementation\n  title\n  description\n  __typename\n}\n\nquery ReactiveTemplate($id: ID!) {\n  reactiveTemplate(id: $id) {\n    ...ReactiveTemplate\n    __typename\n  }\n}"


class GetFlowQuery(BaseModel):
    flow: Flow

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment BaseRekuestMapNode on RekuestMapNode {\n  hello\n  __typename\n}\n\nfragment FlussBinds on Binds {\n  templates\n  __typename\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n  ...BaseRekuestMapNode\n}\n\nfragment FlussChildPortNested on ChildPort {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    scope\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  scope\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment RekuestNode on RekuestNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  nodeKind\n  __typename\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment FlussChildPort on ChildPort {\n  __typename\n  kind\n  identifier\n  scope\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment RekuestFilterNode on RekuestFilterNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  scope\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment RekuestMapNode on RekuestMapNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterNode\n  ...RekuestMapNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nquery GetFlow($id: ID!) {\n  flow(id: $id) {\n    ...Flow\n    __typename\n  }\n}"


class FlowsQuery(BaseModel):
    flows: Tuple[ListFlow, ...]

    class Arguments(BaseModel):
        limit: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment ListFlow on Flow {\n  id\n  title\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n  __typename\n}\n\nquery Flows($limit: Int) {\n  flows(pagination: {limit: $limit}) {\n    ...ListFlow\n    __typename\n  }\n}"


class SearchFlowsQueryOptions(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchFlowsQuery(BaseModel):
    options: Tuple[SearchFlowsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchFlows($search: String, $values: [ID!]) {\n  options: flows(filters: {search: $search, ids: $values}) {\n    value: id\n    label: title\n    __typename\n  }\n}"


async def acreate_run(
    flow: ID, snapshot_interval: int, assignation: ID, rath: Optional[FlussRath] = None
) -> CreateRunMutationCreaterun:
    """CreateRun
     Start a run on fluss

    Arguments:
        flow: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        snapshot_interval: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        assignation: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateRunMutationCreaterun"""
    return (
        await aexecute(
            CreateRunMutation,
            {
                "input": {
                    "flow": flow,
                    "snapshotInterval": snapshot_interval,
                    "assignation": assignation,
                }
            },
            rath=rath,
        )
    ).create_run


def create_run(
    flow: ID, snapshot_interval: int, assignation: ID, rath: Optional[FlussRath] = None
) -> CreateRunMutationCreaterun:
    """CreateRun
     Start a run on fluss

    Arguments:
        flow: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        snapshot_interval: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        assignation: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateRunMutationCreaterun"""
    return execute(
        CreateRunMutation,
        {
            "input": {
                "flow": flow,
                "snapshotInterval": snapshot_interval,
                "assignation": assignation,
            }
        },
        rath=rath,
    ).create_run


async def aclose_run(
    run: ID, rath: Optional[FlussRath] = None
) -> CloseRunMutationCloserun:
    """CloseRun
     Start a run on fluss

    Arguments:
        run (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CloseRunMutationCloserun"""
    return (await aexecute(CloseRunMutation, {"run": run}, rath=rath)).close_run


def close_run(run: ID, rath: Optional[FlussRath] = None) -> CloseRunMutationCloserun:
    """CloseRun
     Start a run on fluss

    Arguments:
        run (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CloseRunMutationCloserun"""
    return execute(CloseRunMutation, {"run": run}, rath=rath).close_run


async def asnapshot(
    run: ID, events: Iterable[ID], t: int, rath: Optional[FlussRath] = None
) -> SnapshotMutationSnapshot:
    """Snapshot
     Snapshot the current state on the fluss platform

    Arguments:
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        events: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        SnapshotMutationSnapshot"""
    return (
        await aexecute(
            SnapshotMutation,
            {"input": {"run": run, "events": events, "t": t}},
            rath=rath,
        )
    ).snapshot


def snapshot(
    run: ID, events: Iterable[ID], t: int, rath: Optional[FlussRath] = None
) -> SnapshotMutationSnapshot:
    """Snapshot
     Snapshot the current state on the fluss platform

    Arguments:
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        events: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        SnapshotMutationSnapshot"""
    return execute(
        SnapshotMutation, {"input": {"run": run, "events": events, "t": t}}, rath=rath
    ).snapshot


async def atrack(
    reference: str,
    t: int,
    kind: RunEventKind,
    run: ID,
    caused_by: Iterable[ID],
    value: Optional[EventValue] = None,
    message: Optional[str] = None,
    exception: Optional[str] = None,
    source: Optional[str] = None,
    handle: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> TrackMutationTrack:
    """Track
     Track a new event on the fluss platform

    Arguments:
        reference: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        kind: RunEventKind (required)
        value: The `ArrayLike` scalasr typsse represents a reference to a store previously created by the user n a datalayer
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        caused_by: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        message: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        exception: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        source: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        handle: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        TrackMutationTrack"""
    return (
        await aexecute(
            TrackMutation,
            {
                "input": {
                    "reference": reference,
                    "t": t,
                    "kind": kind,
                    "value": value,
                    "run": run,
                    "causedBy": caused_by,
                    "message": message,
                    "exception": exception,
                    "source": source,
                    "handle": handle,
                }
            },
            rath=rath,
        )
    ).track


def track(
    reference: str,
    t: int,
    kind: RunEventKind,
    run: ID,
    caused_by: Iterable[ID],
    value: Optional[EventValue] = None,
    message: Optional[str] = None,
    exception: Optional[str] = None,
    source: Optional[str] = None,
    handle: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> TrackMutationTrack:
    """Track
     Track a new event on the fluss platform

    Arguments:
        reference: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        kind: RunEventKind (required)
        value: The `ArrayLike` scalasr typsse represents a reference to a store previously created by the user n a datalayer
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        caused_by: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        message: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        exception: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        source: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        handle: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        TrackMutationTrack"""
    return execute(
        TrackMutation,
        {
            "input": {
                "reference": reference,
                "t": t,
                "kind": kind,
                "value": value,
                "run": run,
                "causedBy": caused_by,
                "message": message,
                "exception": exception,
                "source": source,
                "handle": handle,
            }
        },
        rath=rath,
    ).track


async def aupdate_workspace(
    workspace: ID,
    graph: GraphInput,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """UpdateWorkspace


    Arguments:
        workspace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        graph:  (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return (
        await aexecute(
            UpdateWorkspaceMutation,
            {
                "input": {
                    "workspace": workspace,
                    "graph": graph,
                    "title": title,
                    "description": description,
                }
            },
            rath=rath,
        )
    ).update_workspace


def update_workspace(
    workspace: ID,
    graph: GraphInput,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """UpdateWorkspace


    Arguments:
        workspace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        graph:  (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return execute(
        UpdateWorkspaceMutation,
        {
            "input": {
                "workspace": workspace,
                "graph": graph,
                "title": title,
                "description": description,
            }
        },
        rath=rath,
    ).update_workspace


async def acreate_workspace(
    vanilla: bool,
    graph: Optional[GraphInput] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """CreateWorkspace


    Arguments:
        graph:
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vanilla: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return (
        await aexecute(
            CreateWorkspaceMutation,
            {
                "input": {
                    "graph": graph,
                    "title": title,
                    "description": description,
                    "vanilla": vanilla,
                }
            },
            rath=rath,
        )
    ).create_workspace


def create_workspace(
    vanilla: bool,
    graph: Optional[GraphInput] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """CreateWorkspace


    Arguments:
        graph:
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vanilla: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return execute(
        CreateWorkspaceMutation,
        {
            "input": {
                "graph": graph,
                "title": title,
                "description": description,
                "vanilla": vanilla,
            }
        },
        rath=rath,
    ).create_workspace


async def arun(id: ID, rath: Optional[FlussRath] = None) -> Run:
    """Run


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Run"""
    return (await aexecute(RunQuery, {"id": id}, rath=rath)).run


def run(id: ID, rath: Optional[FlussRath] = None) -> Run:
    """Run


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Run"""
    return execute(RunQuery, {"id": id}, rath=rath).run


async def asearch_runs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchRunsQueryOptions, ...]:
    """SearchRuns


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchRunsQueryRuns]"""
    return (
        await aexecute(SearchRunsQuery, {"search": search, "values": values}, rath=rath)
    ).options


def search_runs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchRunsQueryOptions, ...]:
    """SearchRuns


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchRunsQueryRuns]"""
    return execute(
        SearchRunsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aworkspace(id: ID, rath: Optional[FlussRath] = None) -> Workspace:
    """Workspace


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return (await aexecute(WorkspaceQuery, {"id": id}, rath=rath)).workspace


def workspace(id: ID, rath: Optional[FlussRath] = None) -> Workspace:
    """Workspace


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace"""
    return execute(WorkspaceQuery, {"id": id}, rath=rath).workspace


async def aworkspaces(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListWorkspace, ...]:
    """Workspaces


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListWorkspace]"""
    return (
        await aexecute(WorkspacesQuery, {"pagination": pagination}, rath=rath)
    ).workspaces


def workspaces(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListWorkspace, ...]:
    """Workspaces


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListWorkspace]"""
    return execute(WorkspacesQuery, {"pagination": pagination}, rath=rath).workspaces


async def areactive_templates(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ReactiveTemplate, ...]:
    """ReactiveTemplates


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ReactiveTemplate]"""
    return (
        await aexecute(ReactiveTemplatesQuery, {"pagination": pagination}, rath=rath)
    ).reactive_templates


def reactive_templates(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ReactiveTemplate, ...]:
    """ReactiveTemplates


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ReactiveTemplate]"""
    return execute(
        ReactiveTemplatesQuery, {"pagination": pagination}, rath=rath
    ).reactive_templates


async def areactive_template(
    id: ID, rath: Optional[FlussRath] = None
) -> ReactiveTemplate:
    """ReactiveTemplate


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReactiveTemplate"""
    return (
        await aexecute(ReactiveTemplateQuery, {"id": id}, rath=rath)
    ).reactive_template


def reactive_template(id: ID, rath: Optional[FlussRath] = None) -> ReactiveTemplate:
    """ReactiveTemplate


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReactiveTemplate"""
    return execute(ReactiveTemplateQuery, {"id": id}, rath=rath).reactive_template


async def aget_flow(id: ID, rath: Optional[FlussRath] = None) -> Flow:
    """GetFlow


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flow"""
    return (await aexecute(GetFlowQuery, {"id": id}, rath=rath)).flow


def get_flow(id: ID, rath: Optional[FlussRath] = None) -> Flow:
    """GetFlow


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flow"""
    return execute(GetFlowQuery, {"id": id}, rath=rath).flow


async def aflows(
    limit: Optional[int] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListFlow, ...]:
    """Flows


    Arguments:
        limit (Optional[int], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListFlow]"""
    return (await aexecute(FlowsQuery, {"limit": limit}, rath=rath)).flows


def flows(
    limit: Optional[int] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListFlow, ...]:
    """Flows


    Arguments:
        limit (Optional[int], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListFlow]"""
    return execute(FlowsQuery, {"limit": limit}, rath=rath).flows


async def asearch_flows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchFlowsQueryOptions, ...]:
    """SearchFlows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlowsQueryFlows]"""
    return (
        await aexecute(
            SearchFlowsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_flows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchFlowsQueryOptions, ...]:
    """SearchFlows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlowsQueryFlows]"""
    return execute(
        SearchFlowsQuery, {"search": search, "values": values}, rath=rath
    ).options


AssignWidgetInput.model_rebuild()
ChildPortInput.model_rebuild()
GraphEdgeInput.model_rebuild()
GraphInput.model_rebuild()
GraphNodeInput.model_rebuild()
PortInput.model_rebuild()
UpdateWorkspaceInput.model_rebuild()
