import logging
import time
from pathlib import Path

# === 自作モジュールのインポート ===
# ※ファイル名やクラス名が違う場合はここを修正してください
from translator import PLaMoTranslator
from convert_md import MdProcessor

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
    base_dir = Path(__file__).parent
    input_pdf = base_dir / "tests/data/Pinocchio.pdf"

    output_dir = input_pdf.parent
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Target PDF: {input_pdf}")

    logger.info("Initializing modules...")

    try:
        processor = MdProcessor()
    except Exception as e:
        logger.critical(f"Failed to initialize MdProcessor: {e}")
        return

    logger.info("Starting PDF conversion...")
    start_time = time.time()

    try:
        doc = processor.convert(input_pdf)
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        return

    logger.info(f"PDF parsed in {time.time() - start_time:.2f}s")

    logger.info("Starting reconstruction loop...")

    md_lines = []
    image_counter = 0

    for item, level in doc.iterate_items():
        if isinstance(item, PictureItem):
            if item.image:
                image_counter += 1
                filename = f"{input_pdf.stem}_img_{image_counter}.png"
                save_path = images_dir / filename

            pil_image = item.get_image(doc)
            if pil_image:
                pil_image.save(save_path)
                rel_path = f"./images/{filename}"
                md_lines.append(f"\n![Image]({rel_path})\n")
                logger.debug(f"Saved image: {filename}")
            else:
                md_lines.append("\n<!-- Empty Image Box -->\n")

        elif isinstance(item, TableItem):
            md_lines.append(f"\n{item.export_to_markdown(doc=doc)}\n")

        elif isinstance(item, CodeItem):
            md_lines.append(f"\n```{item.code_language}\n{item.text}\n```\n")

        elif isinstance(item, FormulaItem):
            md_lines.append(f"\n$$\n{item.text}\n$$\n")
            logger.info(f"Formula item encountered; {item}...")

        elif isinstance(item, SectionHeaderItem):
            prefix = "#" * (level + 1)
            md_lines.append(f"\n{prefix} {item.text}\n")

        elif isinstance(item, ListItem):
            md_lines.append(f"* {item.text}")

        elif isinstance(item, TextItem):
            md_lines.append(f"{item.text}\n")
            if len(item.text) > 20:
                logger.info(f"Text processed ({len(item.text)} chars)")

    output_md = input_pdf.with_name(f'{input_pdf.stem}_lines.md')
    try:
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        logger.info(f"SUCCESS! Markdown saved to: {output_md}")
    except IOError as e:
        logger.error(f"Failed to save file: {e}")

if __name__ == "__main__":
    main()