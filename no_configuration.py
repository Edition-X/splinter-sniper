from opentelemetry import trace

with trace.get_tracer(__name__).start_as_current_span("foo"):
    with trace.get_tracer(__name__).start_as_current_span("bar"):
        print("baz")
