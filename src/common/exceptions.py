"""Pipeline exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.integration.models import SourceCatalogue


class PipelineError(Exception):
    """Base error for the pipeline."""


class SchemaError(PipelineError):
    """Input schema is missing or invalid."""


class QualityGateError(PipelineError):
    """Data quality gate failed."""


class ConfigurationError(PipelineError):
    """Configuration is missing or invalid."""


class ExternalSourceError(PipelineError):
    """An external reference source could not be loaded."""


class QueryExecutionError(PipelineError):
    """A mediated query could not be executed on the source tables."""


class KpiMismatchError(PipelineError):
    """A rewritten query disagrees with its reference KPI beyond tolerance (BR3.6)."""

    def __init__(
        self,
        message: str,
        groups: tuple[tuple[str, str, float], ...],
    ) -> None:
        super().__init__(message)
        self.groups = groups


class NoSourceAvailableError(PipelineError):
    """No source profile covers every field one query needs (BR5.6)."""

    def __init__(
        self,
        message: str,
        missing_fields: tuple[str, ...],
        catalogue: SourceCatalogue,
    ) -> None:
        super().__init__(message)
        self.missing_fields = missing_fields
        self.catalogue = catalogue


class LinkageResultMissingError(PipelineError):
    """The C5 result file has not been produced yet; not an error state, an empty one."""


class LinkageResultInvalidError(PipelineError):
    """The C5 result file cannot be read or lacks a required field."""
