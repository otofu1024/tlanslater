# LM StudioはOpenAI互換のAPIを提供
from openai import OpenAI

# LM StudioにホストされているAPIサーバーに接続
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

text = """Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
2025-11-19 01:07:05,231 - WARNING - Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
2025-11-19 01:07:52,939 - WARNING - Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`"""
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