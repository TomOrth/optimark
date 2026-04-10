"""Command-line entrypoint for the Hermes worker bootstrap."""

from optimark_clio.health import WorkerBootstrapMessage
from optimark_metis.runtime import build_service_descriptor
from optimark_mnemosyne.runtime import default_persistence_descriptor


def main() -> None:
    """Print a bootstrap message describing the worker wiring."""
    service = build_service_descriptor(service_name="hermes", layer="worker")
    persistence = default_persistence_descriptor()
    message = WorkerBootstrapMessage.from_values(
        status=service.status,
        worker_name=service.service_name,
        persistence_provider=persistence.database_provider,
        workspace_packages=["metis", "mnemosyne", "clio"],
    )
    print(message.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
