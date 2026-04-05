from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    app_name: str
    service_name: str
    layer: str
    persistence_provider: str
    workspace_packages: list[str]

    @classmethod
    def from_values(
        cls,
        *,
        status: str,
        app_name: str,
        service_name: str,
        layer: str,
        persistence_provider: str,
        workspace_packages: list[str],
    ) -> "HealthResponse":
        return cls(
            status=status,
            app_name=app_name,
            service_name=service_name,
            layer=layer,
            persistence_provider=persistence_provider,
            workspace_packages=workspace_packages,
        )


class WorkerBootstrapMessage(BaseModel):
    status: str
    worker_name: str
    persistence_provider: str
    workspace_packages: list[str]

    @classmethod
    def from_values(
        cls,
        *,
        status: str,
        worker_name: str,
        persistence_provider: str,
        workspace_packages: list[str],
    ) -> "WorkerBootstrapMessage":
        return cls(
            status=status,
            worker_name=worker_name,
            persistence_provider=persistence_provider,
            workspace_packages=workspace_packages,
        )
