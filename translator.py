from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class PLaMoTranslator:
    def __init__(self, base_url="http://localhost:1234/v1", api_key="not-needed"):
        # 念のため /v1 を強制
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if not base_url.endswith("/v1"):
            base_url = base_url + "/v1"

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = "plamo-2-translate"

        logger.warning(f"OpenAI base_url = {base_url}")

    def translate(self, text: str, input_lang="English", output_lang="Japanese") -> str:
        """
        テキストを受け取り、翻訳して返す
        """
        # 空文字や短すぎる文字は翻訳せずそのまま返す（コスト削減・エラー回避）
        if not text or len(text.strip()) < 2:
            return text

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", 
                    "content": f"""<|plamo:op|>dataset
                    translation
                    <|plamo:op|>input lang={input_lang}
                    {text}
                    <|plamo:op|>output lang={output_lang}"""}
                ],
                # 必要に応じてmax_tokensやtemperatureも設定
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text # エラー時は原文を返す（システムを止めないため）

if __name__ == "__main__":
    print(PLaMoTranslator().translate("Hello, world!"))