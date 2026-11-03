
# === 埋め込み生成 ===
def embed_texts(texts):
    """
    OpenAIの埋め込みAPIを利用して、テキストリストをベクトル化
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        embeddings = [d.embedding for d in response.data]
        return np.array(embeddings, dtype="float32")
    except Exception as e:
        st.error(f"Embeddingの生成に失敗しました: {e}")
        return None


client.embeddings.createとは？
https://developers.openai.com/api/docs/guides/embeddings?lang=python
エンベディング：テキストを数値の並び(ベクトル)に変換する
公式「
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(
    input="Your text string goes here", model="text-embedding-3-small"
)
print(response.data[0].embedding)
」

レスポンス(response)にはエンベディング(ベクトル)とさまざまなメタデータが入っている。
→
「
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [
        -0.006929283495992422, -0.005336422007530928, -4.547132266452536e-5,
        -0.024047505110502243
      ]
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
」
response.data[0].embedding
でエンベディング取り出す！！
