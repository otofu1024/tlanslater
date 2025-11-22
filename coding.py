from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline


def main():
    # 1. 設定 (CodeFormulaV2を有効化)
    pipeline_options = ThreadedPdfPipelineOptions(
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.CUDA,
        ),
        ocr_batch_size=4,
        layout_batch_size=64,
        table_batch_size=4,
        generate_picture_images=True,
        
        # ★コード認識と数式認識をONにする
        do_code_enrichment=True,
        do_formula_enrichment=True,
        
        images_scale=2.0,
    )

    # 2. コンバーター初期化
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=ThreadedStandardPdfPipeline,
            pipeline_options=pipeline_options,
        )
    })

    # 3. 実行 (LLM関連の論文など、コードが含まれるPDFを指定)
    target_url = "tests/data/coding-for-researchers.pdf" # またはローカルパス
    print(f"Converting: {target_url}...")
    
    result = converter.convert(target_url)
    doc = result.document
    with open("coding.md", "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown(doc=doc))

if __name__ == "__main__":
    main()