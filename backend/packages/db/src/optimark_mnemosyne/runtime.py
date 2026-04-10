"""Bootstrap persistence descriptors for backend health reporting."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PersistenceDescriptor:
    """Describe the currently configured persistence layer.

    Attributes:
        database_provider: Name of the backing database technology.
        workspace_package: Workspace package exposing persistence services.
    """

    database_provider: str
    workspace_package: str


def default_persistence_descriptor() -> PersistenceDescriptor:
    """Return the default persistence descriptor for backend bootstraps.

    Returns:
        PersistenceDescriptor: Default persistence metadata.
    """
    return PersistenceDescriptor(
        database_provider="postgres",
        workspace_package="mnemosyne",
    )
