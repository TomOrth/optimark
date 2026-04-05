from dataclasses import dataclass


@dataclass(frozen=True)
class PersistenceDescriptor:
    database_provider: str
    workspace_package: str


def default_persistence_descriptor() -> PersistenceDescriptor:
    return PersistenceDescriptor(
        database_provider="postgres",
        workspace_package="mnemosyne",
    )
