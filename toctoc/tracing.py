import logging
from typing import Optional
from threading import Lock

from phoenix.config import get_env_host, get_env_port
from openinference.semconv.resource import ResourceAttributes
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk import trace as trace_sdk


LOGGER = logging.getLogger(__name__)


def setup_tracer(
    project_name: str,
    collector_endpoint: Optional[str] = None,
) -> trace_api.Tracer:
    """Setup a tracer with the given project name and collector endpoint."""
    if collector_endpoint is None:
        collector_endpoint = f"http://{get_env_host()}:{get_env_port()}/v1/traces"

    resource = Resource(
        attributes={
            ResourceAttributes.PROJECT_NAME: project_name,
        }
    )

    tracer_provider = trace_sdk.TracerProvider(resource=resource)

    span_exporter = OTLPSpanExporter(endpoint=collector_endpoint)
    simple_span_processor = SimpleSpanProcessor(span_exporter=span_exporter)

    tracer_provider.add_span_processor(span_processor=simple_span_processor)
    trace_api.set_tracer_provider(tracer_provider=tracer_provider)

    tracer = trace_api.get_tracer(__name__)

    LOGGER.info(f"Tracer setup with collector endpoint: {collector_endpoint}")
    return tracer


class TracerProvider:
    """
    A singleton class to manage the creation and retrieval of a tracer instance.

    Attributes:
        _instance (Optional[trace_api.Tracer]): The singleton tracer instance.
        _lock (Lock): A lock to ensure thread-safe initialization.
    """

    _instance: Optional[trace_api.Tracer] = None
    _lock = Lock()

    @classmethod
    def get_tracer(
        cls, project_name: str, collector_endpoint: Optional[str] = None
    ) -> trace_api.Tracer:
        """
        Get or create a singleton tracer instance.

        Args:
            project_name (str): The name of the project for the tracer.
            collector_endpoint (Optional[str]): The endpoint for the trace collector.
                Defaults to using environment variables if not provided.

        Returns:
            trace_api.Tracer: The singleton tracer instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = setup_tracer(project_name, collector_endpoint)
        return cls._instance
