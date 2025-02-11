from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from sociedadecivil.base import config

resource = Resource(attributes={
    "service.name": "service"
})

provider = TracerProvider(resource=resource)

provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint='http://localhost:4318')))

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

def get_tracer(name):
    return OtelWrapper(trace.get_tracer(name))

class OtelWrapper:
    
    def __init__(self, tracer):
        self.tracer = tracer
    
    def start_span(self, name):
        span = self.tracer.start_as_current_span(name)
        wrapper = OtelWrapperSpan(span)
        return wrapper

class OtelWrapperSpan:
    def __init__(self, span):
        self.span = span
    
    def __enter__(self):
        self.span = self.span.__enter__()
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.span.__exit__(exception_type, exception_value, exception_traceback)
        print("=========== EXITED =============")

    def __add_event__(self, message, log_level):
        self.span.add_event(message, {"verbosity_level": log_level})

    def error(self, message, ex=None):
        self.span.set_status(Status(StatusCode.ERROR))
        self.__add_event__(message, "error")
        if ex is not None:
            self.span.record_exception(ex)

    def warn(self, message):
        if config.trace_level >= config.TraceLevels.WARN.value:
            self.__add_event__(message, "warn")

    def info(self, message):
        if config.trace_level >= config.TraceLevels.INFO.value:
            self.__add_event__(message, "info")

    def debug(self, message):
        if config.trace_level >= config.TraceLevels.DEBUG.value:
            self.__add_event__(message, "debug")

