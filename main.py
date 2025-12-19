import logging
import time
from pathlib import Path

# === 自作モジュールのインポート ===
# ※ファイル名やクラス名が違う場合はここを修正してください
from translator import PLaMoTranslator
from convert_md import MdProcessor
from pdf_exporter import PDFExporter

# === Doclingの型定義（アイテム識別用） ===
from docling_core.types.doc import (
    PictureItem,
    TableItem,
    TextItem,
    SectionHeaderItem,
    ListItem,
    CodeItem,
    FormulaItem,
)

# === ログ設定 ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
# ライブラリのログがうるさいので黙らせる
logging.getLogger("docling").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    # ---------------------------------------------------------
    # 1. 設定と準備
    # ---------------------------------------------------------
    base_dir = Path(__file__).parent
    # テスト用PDFのパス（実際運用時はここを引数などで変える）
    input_pdf = base_dir / "tests/data/amazon-dynamo-sosp2007.pdf"
    
    # 出力先の設定
    output_dir = input_pdf.parent
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Target PDF: {input_pdf}")

    # ---------------------------------------------------------
    # 2. インスタンス化（モデルロード）
    # ---------------------------------------------------------
    logger.info("Initializing modules...")
    
    # PDF解析エンジンの起動
    try:
        processor = MdProcessor()
    except Exception as e:
        logger.critical(f"Failed to initialize MdProcessor: {e}")
        return
    try:
        pdf_exporter = PDFExporter()
    except Exception as e:
        logger.critical(f"Failed to initialize PDFExporter: {e}")
        return

    # 翻訳エンジンの起動 (LM Studioなどが動いている前提)
    try:
        translator = PLaMoTranslator()
    except Exception as e:
        logger.critical(f"Failed to initialize Translator: {e}")
        return

    # ---------------------------------------------------------
    # 3. PDF解析の実行
    # ---------------------------------------------------------
    logger.info("Starting PDF conversion...")
    start_time = time.time()
    
    try:
        doc = processor.convert(input_pdf)
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        return

    logger.info(f"PDF parsed in {time.time() - start_time:.2f}s")

    # ---------------------------------------------------------
    # 4. 再構築ループ（画像保存 & 翻訳）
    # ---------------------------------------------------------
    logger.info("Starting translation and reconstruction loop...")

    md_lines = []
    md_translated_lines = []
    image_counter = 0

    # ドキュメントを頭からお尻まで舐める
    for item, level in doc.iterate_items():

        # --- A. 画像アイテム (保存してリンク) ---
        if isinstance(item, PictureItem):
            pil_image = item.get_image(doc)
            if pil_image:
                image_counter += 1
                # ファイル名の生成は画像が取れた時だけ行う
                filename = f"{input_pdf.stem}_img_{image_counter}.png"
                save_path = images_dir / filename

                pil_image.save(save_path)
                rel_path = f"./images/{filename}"
                md_translated_lines.append(f"\n![Image]({rel_path})\n")
                md_lines.append(f"\n![Image]({rel_path})\n")
                logger.debug(f"Saved image: {filename}")
            else:
                md_translated_lines.append("\n<!-- Empty Image Box -->\n")
                md_lines.append("\n<!-- Empty Image Box -->\n")

        # --- B. 表 (Markdown化のみ) ---
        elif isinstance(item, TableItem):
            # 翻訳はリスクが高いので一旦そのまま
            md_lines.append(f"\n{item.export_to_markdown(doc=doc)}\n")
            md_translated_lines.append(f"\n{item.export_to_markdown(doc=doc)}\n")

        # --- C. コードブロック (Markdown化のみ) ---
        elif isinstance(item, CodeItem):
            md_translated_lines.append(f"\n```{item.code_language}\n{item.text}\n```\n")
            md_lines.append(f"\n```{item.code_language}\n{item.text}\n```\n")

        # --- D. 数式 (Markdown化のみ) ---
        elif isinstance(item, FormulaItem):
            md_translated_lines.append(f"\n$$\n{item.text}\n$$\n")
            md_lines.append(f"\n$$\n{item.text}\n$$\n")

        # --- E. 見出し (翻訳) ---
        elif isinstance(item, SectionHeaderItem):
            prefix = "#" * (level + 1)
            # テキストを翻訳機に投げる
            translated_text = translator.translate(item.text)
            md_lines.append(f"\n{prefix} {item.text}\n")
            md_translated_lines.append(f"\n{prefix} {translated_text}\n")
            logger.info(f"Header: {item.text[:10]}... -> {translated_text[:10]}...")

        # --- F. リスト (翻訳) ---
        elif isinstance(item, ListItem):
            translated_text = translator.translate(item.text)
            md_lines.append(f"* {item.text}")
            md_translated_lines.append(f"* {translated_text}")

        # --- G. 本文 (翻訳) ---
        elif isinstance(item, TextItem):
            # 空行や意味のない短い文字はスキップしても良いが、Translator側で制御推奨
            translated_text = translator.translate(item.text)
            md_lines.append(f"{item.text}\n")
            md_translated_lines.append(f"{translated_text}\n")
            # 進捗が見えるように少しログを出す
            if len(item.text) > 20:
                logger.info(f"Text translated ({len(item.text)} chars)")


    # ---------------------------------------------------------
    # 5. ファイル保存
    # ---------------------------------------------------------
    output_md = input_pdf.with_name(f'{input_pdf.stem}_translated.md')
    output_md_lines = input_pdf.with_name(f'{input_pdf.stem}_lines.md')
    translated_content = "\n".join(md_translated_lines)
    raw_content = "\n".join(md_lines)
    try:
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(translated_content)
        with open(output_md_lines, "w", encoding="utf-8") as f:
            f.write(raw_content)
        logger.info(f"SUCCESS! Markdown saved to: {output_md}")
    except IOError as e:
        logger.error(f"Failed to save file: {e}")
        return

    # ---------------------------------------------------------
    # 6. PDF変換
    # ---------------------------------------------------------
    output_pdf = input_pdf.with_name(f'{input_pdf.stem}_translated.pdf')
    try:
        pdf_exporter.export(
            markdown_text=translated_content,
            output_pdf_path=output_pdf,
            base_url=output_md.parent
        )
        logger.info(f"PDF saved to: {output_pdf}")
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")

if __name__ == "__main__":
    main()
