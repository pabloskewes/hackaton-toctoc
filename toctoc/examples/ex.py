from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)

from src.tracing import setup_tracer


if __name__ == "__main__":
    tracer = setup_tracer(project_name="prep-toctoc")

    with tracer.start_as_current_span("main") as span:
        span.set_attribute("example", "value")
        span.add_event("event in main")

        with tracer.start_as_current_span("sub-span") as sub_span:
            sub_span.set_attribute("example", "value")
            sub_span.add_event("event in sub-span")
            sub_span.record_exception(ValueError("error in sub-span"))

        span.add_event("another event in main")

        span.set_attributes(
            {
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
                SpanAttributes.INPUT_VALUE: "Este es el input de la LLM",
                SpanAttributes.OUTPUT_VALUE: "Este es el output de la LLM",
            }
        )
