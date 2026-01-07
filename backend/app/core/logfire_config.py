"""Logfire configuration for observability."""

import logfire


def configure_logfire() -> None:
    """Configure Logfire for the application.
    
    Call this once at application startup.
    Sends to Logfire only when LOGFIRE_TOKEN env var is set.
    """
    logfire.configure(
        service_name="show-your-app",
        send_to_logfire="if-token-present",
    )
    
    # Instrument Pydantic AI for agent tracing
    logfire.instrument_pydantic_ai()
