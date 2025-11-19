from pathlib import Path
import logging
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        # パイプライン設定（初期化時に1回だけ作る）
        pipeline_options = ThreadedPdfPipelineOptions(
            accelerator_options=AcceleratorOptions(
                device=AcceleratorDevice.CUDA,
            ),
            ocr_batch_size=4,
            layout_batch_size=64,
            table_batch_size=4,
            generate_picture_images=True,
            images_scale=2.0,
            do_ocr=True, # デジタルPDFならFalse推奨だが、今は検証用でTrue
        )

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=ThreadedStandardPdfPipeline,
                    pipeline_options=pipeline_options,
                )
            }
        )

    def convert(self, input_path: Path):
        """
        PDFを変換し、DoclingのDocumentオブジェクトを返す
        """
        logger.info(f"Converting PDF: {input_path}")
        try:
            result = self.converter.convert(input_path)
            if result.status != ConversionStatus.SUCCESS:
                raise Exception(f"Conversion failed with status: {result.status}")
            return result.document
        except Exception as e:
            logger.error(f"Docling conversion error: {e}")
            raise