"""Pipeline exceptions."""

from __future__ import annotations


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
