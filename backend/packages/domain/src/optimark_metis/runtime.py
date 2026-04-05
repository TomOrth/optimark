from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceDescriptor:
    service_name: str
    layer: str
    app_name: str = "optimark"
    status: str = "ok"


def build_service_descriptor(*, service_name: str, layer: str) -> ServiceDescriptor:
    return ServiceDescriptor(service_name=service_name, layer=layer)
