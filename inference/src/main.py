"""
Baker Compliant AI - Inference Service Entry Point

This module starts the inference service that processes AI requests from the queue.
The service runs continuously, polling for new requests and processing them with
appropriate agents while maintaining SEC compliance and proper resource management.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path so we can import from other modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from inference.src.utils.config import InferenceSettings
from inference.src.utils.logging import configure_logging, logger
from inference.src.services.inference_service import run_inference_service


async def main() -> None:
    """Main entry point for the inference service."""
    try:
        # Load configuration
        settings = InferenceSettings()
        
        # Configure logging
        configure_logging(
            log_level=settings.service.log_level,
            service_name=settings.service_name
        )
        
        logger.info(
            "Starting Baker Compliant AI Inference Service",
            version="1.0.0",
            service_config=settings.service.model_dump()
        )
        
        # Run the inference service
        await run_inference_service()
        
    except KeyboardInterrupt:
        logger.info("Inference service shutdown requested by user")
    except Exception as e:
        logger.error(
            "Inference service startup failed",
            error=str(e),
            exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    # Run the service
    asyncio.run(main())