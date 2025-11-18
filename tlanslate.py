# LM StudioはOpenAI互換のAPIを提供
from openai import OpenAI

# LM StudioにホストされているAPIサーバーに接続
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

text = """Converting PDF documents back into a machine-processable format has been a major challenge for decades due to their huge variability in formats, weak standardization and printing-optimized characteristic, which discards most structural features and metadata. With the advent of LLMs and popular application patterns such as retrieval-augmented generation (RAG), leveraging the rich content embedded in PDFs has become ever more relevant. In the past decade, several powerful document understanding solutions have emerged on the market, most of which are commercial software, cloud offerings [3] and most recently, multi-modal vision-language models. As of today, only a handful of open-source tools cover PDF conversion, leaving a significant feature and quality gap to proprietary solutions."""
input_lang = "English"
output_lang = "Japanese"

# plamo-2-translate モデルでテキスト生成
response = client.chat.completions.create(
    model="plamo-2-translate",  # plamo-2-translateモデルを指定
    messages=[
        {"role": "user", 
        "content": f"""<|plamo:op|>dataset
        translation
        <|plamo:op|>input lang={input_lang}
        {text}
        <|plamo:op|>output lang={output_lang}"""}
    ],  # ユーザーからの入力メッセージ
)

# 生成されたテキスト応答を表示
print(response.choices[0].message.content)