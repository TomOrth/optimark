from pydantic import BaseModel

from optimark_metis.runtime import ServiceDescriptor
from optimark_mnemosyne.runtime import PersistenceDescriptor


class HealthResponse(BaseModel):
    status: str
    app_name: str
    service_name: str
    layer: str
    persistence_provider: str
    workspace_packages: list[str]

    @classmethod
    def from_descriptors(
        cls,
        *,
        service: ServiceDescriptor,
        persistence: PersistenceDescriptor,
    ) -> "HealthResponse":
        return cls(
            status=service.status,
            app_name=service.app_name,
            service_name=service.service_name,
            layer=service.layer,
            persistence_provider=persistence.database_provider,
            workspace_packages=["metis", "mnemosyne", "clio"],
        )


class WorkerBootstrapMessage(BaseModel):
    status: str
    worker_name: str
    persistence_provider: str
    workspace_packages: list[str]

    @classmethod
    def from_descriptors(
        cls,
        *,
        service: ServiceDescriptor,
        persistence: PersistenceDescriptor,
    ) -> "WorkerBootstrapMessage":
        return cls(
            status=service.status,
            worker_name=service.service_name,
            persistence_provider=persistence.database_provider,
            workspace_packages=["metis", "mnemosyne", "clio"],
        )
