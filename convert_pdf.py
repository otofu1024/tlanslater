import datetime
import logging
import time
from pathlib import Path

# ... (Docling関連のインポート) ...
import numpy as np
from pydantic import TypeAdapter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (
    ThreadedPdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline
from docling.utils.profiling import ProfilingItem

_log = logging.getLogger(__name__)

def main():
    # DoclingのログレベルをWARNINGに設定（余計な情報を表示しない）
    logging.getLogger("docling").setLevel(logging.WARNING)
    # このスクリプト自体のログレベルはINFOに設定
    _log.setLevel(logging.INFO)

    # 処理対象のPDFファイルのパスを設定
    data_folder = Path(__file__).parent / "tests/data"
    input_doc_path = data_folder / "ozawa.pdf" # 9 pages

    # === ここが最重要 ===
    
    # 1. パイプライン設定オブジェクトを作成
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
    
    # 4. OCR処理を明示的にオフ
    # pipeline_options.do_ocr = False

    # 5. DocumentConverterの初期化
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ThreadedStandardPdfPipeline,
                pipeline_options=pipeline_options, # <<< ここで設定を渡す
            )
        }
    )

    # パイプラインの初期化（モデルのロードなど）
    start_time = time.time()
    doc_converter.initialize_pipeline(InputFormat.PDF)
    init_runtime = time.time() - start_time
    _log.info(f"Pipeline initialized in {init_runtime:.2f} seconds.")

    # 変換の実行
    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    pipeline_runtime = time.time() - start_time
    
    # 結果の表示
    assert conv_result.status == ConversionStatus.SUCCESS
    num_pages = len(conv_result.pages)
    _log.info(f"Document converted in {pipeline_runtime:.2f} seconds.")
    _log.info(f" {num_pages / pipeline_runtime:.2f} pages/second.")

    # Markdownファイルとして保存
    markdown_content = conv_result.document.export_to_markdown()
    output_md_path = input_doc_path.with_suffix('.md')
    output_md_path.write_text(markdown_content, encoding='utf-8')
    _log.info(f"Markdown file saved to: {output_md_path}")


if __name__ == "__main__":
    main()