import logging
from typing import Optional

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
