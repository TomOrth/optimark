"""Command-line entrypoint for the Athena API application."""

import uvicorn


def main() -> None:
    """Start the FastAPI application with production-like defaults."""
    uvicorn.run(
        "optimark_athena.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
