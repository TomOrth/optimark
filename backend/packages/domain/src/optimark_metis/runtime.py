"""Bootstrap service descriptors used by backend health endpoints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceDescriptor:
    """Describe a running backend service.

    Attributes:
        service_name: Service identifier.
        layer: Runtime layer for the service.
        app_name: Top-level application name.
        status: Current health status.
    """

    service_name: str
    layer: str
    app_name: str = "optimark"
    status: str = "ok"


def build_service_descriptor(*, service_name: str, layer: str) -> ServiceDescriptor:
    """Create a service descriptor for bootstrap reporting.

    Args:
        service_name: Service identifier.
        layer: Runtime layer for the service.

    Returns:
        ServiceDescriptor: Service descriptor with default app metadata.
    """
    return ServiceDescriptor(service_name=service_name, layer=layer)
