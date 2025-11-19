import logging
import time
from pathlib import Path

# ... (Docling関連のインポート) ...
from pydantic import TypeAdapter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (
    ThreadedPdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline
from docling.utils.profiling import ProfilingItem

# ★追加: ドキュメントの個々の要素を識別するために必要
from docling.datamodel.document import PictureItem, TableItem, TextItem, SectionHeaderItem, ListItem

_log = logging.getLogger(__name__)

def main():
    logging.getLogger("docling").setLevel(logging.WARNING)
    _log.setLevel(logging.INFO)

    data_folder = Path(__file__).parent / "tests/data"
    input_doc_path = data_folder / "test.pdf"

    # 1. パイプライン設定
    pipeline_options = ThreadedPdfPipelineOptions(
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.CUDA,
        ),
        ocr_batch_size=4,
        layout_batch_size=64,
        table_batch_size=4,
        
        # ★追加: これがないと画像データが生成されず、保存できない
        generate_picture_images=True,
        images_scale=2.0,
        # OCR設定
        do_ocr=True,
    )


    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ThreadedStandardPdfPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )

    start_time = time.time()
    doc_converter.initialize_pipeline(InputFormat.PDF)
    init_runtime = time.time() - start_time
    _log.info(f"Pipeline initialized in {init_runtime:.2f} seconds.")

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    pipeline_runtime = time.time() - start_time
    
    assert conv_result.status == ConversionStatus.SUCCESS
    num_pages = len(conv_result.pages)
    _log.info(f"Document converted in {pipeline_runtime:.2f} seconds.")

    # === ★ここから下が大きく変わる部分 ===
    # export_to_markdown() 一発ではなく、手動で組み立てる
    
    doc = conv_result.document
    output_dir = input_doc_path.parent  # PDFと同じフォルダに出力
    images_dir = output_dir / "images"  # 画像用サブフォルダ
    images_dir.mkdir(exist_ok=True)

    md_lines = []
    image_counter = 0

    _log.info("Constructing Markdown and saving images...")

    # ドキュメントの要素を順番に処理
    for item, level in doc.iterate_items():
        
        # --- 画像の場合 ---
        if isinstance(item, PictureItem):
            if item.image:
                image_counter += 1
                # ファイル名決定
                image_filename = f"{input_doc_path.stem}_img_{image_counter}.png"
                save_path = images_dir / image_filename
                
                # 画像保存
                pil_image = item.get_image(doc)
                if pil_image:
                    pil_image.save(save_path)
                    print(f"Saved: {save_path}")
                
                # Markdownには相対パスでリンクを貼る
                # (Markdownファイルから見て images/filename.png)
                rel_path = f"./images/{image_filename}"
                md_lines.append(f"\n![Image]({rel_path})\n")
            else:
                md_lines.append("\n\n")

        # --- その他の要素はMarkdown形式に変換して追加 ---
        elif isinstance(item, TableItem):
            md_lines.append(f"\n{item.export_to_markdown(doc=doc)}\n")
        elif isinstance(item, SectionHeaderItem):
            prefix = "#" * (level + 1)
            md_lines.append(f"\n{prefix} {item.text}\n")
        elif isinstance(item, ListItem):
            md_lines.append(f"* {item.text}")
        elif isinstance(item, TextItem):
            md_lines.append(f"{item.text}\n")

    # Markdown保存
    output_md_path = input_doc_path.with_suffix('.md')
    
    # 書き込み
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    _log.info(f"Markdown file saved to: {output_md_path}")
    _log.info(f"Images saved to: {images_dir}")

if __name__ == "__main__":
    main()