from opentelemetry import trace, context
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.propagate import set_global_textmap, extract
from opentelemetry.propagators.b3 import B3Format
set_global_textmap(B3Format())

def instrument_app(app, tracer):
    _ENVIRON_SPAN_KEY = "opentelemetry-sanic.span_key"
    _ENVIRON_ACTIVATION_KEY = "opentelemetry-sanic.activation_key"
    @app.on_request
    def on_before_request(req):
        context.attach(extract(req.headers))
        span = tracer.start_span(
            "sanic.request",
            kind=trace.SpanKind.SERVER,

        )
        activation = trace.use_span(span, end_on_exit=True)
        activation.__enter__()

        span.set_attribute(SpanAttributes.HTTP_METHOD, req.method)
        span.set_attribute(SpanAttributes.HTTP_ROUTE, req.path)
        span.set_attribute(SpanAttributes.HTTP_ROUTE, req.path)
        req.ctx.tracing = {_ENVIRON_ACTIVATION_KEY: activation, _ENVIRON_SPAN_KEY: span}

    @app.on_response
    def on_after_request(req, res):
        if hasattr(req.ctx, "tracing"):
            req.ctx.tracing[_ENVIRON_SPAN_KEY].set_attribute(SpanAttributes.HTTP_STATUS_CODE, res.status)
            req.ctx.tracing[_ENVIRON_ACTIVATION_KEY].__exit__(None,None,None)
