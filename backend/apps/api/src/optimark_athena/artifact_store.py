"""Artifact storage primitives for submission uploads."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath
from threading import Lock
from typing import BinaryIO
from typing import Any, Protocol

from optimark_athena.config import ArtifactStorageSettings


class ArtifactStore(Protocol):
    """Protocol for writing submission artifacts to durable storage."""

    def put_artifact(
        self,
        *,
        key: str,
        fileobj: BinaryIO,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> str:
        """Persist an artifact stream and return the storage key."""

    def delete_artifact(self, *, key: str) -> None:
        """Delete a previously persisted artifact."""


@dataclass
class S3ArtifactStore:
    """S3-compatible artifact store backed by boto3."""

    settings: ArtifactStorageSettings

    def __post_init__(self) -> None:
        import boto3

        self._client: Any = boto3.client(
            "s3",
            endpoint_url=self.settings.endpoint_url,
            region_name=self.settings.region,
            aws_access_key_id=self.settings.access_key_id,
            aws_secret_access_key=self.settings.secret_access_key,
        )
        self._bucket_ready = False
        self._bucket_lock = Lock()

    def put_artifact(
        self,
        *,
        key: str,
        fileobj: BinaryIO,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> str:
        """Persist an artifact stream to the configured S3 bucket."""
        self._ensure_bucket()
        storage_key = self._full_key(key)
        fileobj.seek(0)
        self._client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self.settings.bucket,
            Key=storage_key,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": dict(metadata or {}),
            },
        )
        return storage_key

    def delete_artifact(self, *, key: str) -> None:
        """Delete an artifact from the configured S3 bucket."""
        self._ensure_bucket()
        self._client.delete_object(
            Bucket=self.settings.bucket,
            Key=self._full_key(key),
        )

    def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return

        with self._bucket_lock:
            if self._bucket_ready:
                return

            try:
                self._client.head_bucket(Bucket=self.settings.bucket)
            except Exception:
                if not self.settings.auto_create_bucket:
                    raise
                self._create_bucket()

            self._bucket_ready = True

    def _create_bucket(self) -> None:
        create_kwargs: dict[str, object] = {
            "Bucket": self.settings.bucket,
        }
        if self.settings.endpoint_url is None and self.settings.region != "us-east-1":
            create_kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": self.settings.region,
            }
        self._client.create_bucket(**create_kwargs)

    def _full_key(self, key: str) -> str:
        normalized_key = PurePosixPath(key.lstrip("/")).as_posix()
        prefix = self.settings.key_prefix.strip("/")
        if not prefix:
            return normalized_key
        prefixed_key = f"{prefix}/"
        if normalized_key == prefix or normalized_key.startswith(prefixed_key):
            return normalized_key
        return f"{prefix}/{normalized_key}"
