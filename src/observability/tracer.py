"""Distributed tracing setup."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_tracing(
    service_name: str = "rag-system",
    enable: bool = True,
    endpoint: Optional[str] = None
) -> None:
    """
    Setup distributed tracing.
    
    Args:
        service_name: Name of the service
        enable: Whether to enable tracing
        endpoint: Optional tracing endpoint
    """
    if not enable:
        logger.info("Tracing disabled")
        return
    
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource
        
        # Create resource
        resource = Resource.create({"service.name": service_name})
        
        # Setup tracer provider
        provider = TracerProvider(resource=resource)
        
        # Add console exporter for development
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        # Set as global tracer provider
        trace.set_tracer_provider(provider)
        
        logger.info(f"Tracing setup complete for service: {service_name}")
    
    except ImportError:
        logger.warning("OpenTelemetry not installed, tracing disabled")
    except Exception as e:
        logger.error(f"Error setting up tracing: {e}")


def get_tracer(name: str):
    """
    Get a tracer instance.
    
    Args:
        name: Tracer name
        
    Returns:
        Tracer instance
    """
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        logger.warning("OpenTelemetry not available")
        return None

