from pydantic import ConfigDict, Field, BaseModel
from rekuest_next.scalars import SearchQuery, ValidatorFunction, Identifier, NodeHash
from kabinet.rath import KabinetRath
from typing import Literal, Iterable, Optional, List, Tuple, Annotated, Any, Union
from kabinet.funcs import execute, aexecute
from datetime import datetime
from rath.scalars import ID
from enum import Enum


class AssignWidgetKind(str, Enum):
    SEARCH = "SEARCH"
    CHOICE = "CHOICE"
    SLIDER = "SLIDER"
    CUSTOM = "CUSTOM"
    STRING = "STRING"
    STATE_CHOICE = "STATE_CHOICE"


class ContainerType(str, Enum):
    """The state of a dask cluster"""

    APPTAINER = "APPTAINER"
    DOCKER = "DOCKER"


class EffectKind(str, Enum):
    MESSAGE = "MESSAGE"
    HIDE = "HIDE"
    CUSTOM = "CUSTOM"


class NodeKind(str, Enum):
    FUNCTION = "FUNCTION"
    GENERATOR = "GENERATOR"


class PodStatus(str, Enum):
    """The state of a dask cluster"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    UNKOWN = "UNKOWN"


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


class PortScope(str, Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"


class ReturnWidgetKind(str, Enum):
    CHOICE = "CHOICE"
    CUSTOM = "CUSTOM"


class CpuSelectorInput(BaseModel):
    kind: Literal["cpu"] = Field(default="cpu")
    frequency: Optional[int] = None
    "The frequency in MHz"
    memory: Optional[int] = None
    "The memory in MB"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CudaSelectorInput(BaseModel):
    kind: Literal["cuda"] = Field(default="cuda")
    cuda_version: Optional[str] = Field(alias="cudaVersion", default=None)
    "The minimum cuda version"
    cuda_cores: Optional[int] = Field(alias="cudaCores", default=None)
    "The cuda cores"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OneApiSelectorInput(BaseModel):
    kind: Literal["oneapi"] = Field(default="oneapi")
    oneapi_version: Optional[str] = Field(alias="oneapiVersion", default=None)
    "The api versison of the selector"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RocmSelectorInput(BaseModel):
    kind: Literal["rocm"] = Field(default="rocm")
    api_version: Optional[str] = Field(alias="apiVersion", default=None)
    "The api version of the selector"
    api_thing: Optional[str] = Field(alias="apiThing", default=None)
    "The api thing of the selector"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AppImageInput(BaseModel):
    """Create a new Github repository input"""

    flavour_name: Optional[str] = Field(alias="flavourName", default=None)
    manifest: "ManifestInput"
    selectors: Tuple["SelectorInput", ...]
    app_image_id: str = Field(alias="appImageId")
    inspection: "InspectionInput"
    image: "DockerImageInput"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AssignWidgetInput(BaseModel):
    as_paragraph: Optional[bool] = Field(alias="asParagraph", default=None)
    kind: AssignWidgetKind
    query: Optional[SearchQuery] = None
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
    filters: Optional[Tuple["ChildPortInput", ...]] = None
    dependencies: Optional[Tuple[str, ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BackendFilter(BaseModel):
    """Filter for Resources"""

    ids: Optional[Tuple[ID, ...]] = None
    search: Optional[str] = None
    and_: Optional["BackendFilter"] = Field(alias="AND", default=None)
    or_: Optional["BackendFilter"] = Field(alias="OR", default=None)
    not_: Optional["BackendFilter"] = Field(alias="NOT", default=None)
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


class ChildPortInput(BaseModel):
    default: Optional[Any] = None
    key: str
    label: Optional[str] = None
    kind: PortKind
    scope: PortScope
    description: Optional[str] = None
    identifier: Optional[Identifier] = None
    nullable: bool
    children: Optional[Tuple["ChildPortInput", ...]] = None
    effects: Optional[Tuple["EffectInput", ...]] = None
    assign_widget: Optional[AssignWidgetInput] = Field(
        alias="assignWidget", default=None
    )
    return_widget: Optional["ReturnWidgetInput"] = Field(
        alias="returnWidget", default=None
    )
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


class CreateDeploymentInput(BaseModel):
    """Create a new Github repository input"""

    instance_id: str = Field(alias="instanceId")
    local_id: ID = Field(alias="localId")
    flavour: ID
    last_pulled: Optional[datetime] = Field(alias="lastPulled", default=None)
    secret_params: Optional[Any] = Field(alias="secretParams", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateGithubRepoInput(BaseModel):
    """Create a new Github repository input"""

    name: Optional[str] = None
    user: Optional[str] = None
    branch: Optional[str] = None
    repo: Optional[str] = None
    identifier: Optional[str] = None
    auto_scan: Optional[bool] = Field(alias="autoScan", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreatePodInput(BaseModel):
    """Create a new Github repository input"""

    deployment: ID
    local_id: ID = Field(alias="localId")
    resource: Optional[ID] = None
    instance_id: str = Field(alias="instanceId")
    client_id: Optional[str] = Field(alias="clientId", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeclareBackendInput(BaseModel):
    """Create a new Github repository input"""

    instance_id: str = Field(alias="instanceId")
    name: str
    kind: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeclareResourceInput(BaseModel):
    """Create a resource"""

    backend: ID
    name: Optional[str] = None
    local_id: str = Field(alias="localId")
    qualifiers: Optional[Tuple["QualifierInput", ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DefinitionInput(BaseModel):
    description: Optional[str] = None
    collections: Tuple[str, ...]
    name: str
    stateful: bool
    port_groups: Tuple["PortGroupInput", ...] = Field(alias="portGroups")
    args: Tuple["PortInput", ...]
    returns: Tuple["PortInput", ...]
    kind: NodeKind
    is_test_for: Tuple[str, ...] = Field(alias="isTestFor")
    interfaces: Tuple[str, ...]
    is_dev: bool = Field(alias="isDev")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeletePodInput(BaseModel):
    id: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DependencyInput(BaseModel):
    hash: Optional[NodeHash] = None
    reference: Optional[str] = None
    binds: Optional[BindsInput] = None
    optional: bool
    viable_instances: Optional[int] = Field(alias="viableInstances", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeviceFeature(BaseModel):
    """The Feature you are trying to match"""

    kind: str
    cpu_count: str = Field(alias="cpuCount")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DockerImageInput(BaseModel):
    image_string: str = Field(alias="imageString")
    build_at: datetime = Field(alias="buildAt")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DumpLogsInput(BaseModel):
    """Create a new Github repository input"""

    pod: ID
    logs: str
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


class EnvironmentInput(BaseModel):
    """Which environment do you want to match against?"""

    features: Optional[Tuple[DeviceFeature, ...]] = None
    container_type: ContainerType = Field(alias="containerType")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class InspectionInput(BaseModel):
    size: Optional[int] = None
    templates: Tuple["TemplateInput", ...]
    requirements: Tuple["RequirementInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ManifestInput(BaseModel):
    entrypoint: Optional[str] = None
    "The entrypoint of the app, defaults to 'app'"
    identifier: str
    version: str
    author: str
    logo: Optional[str] = None
    scopes: Tuple[str, ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PortGroupInput(BaseModel):
    key: str
    title: Optional[str] = None
    description: Optional[str] = None
    effects: Optional[Tuple[EffectInput, ...]] = None
    ports: Optional[Tuple[str, ...]] = None
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
    effects: Optional[Tuple[EffectInput, ...]] = None
    default: Optional[Any] = None
    children: Optional[Tuple[ChildPortInput, ...]] = None
    assign_widget: Optional[AssignWidgetInput] = Field(
        alias="assignWidget", default=None
    )
    return_widget: Optional["ReturnWidgetInput"] = Field(
        alias="returnWidget", default=None
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class QualifierInput(BaseModel):
    """A qualifier that describes some property of the node"""

    key: str
    value: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequirementInput(BaseModel):
    key: str
    service: str
    optional: bool
    description: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ResourceFilter(BaseModel):
    """Filter for Resources"""

    ids: Optional[Tuple[ID, ...]] = None
    search: Optional[str] = None
    and_: Optional["ResourceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ResourceFilter"] = Field(alias="OR", default=None)
    not_: Optional["ResourceFilter"] = Field(alias="NOT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReturnWidgetInput(BaseModel):
    kind: ReturnWidgetKind
    query: Optional[SearchQuery] = None
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


SelectorInput = Annotated[
    Union[CpuSelectorInput, CudaSelectorInput, OneApiSelectorInput, RocmSelectorInput],
    Field(discriminator="kind"),
]


class TemplateInput(BaseModel):
    definition: DefinitionInput
    dependencies: Tuple[DependencyInput, ...]
    interface: str
    params: Optional[Any] = None
    dynamic: bool
    logo: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdatePodInput(BaseModel):
    """Create a new Github repository input"""

    pod: Optional[ID] = None
    local_id: Optional[ID] = Field(alias="localId", default=None)
    status: PodStatus
    instance_id: str = Field(alias="instanceId")
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


class Deployment(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Deployment"] = Field(
        alias="__typename", default="Deployment", exclude=True
    )
    id: ID
    local_id: ID = Field(alias="localId")
    model_config = ConfigDict(frozen=True)


class ListDeployment(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Deployment"] = Field(
        alias="__typename", default="Deployment", exclude=True
    )
    id: ID
    local_id: ID = Field(alias="localId")
    model_config = ConfigDict(frozen=True)


class GithubRepoFlavoursDefinitions(BaseModel):
    """Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation"""

    typename: Literal["Definition"] = Field(
        alias="__typename", default="Definition", exclude=True
    )
    id: ID
    hash: NodeHash
    "The hash of the Node (completely unique)"
    model_config = ConfigDict(frozen=True)


class GithubRepoFlavours(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Flavour"] = Field(
        alias="__typename", default="Flavour", exclude=True
    )
    definitions: Tuple[GithubRepoFlavoursDefinitions, ...]
    "The flavours this Definition belongs to"
    model_config = ConfigDict(frozen=True)


class GithubRepo(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["GithubRepo"] = Field(
        alias="__typename", default="GithubRepo", exclude=True
    )
    id: ID
    branch: str
    user: str
    repo: str
    flavours: Tuple[GithubRepoFlavours, ...]
    model_config = ConfigDict(frozen=True)


class ListPod(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Pod"] = Field(alias="__typename", default="Pod", exclude=True)
    id: ID
    pod_id: str = Field(alias="podId")
    model_config = ConfigDict(frozen=True)


class CudaSelector(BaseModel):
    """A selector is a way to select a release"""

    typename: Literal["CudaSelector"] = Field(
        alias="__typename", default="CudaSelector", exclude=True
    )
    cuda_version: Optional[str] = Field(default=None, alias="cudaVersion")
    "The minimum cuda version"
    cuda_cores: Optional[int] = Field(default=None, alias="cudaCores")
    "The number of cuda cores"
    model_config = ConfigDict(frozen=True)


class RocmSelector(BaseModel):
    """A selector is a way to select a release"""

    typename: Literal["RocmSelector"] = Field(
        alias="__typename", default="RocmSelector", exclude=True
    )
    api_version: Optional[str] = Field(default=None, alias="apiVersion")
    api_thing: Optional[str] = Field(default=None, alias="apiThing")
    model_config = ConfigDict(frozen=True)


class ResourceBackend(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Backend"] = Field(
        alias="__typename", default="Backend", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ResourcePods(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Pod"] = Field(alias="__typename", default="Pod", exclude=True)
    id: ID
    pod_id: str = Field(alias="podId")
    model_config = ConfigDict(frozen=True)


class Resource(BaseModel):
    """A resource on a backend. Resource define allocated resources on a backend. E.g a computational node"""

    typename: Literal["Resource"] = Field(
        alias="__typename", default="Resource", exclude=True
    )
    id: ID
    name: str
    qualifiers: Optional[Any] = Field(default=None)
    backend: ResourceBackend
    pods: Tuple[ResourcePods, ...]
    model_config = ConfigDict(frozen=True)


class ListResourceBackend(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Backend"] = Field(
        alias="__typename", default="Backend", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ListResource(BaseModel):
    """A resource on a backend. Resource define allocated resources on a backend. E.g a computational node"""

    typename: Literal["Resource"] = Field(
        alias="__typename", default="Resource", exclude=True
    )
    id: ID
    name: str
    qualifiers: Optional[Any] = Field(default=None)
    backend: ListResourceBackend
    model_config = ConfigDict(frozen=True)


class ListDefinition(BaseModel):
    """Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation"""

    typename: Literal["Definition"] = Field(
        alias="__typename", default="Definition", exclude=True
    )
    id: ID
    name: str
    "The cleartext name of this Node"
    hash: NodeHash
    "The hash of the Node (completely unique)"
    description: Optional[str] = Field(default=None)
    "A description for the Node"
    model_config = ConfigDict(frozen=True)


class Definition(BaseModel):
    """Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation"""

    typename: Literal["Definition"] = Field(
        alias="__typename", default="Definition", exclude=True
    )
    id: ID
    name: str
    "The cleartext name of this Node"
    model_config = ConfigDict(frozen=True)


class Backend(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Backend"] = Field(
        alias="__typename", default="Backend", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ListBackend(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Backend"] = Field(
        alias="__typename", default="Backend", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ListFlavourImage(BaseModel):
    """A docker image descriptor"""

    typename: Literal["DockerImage"] = Field(
        alias="__typename", default="DockerImage", exclude=True
    )
    image_string: str = Field(alias="imageString")
    build_at: datetime = Field(alias="buildAt")
    model_config = ConfigDict(frozen=True)


class ListFlavourRequirements(BaseModel):
    """A requirement"""

    typename: Literal["Requirement"] = Field(
        alias="__typename", default="Requirement", exclude=True
    )
    key: str
    service: str
    description: Optional[str] = Field(default=None)
    optional: bool
    model_config = ConfigDict(frozen=True)


class ListFlavourImage(BaseModel):
    """A docker image descriptor"""

    typename: Literal["DockerImage"] = Field(
        alias="__typename", default="DockerImage", exclude=True
    )
    image_string: str = Field(alias="imageString")
    build_at: datetime = Field(alias="buildAt")
    model_config = ConfigDict(frozen=True)


class ListFlavourSelectorsBase(BaseModel):
    """A selector is a way to select a release"""

    model_config = ConfigDict(frozen=True)


class ListFlavourSelectorsBaseCPUSelector(ListFlavourSelectorsBase, BaseModel):
    typename: Literal["CPUSelector"] = Field(
        alias="__typename", default="CPUSelector", exclude=True
    )


class ListFlavourSelectorsBaseCudaSelector(
    CudaSelector, ListFlavourSelectorsBase, BaseModel
):
    typename: Literal["CudaSelector"] = Field(
        alias="__typename", default="CudaSelector", exclude=True
    )


class ListFlavourSelectorsBaseRocmSelector(
    RocmSelector, ListFlavourSelectorsBase, BaseModel
):
    typename: Literal["RocmSelector"] = Field(
        alias="__typename", default="RocmSelector", exclude=True
    )


class ListFlavour(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Flavour"] = Field(
        alias="__typename", default="Flavour", exclude=True
    )
    id: ID
    name: str
    image: ListFlavourImage
    manifest: Any
    requirements: Tuple[ListFlavourRequirements, ...]
    image: ListFlavourImage
    selectors: Tuple[
        Annotated[
            Union[
                ListFlavourSelectorsBaseCPUSelector,
                ListFlavourSelectorsBaseCudaSelector,
                ListFlavourSelectorsBaseRocmSelector,
            ],
            Field(discriminator="typename"),
        ],
        ...,
    ]
    model_config = ConfigDict(frozen=True)


class ReleaseApp(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    identifier: str
    model_config = ConfigDict(frozen=True)


class Release(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    id: ID
    version: str
    app: ReleaseApp
    scopes: Tuple[str, ...]
    colour: str
    "Is this release deployed"
    description: str
    "Is this release deployed"
    flavours: Tuple[ListFlavour, ...]
    model_config = ConfigDict(frozen=True)


class ListReleaseApp(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    identifier: str
    model_config = ConfigDict(frozen=True)


class ListRelease(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    id: ID
    version: str
    app: ListReleaseApp
    installed: bool
    "Is this release deployed"
    scopes: Tuple[str, ...]
    flavours: Tuple[ListFlavour, ...]
    colour: str
    "Is this release deployed"
    description: str
    "Is this release deployed"
    model_config = ConfigDict(frozen=True)


class FlavourReleaseApp(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    identifier: str
    model_config = ConfigDict(frozen=True)


class FlavourRelease(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    id: ID
    version: str
    app: FlavourReleaseApp
    scopes: Tuple[str, ...]
    colour: str
    "Is this release deployed"
    description: str
    "Is this release deployed"
    model_config = ConfigDict(frozen=True)


class Flavour(ListFlavour, BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Flavour"] = Field(
        alias="__typename", default="Flavour", exclude=True
    )
    release: FlavourRelease
    model_config = ConfigDict(frozen=True)


class PodDeployment(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Deployment"] = Field(
        alias="__typename", default="Deployment", exclude=True
    )
    flavour: Flavour
    model_config = ConfigDict(frozen=True)


class Pod(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Pod"] = Field(alias="__typename", default="Pod", exclude=True)
    id: ID
    pod_id: str = Field(alias="podId")
    deployment: PodDeployment
    model_config = ConfigDict(frozen=True)


class CreateDeploymentMutation(BaseModel):
    create_deployment: Deployment = Field(alias="createDeployment")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: CreateDeploymentInput

    class Meta:
        document = "fragment Deployment on Deployment {\n  id\n  localId\n  __typename\n}\n\nmutation CreateDeployment($input: CreateDeploymentInput!) {\n  createDeployment(input: $input) {\n    ...Deployment\n    __typename\n  }\n}"


class CreatePodMutation(BaseModel):
    create_pod: Pod = Field(alias="createPod")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: CreatePodInput

    class Meta:
        document = "fragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Flavour on Flavour {\n  ...ListFlavour\n  release {\n    id\n    version\n    app {\n      identifier\n      __typename\n    }\n    scopes\n    colour\n    description\n    __typename\n  }\n  __typename\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreatePod($input: CreatePodInput!) {\n  createPod(input: $input) {\n    ...Pod\n    __typename\n  }\n}"


class UpdatePodMutation(BaseModel):
    update_pod: Pod = Field(alias="updatePod")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: UpdatePodInput

    class Meta:
        document = "fragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Flavour on Flavour {\n  ...ListFlavour\n  release {\n    id\n    version\n    app {\n      identifier\n      __typename\n    }\n    scopes\n    colour\n    description\n    __typename\n  }\n  __typename\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation UpdatePod($input: UpdatePodInput!) {\n  updatePod(input: $input) {\n    ...Pod\n    __typename\n  }\n}"


class DeletePodMutation(BaseModel):
    delete_pod: ID = Field(alias="deletePod")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: DeletePodInput

    class Meta:
        document = "mutation DeletePod($input: DeletePodInput!) {\n  deletePod(input: $input)\n}"


class DumpLogsMutationDumplogsPod(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Pod"] = Field(alias="__typename", default="Pod", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class DumpLogsMutationDumplogs(BaseModel):
    """The logs of a pod"""

    typename: Literal["LogDump"] = Field(
        alias="__typename", default="LogDump", exclude=True
    )
    pod: DumpLogsMutationDumplogsPod
    logs: str
    model_config = ConfigDict(frozen=True)


class DumpLogsMutation(BaseModel):
    dump_logs: DumpLogsMutationDumplogs = Field(alias="dumpLogs")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: DumpLogsInput

    class Meta:
        document = "mutation DumpLogs($input: DumpLogsInput!) {\n  dumpLogs(input: $input) {\n    pod {\n      id\n      __typename\n    }\n    logs\n    __typename\n  }\n}"


class CreateAppImageMutation(BaseModel):
    create_app_image: Release = Field(alias="createAppImage")
    "Create a new release"

    class Arguments(BaseModel):
        input: AppImageInput

    class Meta:
        document = "fragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Release on Release {\n  id\n  version\n  app {\n    identifier\n    __typename\n  }\n  scopes\n  colour\n  description\n  flavours {\n    ...ListFlavour\n    __typename\n  }\n  __typename\n}\n\nmutation CreateAppImage($input: AppImageInput!) {\n  createAppImage(input: $input) {\n    ...Release\n    __typename\n  }\n}"


class CreateGithubRepoMutation(BaseModel):
    create_github_repo: GithubRepo = Field(alias="createGithubRepo")
    "Create a new Github repository on a bridge server"

    class Arguments(BaseModel):
        input: CreateGithubRepoInput

    class Meta:
        document = "fragment GithubRepo on GithubRepo {\n  id\n  branch\n  user\n  repo\n  flavours {\n    definitions {\n      id\n      hash\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateGithubRepo($input: CreateGithubRepoInput!) {\n  createGithubRepo(input: $input) {\n    ...GithubRepo\n    __typename\n  }\n}"


class DeclareResourceMutation(BaseModel):
    declare_resource: Resource = Field(alias="declareResource")
    "Create a new resource for your backend"

    class Arguments(BaseModel):
        input: DeclareResourceInput

    class Meta:
        document = "fragment Resource on Resource {\n  id\n  name\n  qualifiers\n  backend {\n    id\n    name\n    __typename\n  }\n  pods {\n    id\n    podId\n    __typename\n  }\n  __typename\n}\n\nmutation DeclareResource($input: DeclareResourceInput!) {\n  declareResource(input: $input) {\n    ...Resource\n    __typename\n  }\n}"


class DeclareBackendMutation(BaseModel):
    declare_backend: Backend = Field(alias="declareBackend")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        input: DeclareBackendInput

    class Meta:
        document = "fragment Backend on Backend {\n  id\n  name\n  __typename\n}\n\nmutation DeclareBackend($input: DeclareBackendInput!) {\n  declareBackend(input: $input) {\n    ...Backend\n    __typename\n  }\n}"


class ListReleasesQuery(BaseModel):
    releases: Tuple[ListRelease, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  app {\n    identifier\n    __typename\n  }\n  installed\n  scopes\n  flavours {\n    ...ListFlavour\n    __typename\n  }\n  colour\n  description\n  __typename\n}\n\nquery ListReleases {\n  releases {\n    ...ListRelease\n    __typename\n  }\n}"


class GetReleaseQuery(BaseModel):
    release: Release
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Release on Release {\n  id\n  version\n  app {\n    identifier\n    __typename\n  }\n  scopes\n  colour\n  description\n  flavours {\n    ...ListFlavour\n    __typename\n  }\n  __typename\n}\n\nquery GetRelease($id: ID!) {\n  release(id: $id) {\n    ...Release\n    __typename\n  }\n}"


class SearchReleasesQueryOptions(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    value: ID
    label: str
    "Is this release deployed"
    model_config = ConfigDict(frozen=True)


class SearchReleasesQuery(BaseModel):
    options: Tuple[SearchReleasesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchReleases($search: String, $values: [ID!]) {\n  options: releases(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetDeploymentQuery(BaseModel):
    deployment: Deployment
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Deployment on Deployment {\n  id\n  localId\n  __typename\n}\n\nquery GetDeployment($id: ID!) {\n  deployment(id: $id) {\n    ...Deployment\n    __typename\n  }\n}"


class ListDeploymentsQuery(BaseModel):
    deployments: Tuple[ListDeployment, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListDeployment on Deployment {\n  id\n  localId\n  __typename\n}\n\nquery ListDeployments {\n  deployments {\n    ...ListDeployment\n    __typename\n  }\n}"


class SearchDeploymentsQueryOptions(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Deployment"] = Field(
        alias="__typename", default="Deployment", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchDeploymentsQuery(BaseModel):
    options: Tuple[SearchDeploymentsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchDeployments($search: String, $values: [ID!]) {\n  options: deployments(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListPodQuery(BaseModel):
    pods: Tuple[ListPod, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListPod on Pod {\n  id\n  podId\n  __typename\n}\n\nquery ListPod {\n  pods {\n    ...ListPod\n    __typename\n  }\n}"


class GetPodQuery(BaseModel):
    pod: Pod
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Flavour on Flavour {\n  ...ListFlavour\n  release {\n    id\n    version\n    app {\n      identifier\n      __typename\n    }\n    scopes\n    colour\n    description\n    __typename\n  }\n  __typename\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetPod($id: ID!) {\n  pod(id: $id) {\n    ...Pod\n    __typename\n  }\n}"


class SearchPodsQueryOptions(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Pod"] = Field(alias="__typename", default="Pod", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchPodsQuery(BaseModel):
    options: Tuple[SearchPodsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        backend: Optional[ID] = Field(default=None)

    class Meta:
        document = "query SearchPods($search: String, $values: [ID!], $backend: ID) {\n  options: pods(\n    filters: {search: $search, ids: $values, backend: $backend}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListDefinitionsQuery(BaseModel):
    definitions: Tuple[ListDefinition, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListDefinition on Definition {\n  id\n  name\n  hash\n  description\n  __typename\n}\n\nquery ListDefinitions {\n  definitions {\n    ...ListDefinition\n    __typename\n  }\n}"


class GetDefinitionByHashQuery(BaseModel):
    definition: Definition
    "Return all dask clusters"

    class Arguments(BaseModel):
        hash: Optional[NodeHash] = Field(default=None)

    class Meta:
        document = "fragment Definition on Definition {\n  id\n  name\n  __typename\n}\n\nquery GetDefinitionByHash($hash: NodeHash) {\n  definition(hash: $hash) {\n    ...Definition\n    __typename\n  }\n}"


class GetDefinitionQuery(BaseModel):
    definition: Definition
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Definition on Definition {\n  id\n  name\n  __typename\n}\n\nquery GetDefinition($id: ID!) {\n  definition(id: $id) {\n    ...Definition\n    __typename\n  }\n}"


class SearchDefinitionsQueryOptions(BaseModel):
    """Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation"""

    typename: Literal["Definition"] = Field(
        alias="__typename", default="Definition", exclude=True
    )
    value: ID
    label: str
    "The cleartext name of this Node"
    model_config = ConfigDict(frozen=True)


class SearchDefinitionsQuery(BaseModel):
    options: Tuple[SearchDefinitionsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchDefinitions($search: String, $values: [ID!]) {\n  options: definitions(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class MatchFlavourQueryMatchflavourImage(BaseModel):
    """A docker image descriptor"""

    typename: Literal["DockerImage"] = Field(
        alias="__typename", default="DockerImage", exclude=True
    )
    image_string: str = Field(alias="imageString")
    build_at: datetime = Field(alias="buildAt")
    model_config = ConfigDict(frozen=True)


class MatchFlavourQueryMatchflavour(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Flavour"] = Field(
        alias="__typename", default="Flavour", exclude=True
    )
    id: ID
    image: MatchFlavourQueryMatchflavourImage
    model_config = ConfigDict(frozen=True)


class MatchFlavourQuery(BaseModel):
    match_flavour: MatchFlavourQueryMatchflavour = Field(alias="matchFlavour")
    "Return the currently logged in user"

    class Arguments(BaseModel):
        nodes: Optional[List[NodeHash]] = Field(default=None)
        environment: Optional[EnvironmentInput] = Field(default=None)

    class Meta:
        document = "query MatchFlavour($nodes: [NodeHash!], $environment: EnvironmentInput) {\n  matchFlavour(input: {nodes: $nodes, environment: $environment}) {\n    id\n    image {\n      imageString\n      buildAt\n      __typename\n    }\n    __typename\n  }\n}"


class GetFlavourQuery(BaseModel):
    flavour: Flavour
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment CudaSelector on CudaSelector {\n  cudaVersion\n  cudaCores\n  __typename\n}\n\nfragment RocmSelector on RocmSelector {\n  apiVersion\n  apiThing\n  __typename\n}\n\nfragment ListFlavour on Flavour {\n  id\n  name\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  manifest\n  requirements {\n    key\n    service\n    description\n    optional\n    __typename\n  }\n  image {\n    imageString\n    buildAt\n    __typename\n  }\n  selectors {\n    ...CudaSelector\n    ...RocmSelector\n    __typename\n  }\n  __typename\n}\n\nfragment Flavour on Flavour {\n  ...ListFlavour\n  release {\n    id\n    version\n    app {\n      identifier\n      __typename\n    }\n    scopes\n    colour\n    description\n    __typename\n  }\n  __typename\n}\n\nquery GetFlavour($id: ID!) {\n  flavour(id: $id) {\n    ...Flavour\n    __typename\n  }\n}"


class SearchFlavoursQueryOptions(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Flavour"] = Field(
        alias="__typename", default="Flavour", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchFlavoursQuery(BaseModel):
    options: Tuple[SearchFlavoursQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchFlavours($search: String, $values: [ID!]) {\n  options: flavours(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListResourcesQuery(BaseModel):
    resources: Tuple[ListResource, ...]

    class Arguments(BaseModel):
        filters: Optional[ResourceFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment ListResource on Resource {\n  id\n  name\n  qualifiers\n  backend {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nquery ListResources($filters: ResourceFilter, $pagination: OffsetPaginationInput) {\n  resources(filters: $filters, pagination: $pagination) {\n    ...ListResource\n    __typename\n  }\n}"


class GeResourceQuery(BaseModel):
    resource: Resource
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Resource on Resource {\n  id\n  name\n  qualifiers\n  backend {\n    id\n    name\n    __typename\n  }\n  pods {\n    id\n    podId\n    __typename\n  }\n  __typename\n}\n\nquery GeResource($id: ID!) {\n  resource(id: $id) {\n    ...Resource\n    __typename\n  }\n}"


class SearchResourcesQueryOptions(BaseModel):
    """A resource on a backend. Resource define allocated resources on a backend. E.g a computational node"""

    typename: Literal["Resource"] = Field(
        alias="__typename", default="Resource", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchResourcesQuery(BaseModel):
    options: Tuple[SearchResourcesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchResources($search: String, $values: [ID!]) {\n  options: resources(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListBackendsQuery(BaseModel):
    backends: Tuple[ListBackend, ...]

    class Arguments(BaseModel):
        filters: Optional[BackendFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment ListBackend on Backend {\n  id\n  name\n  __typename\n}\n\nquery ListBackends($filters: BackendFilter, $pagination: OffsetPaginationInput) {\n  backends(filters: $filters, pagination: $pagination) {\n    ...ListBackend\n    __typename\n  }\n}"


class GetBackendQuery(BaseModel):
    backend: Backend
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Backend on Backend {\n  id\n  name\n  __typename\n}\n\nquery GetBackend($id: ID!) {\n  backend(id: $id) {\n    ...Backend\n    __typename\n  }\n}"


class SearchBackendsQueryOptions(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Literal["Backend"] = Field(
        alias="__typename", default="Backend", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchBackendsQuery(BaseModel):
    options: Tuple[SearchBackendsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchBackends($search: String, $values: [ID!]) {\n  options: backends(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


async def acreate_deployment(
    instance_id: str,
    local_id: ID,
    flavour: ID,
    last_pulled: Optional[datetime] = None,
    secret_params: Optional[Any] = None,
    rath: Optional[KabinetRath] = None,
) -> Deployment:
    """CreateDeployment

    Create a new dask cluster on a bridge server

    Arguments:
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        flavour: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        last_pulled: Date with time (isoformat)
        secret_params: UntypedParams represents an untyped options object returned by the Dask Gateway API.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Deployment"""
    return (
        await aexecute(
            CreateDeploymentMutation,
            {
                "input": {
                    "instanceId": instance_id,
                    "localId": local_id,
                    "flavour": flavour,
                    "lastPulled": last_pulled,
                    "secretParams": secret_params,
                }
            },
            rath=rath,
        )
    ).create_deployment


def create_deployment(
    instance_id: str,
    local_id: ID,
    flavour: ID,
    last_pulled: Optional[datetime] = None,
    secret_params: Optional[Any] = None,
    rath: Optional[KabinetRath] = None,
) -> Deployment:
    """CreateDeployment

    Create a new dask cluster on a bridge server

    Arguments:
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        flavour: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        last_pulled: Date with time (isoformat)
        secret_params: UntypedParams represents an untyped options object returned by the Dask Gateway API.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Deployment"""
    return execute(
        CreateDeploymentMutation,
        {
            "input": {
                "instanceId": instance_id,
                "localId": local_id,
                "flavour": flavour,
                "lastPulled": last_pulled,
                "secretParams": secret_params,
            }
        },
        rath=rath,
    ).create_deployment


async def acreate_pod(
    deployment: ID,
    local_id: ID,
    instance_id: str,
    resource: Optional[ID] = None,
    client_id: Optional[str] = None,
    rath: Optional[KabinetRath] = None,
) -> Pod:
    """CreatePod

    Create a new dask cluster on a bridge server

    Arguments:
        deployment: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        resource: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        client_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return (
        await aexecute(
            CreatePodMutation,
            {
                "input": {
                    "deployment": deployment,
                    "localId": local_id,
                    "resource": resource,
                    "instanceId": instance_id,
                    "clientId": client_id,
                }
            },
            rath=rath,
        )
    ).create_pod


