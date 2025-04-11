from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.widgets import SearchWidget
from rekuest_next.api.schema import ChildPortInput, PortKind, PortScope

from kabinet.api.schema import (
    Pod,
    aget_pod,
    Flavour,
    aget_flavour,
    Deployment,
    aget_deployment,
    Release,
    aget_release,
    Definition,
    aget_definition,
    SearchDefinitionsQuery,
    SearchPodsQuery,
    SearchDeploymentsQuery,
    SearchReleasesQuery,
    SearchBackendsQuery,
    SearchFlavoursQuery,
)

structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Pod,
    identifier="@kabinet/pod",
    scope=PortScope.GLOBAL,
    aexpand=aget_pod,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchPodsQuery.Meta.document,
        ward="kabinet",
        filters=[
            ChildPortInput(
                key="deployment",
                kind=PortKind.STRUCTURE,
                scope=PortScope.GLOBAL,
                nullable=True,
                identifier="@kabinet/deployment",
                assignWidget=SearchWidget(
                    query=SearchDeploymentsQuery.Meta.document,
                    ward="kabinet",
                ),
            )
        ],
    ),
)

structure_reg.register_as_structure(
    Deployment,
    identifier="@kabinet/deployment",
    scope=PortScope.GLOBAL,
    aexpand=aget_deployment,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchDeploymentsQuery.Meta.document,
        ward="kabinet",
    ),
)
structure_reg.register_as_structure(
    Release,
    identifier="@kabinet/release",
    scope=PortScope.GLOBAL,
    aexpand=aget_release,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchReleasesQuery.Meta.document,
        ward="kabinet",
    ),
)
structure_reg.register_as_structure(
    Definition,
    identifier="@kabinet/definition",
    scope=PortScope.GLOBAL,
    aexpand=aget_definition,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchDefinitionsQuery.Meta.document,
        ward="kabinet",
    ),
)

structure_reg.register_as_structure(
    Flavour,
    identifier="@kabinet/flavour",
    scope=PortScope.GLOBAL,
    aexpand=aget_flavour,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchFlavoursQuery.Meta.document,
        ward="kabinet",
    ),
)
