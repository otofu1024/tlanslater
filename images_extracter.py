from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (
    ThreadedPdfPipelineOptions,
)

pipeline_options = ThreadedPdfPipelineOptions(
        
        # 2. アクセラレータ（GPU）の指定
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.CUDA,
        ),
        
        # 3. 各処理のバッチサイズ指定
        ocr_batch_size=4,
        layout_batch_size=64, # GPUを使うレイアウト検出のバッチサイズを大きくしている
        table_batch_size=4,
    )
    
pipeline_options.do_picture_description = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document