def create_pod(
    deployment: ID,
    local_id: ID,
    instance_id: str,
    resource: Optional[ID] = None,
    client_id: Optional[str] = None,
    rath: Optional[KabinetRath] = None,
) -> Pod:
    """CreatePod

    Create a new dask cluster on a bridge server

    Arguments:
        deployment: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        resource: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        client_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return execute(
        CreatePodMutation,
        {
            "input": {
                "deployment": deployment,
                "localId": local_id,
                "resource": resource,
                "instanceId": instance_id,
                "clientId": client_id,
            }
        },
        rath=rath,
    ).create_pod


async def aupdate_pod(
    status: PodStatus,
    instance_id: str,
    pod: Optional[ID] = None,
    local_id: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> Pod:
    """UpdatePod

    Create a new dask cluster on a bridge server

    Arguments:
        pod: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        status: PodStatus (required)
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return (
        await aexecute(
            UpdatePodMutation,
            {
                "input": {
                    "pod": pod,
                    "localId": local_id,
                    "status": status,
                    "instanceId": instance_id,
                }
            },
            rath=rath,
        )
    ).update_pod


def update_pod(
    status: PodStatus,
    instance_id: str,
    pod: Optional[ID] = None,
    local_id: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> Pod:
    """UpdatePod

    Create a new dask cluster on a bridge server

    Arguments:
        pod: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        local_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        status: PodStatus (required)
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return execute(
        UpdatePodMutation,
        {
            "input": {
                "pod": pod,
                "localId": local_id,
                "status": status,
                "instanceId": instance_id,
            }
        },
        rath=rath,
    ).update_pod


async def adelete_pod(id: ID, rath: Optional[KabinetRath] = None) -> ID:
    """DeletePod

    Create a new dask cluster on a bridge server

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ID"""
    return (
        await aexecute(DeletePodMutation, {"input": {"id": id}}, rath=rath)
    ).delete_pod


def delete_pod(id: ID, rath: Optional[KabinetRath] = None) -> ID:
    """DeletePod

    Create a new dask cluster on a bridge server

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ID"""
    return execute(DeletePodMutation, {"input": {"id": id}}, rath=rath).delete_pod


async def adump_logs(
    pod: ID, logs: str, rath: Optional[KabinetRath] = None
) -> DumpLogsMutationDumplogs:
    """DumpLogs

    Create a new dask cluster on a bridge server

    Arguments:
        pod: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        logs: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DumpLogsMutationDumplogs"""
    return (
        await aexecute(
            DumpLogsMutation, {"input": {"pod": pod, "logs": logs}}, rath=rath
        )
    ).dump_logs


def dump_logs(
    pod: ID, logs: str, rath: Optional[KabinetRath] = None
) -> DumpLogsMutationDumplogs:
    """DumpLogs

    Create a new dask cluster on a bridge server

    Arguments:
        pod: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        logs: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DumpLogsMutationDumplogs"""
    return execute(
        DumpLogsMutation, {"input": {"pod": pod, "logs": logs}}, rath=rath
    ).dump_logs


async def acreate_app_image(
    manifest: ManifestInput,
    selectors: Iterable[SelectorInput],
    app_image_id: str,
    inspection: InspectionInput,
    image: DockerImageInput,
    flavour_name: Optional[str] = None,
    rath: Optional[KabinetRath] = None,
) -> Release:
    """CreateAppImage

    Create a new release

    Arguments:
        flavour_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        manifest:  (required)
        selectors:  (required) (list) (required)
        app_image_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        inspection:  (required)
        image:  (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Release"""
    return (
        await aexecute(
            CreateAppImageMutation,
            {
                "input": {
                    "flavourName": flavour_name,
                    "manifest": manifest,
                    "selectors": selectors,
                    "appImageId": app_image_id,
                    "inspection": inspection,
                    "image": image,
                }
            },
            rath=rath,
        )
    ).create_app_image


def create_app_image(
    manifest: ManifestInput,
    selectors: Iterable[SelectorInput],
    app_image_id: str,
    inspection: InspectionInput,
    image: DockerImageInput,
    flavour_name: Optional[str] = None,
    rath: Optional[KabinetRath] = None,
) -> Release:
    """CreateAppImage

    Create a new release

    Arguments:
        flavour_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        manifest:  (required)
        selectors:  (required) (list) (required)
        app_image_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        inspection:  (required)
        image:  (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Release"""
    return execute(
        CreateAppImageMutation,
        {
            "input": {
                "flavourName": flavour_name,
                "manifest": manifest,
                "selectors": selectors,
                "appImageId": app_image_id,
                "inspection": inspection,
                "image": image,
            }
        },
        rath=rath,
    ).create_app_image


async def acreate_github_repo(
    name: Optional[str] = None,
    user: Optional[str] = None,
    branch: Optional[str] = None,
    repo: Optional[str] = None,
    identifier: Optional[str] = None,
    auto_scan: Optional[bool] = True,
    rath: Optional[KabinetRath] = None,
) -> GithubRepo:
    """CreateGithubRepo

    Create a new Github repository on a bridge server

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        user: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        branch: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        repo: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        identifier: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        auto_scan: The `Boolean` scalar type represents `true` or `false`.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GithubRepo"""
    return (
        await aexecute(
            CreateGithubRepoMutation,
            {
                "input": {
                    "name": name,
                    "user": user,
                    "branch": branch,
                    "repo": repo,
                    "identifier": identifier,
                    "autoScan": auto_scan,
                }
            },
            rath=rath,
        )
    ).create_github_repo


def create_github_repo(
    name: Optional[str] = None,
    user: Optional[str] = None,
    branch: Optional[str] = None,
    repo: Optional[str] = None,
    identifier: Optional[str] = None,
    auto_scan: Optional[bool] = True,
    rath: Optional[KabinetRath] = None,
) -> GithubRepo:
    """CreateGithubRepo

    Create a new Github repository on a bridge server

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        user: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        branch: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        repo: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        identifier: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        auto_scan: The `Boolean` scalar type represents `true` or `false`.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GithubRepo"""
    return execute(
        CreateGithubRepoMutation,
        {
            "input": {
                "name": name,
                "user": user,
                "branch": branch,
                "repo": repo,
                "identifier": identifier,
                "autoScan": auto_scan,
            }
        },
        rath=rath,
    ).create_github_repo


async def adeclare_resource(
    backend: ID,
    local_id: str,
    name: Optional[str] = None,
    qualifiers: Optional[Iterable[QualifierInput]] = None,
    rath: Optional[KabinetRath] = None,
) -> Resource:
    """DeclareResource

    Create a new resource for your backend

    Arguments:
        backend: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        local_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        qualifiers: A qualifier that describes some property of the node (required) (list)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Resource"""
    return (
        await aexecute(
            DeclareResourceMutation,
            {
                "input": {
                    "backend": backend,
                    "name": name,
                    "localId": local_id,
                    "qualifiers": qualifiers,
                }
            },
            rath=rath,
        )
    ).declare_resource


def declare_resource(
    backend: ID,
    local_id: str,
    name: Optional[str] = None,
    qualifiers: Optional[Iterable[QualifierInput]] = None,
    rath: Optional[KabinetRath] = None,
) -> Resource:
    """DeclareResource

    Create a new resource for your backend

    Arguments:
        backend: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        local_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        qualifiers: A qualifier that describes some property of the node (required) (list)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Resource"""
    return execute(
        DeclareResourceMutation,
        {
            "input": {
                "backend": backend,
                "name": name,
                "localId": local_id,
                "qualifiers": qualifiers,
            }
        },
        rath=rath,
    ).declare_resource


async def adeclare_backend(
    instance_id: str, name: str, kind: str, rath: Optional[KabinetRath] = None
) -> Backend:
    """DeclareBackend

    Create a new dask cluster on a bridge server

    Arguments:
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        kind: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Backend"""
    return (
        await aexecute(
            DeclareBackendMutation,
            {"input": {"instanceId": instance_id, "name": name, "kind": kind}},
            rath=rath,
        )
    ).declare_backend


def declare_backend(
    instance_id: str, name: str, kind: str, rath: Optional[KabinetRath] = None
) -> Backend:
    """DeclareBackend

    Create a new dask cluster on a bridge server

    Arguments:
        instance_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        kind: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Backend"""
    return execute(
        DeclareBackendMutation,
        {"input": {"instanceId": instance_id, "name": name, "kind": kind}},
        rath=rath,
    ).declare_backend


async def alist_releases(rath: Optional[KabinetRath] = None) -> Tuple[ListRelease, ...]:
    """ListReleases


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRelease]"""
    return (await aexecute(ListReleasesQuery, {}, rath=rath)).releases


def list_releases(rath: Optional[KabinetRath] = None) -> Tuple[ListRelease, ...]:
    """ListReleases


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRelease]"""
    return execute(ListReleasesQuery, {}, rath=rath).releases


async def aget_release(id: ID, rath: Optional[KabinetRath] = None) -> Release:
    """GetRelease

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Release"""
    return (await aexecute(GetReleaseQuery, {"id": id}, rath=rath)).release


def get_release(id: ID, rath: Optional[KabinetRath] = None) -> Release:
    """GetRelease

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Release"""
    return execute(GetReleaseQuery, {"id": id}, rath=rath).release


async def asearch_releases(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchReleasesQueryOptions, ...]:
    """SearchReleases


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchReleasesQueryReleases]"""
    return (
        await aexecute(
            SearchReleasesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_releases(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchReleasesQueryOptions, ...]:
    """SearchReleases


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchReleasesQueryReleases]"""
    return execute(
        SearchReleasesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_deployment(id: ID, rath: Optional[KabinetRath] = None) -> Deployment:
    """GetDeployment

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Deployment"""
    return (await aexecute(GetDeploymentQuery, {"id": id}, rath=rath)).deployment


def get_deployment(id: ID, rath: Optional[KabinetRath] = None) -> Deployment:
    """GetDeployment

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Deployment"""
    return execute(GetDeploymentQuery, {"id": id}, rath=rath).deployment


async def alist_deployments(
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListDeployment, ...]:
    """ListDeployments


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDeployment]"""
    return (await aexecute(ListDeploymentsQuery, {}, rath=rath)).deployments


def list_deployments(rath: Optional[KabinetRath] = None) -> Tuple[ListDeployment, ...]:
    """ListDeployments


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDeployment]"""
    return execute(ListDeploymentsQuery, {}, rath=rath).deployments


async def asearch_deployments(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchDeploymentsQueryOptions, ...]:
    """SearchDeployments


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchDeploymentsQueryDeployments]"""
    return (
        await aexecute(
            SearchDeploymentsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_deployments(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchDeploymentsQueryOptions, ...]:
    """SearchDeployments


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchDeploymentsQueryDeployments]"""
    return execute(
        SearchDeploymentsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_pod(rath: Optional[KabinetRath] = None) -> Tuple[ListPod, ...]:
    """ListPod


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListPod]"""
    return (await aexecute(ListPodQuery, {}, rath=rath)).pods


def list_pod(rath: Optional[KabinetRath] = None) -> Tuple[ListPod, ...]:
    """ListPod


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListPod]"""
    return execute(ListPodQuery, {}, rath=rath).pods


async def aget_pod(id: ID, rath: Optional[KabinetRath] = None) -> Pod:
    """GetPod

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return (await aexecute(GetPodQuery, {"id": id}, rath=rath)).pod


