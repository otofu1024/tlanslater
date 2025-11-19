import logging
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExporter:
    def __init__(self):
        # Windowsで確実に日本語を表示するためのCSS
        # "Meiryo", "Yu Gothic", "MS Gothic" などシステムにあるフォントを指定
        self.css_string = """
        @page {
            size: A4;
            margin: 2.5cm;
        }
        body {
            font-family: "Meiryo", "Yu Gothic", sans-serif;
            font-size: 10pt;
            line-height: 1.6;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        h1, h2, h3 {
            color: #333;
            page-break-after: avoid;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        """

    def export(self, markdown_text: str, output_pdf_path: Path, base_url: Path):
        """
        MarkdownテキストをPDFに変換して保存する
        
        Args:
            markdown_text: 変換元のMarkdown文字列
            output_pdf_path: 保存先のPDFパス
            base_url: 画像などの相対パスを解決するための基準ディレクトリ（重要！）
        """
        logger.info(f"Generating PDF: {output_pdf_path}")

        try:
            # 1. Markdown -> HTML
            # "tables" 拡張で表組みに対応
            html_content = markdown.markdown(
                markdown_text, 
                extensions=['tables', 'fenced_code']
            )

            # 2. HTML -> PDF (WeasyPrint)
            font_config = FontConfiguration()
            css = CSS(string=self.css_string, font_config=font_config)
            
            # base_urlを指定しないと、画像（./images/xxx.png）が見つからない
            html = HTML(string=html_content, base_url=str(base_url))
            
            html.write_pdf(
                output_pdf_path,
                stylesheets=[css],
                font_config=font_config
            )
            logger.info("PDF generation successful.")

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # ここで raise するかは設計次第だが、今回はログだけ出して落ちないようにする
            raise

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    input_md = base_dir / "tests/data/test_translated.md"
    output_pdf = base_dir / "tests/data/test_translated.pdf"
    base_url = input_md.parent

    markdown_text = input_md.read_text(encoding="utf-8")
    pdf_exporter = PDFExporter()
    pdf_exporter.export(markdown_text, output_pdf, base_url)
    logger.info(f"PDF saved to: {output_pdf}")