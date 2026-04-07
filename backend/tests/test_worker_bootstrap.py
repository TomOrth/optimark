import json

from optimark_hermes.__main__ import main


def test_worker_bootstrap_prints_workspace_message(capsys) -> None:
    main()

    captured = capsys.readouterr()

    assert json.loads(captured.out) == {
        "status": "ok",
        "worker_name": "hermes",
        "persistence_provider": "postgres",
        "workspace_packages": ["metis", "mnemosyne", "clio"],
    }
