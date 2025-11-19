# LM StudioはOpenAI互換のAPIを提供
from openai import OpenAI

# LM StudioにホストされているAPIサーバーに接続
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

text = """01:52 Nguyen Tien Nhat I’ll have a flight back to Vietnam tomorrow so I’ll need to wake up at 6am. I’ll give a small gift for anyone slam my door to wake me up at 6am!
01:53 Nguyen Tien Nhat I live in 202
01:53 Nguyen Tien Nhat If you’re a girl you can use the delivery bell at the entrance"""
input_lang = "English"
output_lang = "Japanese"

def tlanslate(text, input_lang, output_lang):
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
    return response.choices[0].message.content

# 生成されたテキスト応答を表示
print(tlanslate(text, input_lang, output_lang))
