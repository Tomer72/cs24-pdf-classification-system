import pikepdf
import io
import logging
from .interface import BasePDFOptimizer

logger = logging.getLogger(__name__)

class LinearizationOptimizer(BasePDFOptimizer):
    def optimize(self, file_bytes):
        try:
            input_stream = io.BytesIO(file_bytes)

            with pikepdf.open(input_stream) as pdf:
                output_stream = io.BytesIO()

                pdf.save(output_stream, linearize=True)

                optimized_data = output_stream.getvalue()

                logger.info(f"Linearization: original= {len(file_bytes)}, linearized: {len(optimized_data)} ")
                return optimized_data
        
        except Exception as e:
            logger.error(f"optimization failed: {e}")

            return file_bytes