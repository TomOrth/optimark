from optimark_clio.health import WorkerBootstrapMessage
from optimark_metis.runtime import build_service_descriptor
from optimark_mnemosyne.runtime import default_persistence_descriptor


def main() -> None:
    service = build_service_descriptor(service_name="hermes", layer="worker")
    persistence = default_persistence_descriptor()
    message = WorkerBootstrapMessage.from_descriptors(
        service=service,
        persistence=persistence,
    )
    print(message.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
