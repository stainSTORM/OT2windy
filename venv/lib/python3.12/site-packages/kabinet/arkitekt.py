import json
import os
from kabinet.kabinet import Kabinet
from kabinet.rath import KabinetLinkComposition, KabinetRath
from rath.links.split import SplitLink
from fakts_next.contrib.rath.aiohttp import FaktsAIOHttpLink
from fakts_next.contrib.rath.graphql_ws import FaktsGraphQLWSLink
from herre_next.contrib.rath.auth_link import HerreAuthLink
from graphql import OperationType
from herre_next import Herre
from fakts_next import Fakts

from arkitekt_next.base_models import Manifest

from arkitekt_next.service_registry import (
    BaseArkitektService,
    Params,
    get_default_service_registry,
)
from arkitekt_next.base_models import Requirement


class ArkitektNextKabinet(Kabinet):
    rath: KabinetRath


def build_relative_path(*path: str) -> str:
    return os.path.join(os.path.dirname(__file__), *path)


class KabinetService(BaseArkitektService):

    def get_service_name(self):
        return "kabinet"

    def build_service(
        self, fakts: Fakts, herre: Herre, params: Params, manifest: Manifest
    ):
        return ArkitektNextKabinet(
            rath=KabinetRath(
                link=KabinetLinkComposition(
                    auth=HerreAuthLink(herre=herre),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(
                            fakts_group="kabinet", fakts=fakts, endpoint_url="FAKE_URL"
                        ),
                        right=FaktsGraphQLWSLink(
                            fakts_group="kabinet",
                            fakts=fakts,
                            ws_endpoint_url="FAKE_URL",
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            )
        )

    def get_requirements(self):
        return [
            Requirement(
                key="kabinet",
                service="live.arkitekt.kabinet",
                description="An instance of ArkitektNext kabinet to relate entities",
            ),
        ]

    def get_graphql_schema(self):
        schema_graphql_path = build_relative_path("api", "schema.graphql")
        with open(schema_graphql_path) as f:
            return f.read()

    def get_turms_project(self):
        turms_prject = build_relative_path("api", "project.json")
        with open(turms_prject) as f:
            return json.loads(f.read())


get_default_service_registry().register(KabinetService())
