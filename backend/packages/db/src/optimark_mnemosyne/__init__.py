"""Mnemosyne persistence package for Optimark."""

from optimark_mnemosyne.assessment_repository import SqlAlchemyAssessmentRepository
from optimark_mnemosyne.auth_repository import SqlAlchemyAuthRepository
from optimark_mnemosyne.base import Base
from optimark_mnemosyne.config import (
    DEFAULT_DATABASE_URL,
    create_db_engine,
    create_session_factory,
    get_database_url,
)
from optimark_mnemosyne.models import (
    AssignmentModel,
    AssignmentVersionModel,
    AuthIdentityModel,
    AuthSessionModel,
    CourseModel,
    EvaluationRecordModel,
    EnrollmentModel,
    GradeRecordModel,
    PasswordCredentialModel,
    SubmissionModel,
    UserModel,
)
from optimark_mnemosyne.repository import SqlAlchemyAcademicRepository
from optimark_mnemosyne.runtime import PersistenceDescriptor, default_persistence_descriptor

__all__ = [
    "AssignmentModel",
    "AssignmentVersionModel",
    "AuthIdentityModel",
    "AuthSessionModel",
    "Base",
    "CourseModel",
    "DEFAULT_DATABASE_URL",
    "EvaluationRecordModel",
    "EnrollmentModel",
    "GradeRecordModel",
    "PasswordCredentialModel",
    "PersistenceDescriptor",
    "SqlAlchemyAcademicRepository",
    "SqlAlchemyAssessmentRepository",
    "SqlAlchemyAuthRepository",
    "SubmissionModel",
    "UserModel",
    "create_db_engine",
    "create_session_factory",
    "default_persistence_descriptor",
    "get_database_url",
]
