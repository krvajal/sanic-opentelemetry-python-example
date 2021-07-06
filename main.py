from opentelemetry import trace, context
from sanic import Sanic
from sanic.response import text
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.instrumentation.propagators import (
    get_global_response_propagator,
)
from opentelemetry.propagate import set_global_textmap, extract
from opentelemetry.propagators.b3 import B3Format

from tracing import instrument_app

set_global_textmap(B3Format())

app = Sanic("My Hello, world app")


provider = TracerProvider()
processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)


instrument_app(app,tracer)

@app.get("/")
async def handler(request):
    with tracer.start_as_current_span("foo"):
        print(request.headers)
        return text(str(request.id))

app.run(host="0.0.0.0", port=1234,)
