# setting jager
# provider = TracerProvider()
# processor = BatchSpanProcessor(ConsoleSpanExporter())
# provider.add_span_processor(processor)
# trace.set_tracer_provider(
#     TracerProvider(
#         resource=Resource.create({SERVICE_NAME: "vtpad"})
#     )
# )
# jaeger_exporter = JaegerExporter(
#     agent_host_name=f"{config.jaeger_host}",
#     agent_port=6831,
# )
#
# trace.get_tracer_provider().add_span_processor(
#     BatchSpanProcessor(jaeger_exporter)
# )
#
# tracer = trace.get_tracer(__name__)

# end settings

# register jager for app
# TortoiseORMInstrumentor().instrument(tracer_provider=trace)
# RequestsInstrumentor().instrument()
# FastAPIInstrumentor.instrument_app(app)
