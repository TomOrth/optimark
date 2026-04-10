"""Health and bootstrap contracts shared across backend apps."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health response returned by the API bootstrap.

    Attributes:
        status: Overall health status string.
        app_name: Application name reported by the service.
        service_name: Service identifier.
        layer: Runtime layer producing the response.
        persistence_provider: Backing persistence provider name.
        workspace_packages: Shared workspace packages wired into the service.
    """

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
        """Construct a health response from primitive values.

        Args:
            status: Overall health status string.
            app_name: Application name reported by the service.
            service_name: Service identifier.
            layer: Runtime layer producing the response.
            persistence_provider: Backing persistence provider name.
            workspace_packages: Shared workspace packages wired into the service.

        Returns:
            HealthResponse: The populated health response model.
        """
        return cls(
            status=status,
            app_name=app_name,
            service_name=service_name,
            layer=layer,
            persistence_provider=persistence_provider,
            workspace_packages=workspace_packages,
        )


class WorkerBootstrapMessage(BaseModel):
    """Worker bootstrap payload printed by the Hermes process.

    Attributes:
        status: Overall health status string.
        worker_name: Worker service identifier.
        persistence_provider: Backing persistence provider name.
        workspace_packages: Shared workspace packages wired into the worker.
    """

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
        """Construct a worker bootstrap message from primitive values.

        Args:
            status: Overall health status string.
            worker_name: Worker service identifier.
            persistence_provider: Backing persistence provider name.
            workspace_packages: Shared workspace packages wired into the worker.

        Returns:
            WorkerBootstrapMessage: The populated worker bootstrap model.
        """
        return cls(
            status=status,
            worker_name=worker_name,
            persistence_provider=persistence_provider,
            workspace_packages=workspace_packages,
        )