def get_pod(id: ID, rath: Optional[KabinetRath] = None) -> Pod:
    """GetPod

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Pod"""
    return execute(GetPodQuery, {"id": id}, rath=rath).pod


async def asearch_pods(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    backend: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchPodsQueryOptions, ...]:
    """SearchPods


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        backend (Optional[ID], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchPodsQueryPods]"""
    return (
        await aexecute(
            SearchPodsQuery,
            {"search": search, "values": values, "backend": backend},
            rath=rath,
        )
    ).options


def search_pods(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    backend: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchPodsQueryOptions, ...]:
    """SearchPods


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        backend (Optional[ID], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchPodsQueryPods]"""
    return execute(
        SearchPodsQuery,
        {"search": search, "values": values, "backend": backend},
        rath=rath,
    ).options


async def alist_definitions(
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListDefinition, ...]:
    """ListDefinitions


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDefinition]"""
    return (await aexecute(ListDefinitionsQuery, {}, rath=rath)).definitions


def list_definitions(rath: Optional[KabinetRath] = None) -> Tuple[ListDefinition, ...]:
    """ListDefinitions


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDefinition]"""
    return execute(ListDefinitionsQuery, {}, rath=rath).definitions


async def aget_definition_by_hash(
    hash: Optional[NodeHash] = None, rath: Optional[KabinetRath] = None
) -> Definition:
    """GetDefinitionByHash

    Return all dask clusters

    Arguments:
        hash (Optional[NodeHash], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Definition"""
    return (
        await aexecute(GetDefinitionByHashQuery, {"hash": hash}, rath=rath)
    ).definition


