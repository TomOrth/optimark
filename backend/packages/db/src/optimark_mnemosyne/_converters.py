"""Shared model-to-domain conversion helpers for Mnemosyne."""

from datetime import UTC, datetime

from optimark_metis.academic import User
from optimark_mnemosyne.models import UserModel


def coerce_utc(value: datetime) -> datetime:
    """Normalize timestamps to timezone-aware UTC values.

    Args:
        value: Timestamp returned by the ORM or database driver.

    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def user_from_model(model: UserModel) -> User:
    """Convert a user ORM model into a domain user.

    Args:
        model: ORM user model instance.

    Returns:
        User: Domain user entity.
    """
    return User(
        id=model.id,
        email=model.email,
        display_name=model.display_name,
        created_at=coerce_utc(model.created_at),
        updated_at=coerce_utc(model.updated_at),
    )
