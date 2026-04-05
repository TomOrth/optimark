from fastapi import FastAPI

from optimark_clio.health import HealthResponse
from optimark_metis.runtime import build_service_descriptor
from optimark_mnemosyne.runtime import default_persistence_descriptor


app = FastAPI(
    title="Optimark API",
    summary="FastAPI bootstrap for the Optimark modular monolith.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    service = build_service_descriptor(service_name="athena", layer="api")
    persistence = default_persistence_descriptor()
    return HealthResponse.from_descriptors(service=service, persistence=persistence)