def get_definition_by_hash(
    hash: Optional[NodeHash] = None, rath: Optional[KabinetRath] = None
) -> Definition:
    """GetDefinitionByHash

    Return all dask clusters

    Arguments:
        hash (Optional[NodeHash], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Definition"""
    return execute(GetDefinitionByHashQuery, {"hash": hash}, rath=rath).definition


async def aget_definition(id: ID, rath: Optional[KabinetRath] = None) -> Definition:
    """GetDefinition

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Definition"""
    return (await aexecute(GetDefinitionQuery, {"id": id}, rath=rath)).definition


def get_definition(id: ID, rath: Optional[KabinetRath] = None) -> Definition:
    """GetDefinition

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Definition"""
    return execute(GetDefinitionQuery, {"id": id}, rath=rath).definition


async def asearch_definitions(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchDefinitionsQueryOptions, ...]:
    """SearchDefinitions


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchDefinitionsQueryDefinitions]"""
    return (
        await aexecute(
            SearchDefinitionsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_definitions(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchDefinitionsQueryOptions, ...]:
    """SearchDefinitions


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchDefinitionsQueryDefinitions]"""
    return execute(
        SearchDefinitionsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def amatch_flavour(
    nodes: Optional[List[NodeHash]] = None,
    environment: Optional[EnvironmentInput] = None,
    rath: Optional[KabinetRath] = None,
) -> MatchFlavourQueryMatchflavour:
    """MatchFlavour

    Return the currently logged in user

    Arguments:
        nodes (Optional[List[NodeHash]], optional): No description.
        environment (Optional[EnvironmentInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MatchFlavourQueryMatchflavour"""
    return (
        await aexecute(
            MatchFlavourQuery, {"nodes": nodes, "environment": environment}, rath=rath
        )
    ).match_flavour


def match_flavour(
    nodes: Optional[List[NodeHash]] = None,
    environment: Optional[EnvironmentInput] = None,
    rath: Optional[KabinetRath] = None,
) -> MatchFlavourQueryMatchflavour:
    """MatchFlavour

    Return the currently logged in user

    Arguments:
        nodes (Optional[List[NodeHash]], optional): No description.
        environment (Optional[EnvironmentInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MatchFlavourQueryMatchflavour"""
    return execute(
        MatchFlavourQuery, {"nodes": nodes, "environment": environment}, rath=rath
    ).match_flavour


async def aget_flavour(id: ID, rath: Optional[KabinetRath] = None) -> Flavour:
    """GetFlavour

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flavour"""
    return (await aexecute(GetFlavourQuery, {"id": id}, rath=rath)).flavour


def get_flavour(id: ID, rath: Optional[KabinetRath] = None) -> Flavour:
    """GetFlavour

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flavour"""
    return execute(GetFlavourQuery, {"id": id}, rath=rath).flavour


async def asearch_flavours(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchFlavoursQueryOptions, ...]:
    """SearchFlavours


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlavoursQueryFlavours]"""
    return (
        await aexecute(
            SearchFlavoursQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_flavours(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchFlavoursQueryOptions, ...]:
    """SearchFlavours


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlavoursQueryFlavours]"""
    return execute(
        SearchFlavoursQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_resources(
    filters: Optional[ResourceFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListResource, ...]:
    """ListResources


    Arguments:
        filters (Optional[ResourceFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListResource]"""
    return (
        await aexecute(
            ListResourcesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).resources


def list_resources(
    filters: Optional[ResourceFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListResource, ...]:
    """ListResources


    Arguments:
        filters (Optional[ResourceFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListResource]"""
    return execute(
        ListResourcesQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).resources


async def age_resource(id: ID, rath: Optional[KabinetRath] = None) -> Resource:
    """GeResource

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Resource"""
    return (await aexecute(GeResourceQuery, {"id": id}, rath=rath)).resource


def ge_resource(id: ID, rath: Optional[KabinetRath] = None) -> Resource:
    """GeResource

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Resource"""
    return execute(GeResourceQuery, {"id": id}, rath=rath).resource


async def asearch_resources(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchResourcesQueryOptions, ...]:
    """SearchResources


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchResourcesQueryResources]"""
    return (
        await aexecute(
            SearchResourcesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_resources(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchResourcesQueryOptions, ...]:
    """SearchResources


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchResourcesQueryResources]"""
    return execute(
        SearchResourcesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_backends(
    filters: Optional[BackendFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListBackend, ...]:
    """ListBackends


    Arguments:
        filters (Optional[BackendFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListBackend]"""
    return (
        await aexecute(
            ListBackendsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).backends


def list_backends(
    filters: Optional[BackendFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[ListBackend, ...]:
    """ListBackends


    Arguments:
        filters (Optional[BackendFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListBackend]"""
    return execute(
        ListBackendsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).backends


async def aget_backend(id: ID, rath: Optional[KabinetRath] = None) -> Backend:
    """GetBackend

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Backend"""
    return (await aexecute(GetBackendQuery, {"id": id}, rath=rath)).backend


def get_backend(id: ID, rath: Optional[KabinetRath] = None) -> Backend:
    """GetBackend

    Return all dask clusters

    Arguments:
        id (ID): No description
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Backend"""
    return execute(GetBackendQuery, {"id": id}, rath=rath).backend


async def asearch_backends(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchBackendsQueryOptions, ...]:
    """SearchBackends


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchBackendsQueryBackends]"""
    return (
        await aexecute(
            SearchBackendsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_backends(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KabinetRath] = None,
) -> Tuple[SearchBackendsQueryOptions, ...]:
    """SearchBackends


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchBackendsQueryBackends]"""
    return execute(
        SearchBackendsQuery, {"search": search, "values": values}, rath=rath
    ).options


AppImageInput.model_rebuild()
AssignWidgetInput.model_rebuild()
BackendFilter.model_rebuild()
ChildPortInput.model_rebuild()
DeclareResourceInput.model_rebuild()
DefinitionInput.model_rebuild()
InspectionInput.model_rebuild()
PortInput.model_rebuild()
ResourceFilter.model_rebuild()
