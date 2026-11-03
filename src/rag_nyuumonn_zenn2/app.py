import os
from pathlib import Path

import numpy as np
import faiss
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# === 設定 ===
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-5"  # GPT-5系モデル
TOP_K = 3  # 何件のドキュメントを参照するか

# === OpenAIクライアントの初期化 ===
load_dotenv()#python-dotenvが.envを読み込み、環境変数として登録。
try:
    # .env の OPENAI_API_KEY を読む   api_key=OPENAI_API_KEY=sk-~~~を登録。
    #通常はclient=OpenAI()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    st.error(f"OpenAI APIキーの読み込みに失敗しました。.envファイルを確認してください。: {e}")
    st.stop()


# === ドキュメント読み込み ===
def load_documents(data_dir: str = "data"):
    """
    'data'ディレクトリから.txtファイルを読み込む
    """
    docs = []
    base = Path(data_dir)
    if not base.exists():
        st.error(f"'{data_dir}' ディレクトリが見つかりません。作成してください。")
        return []

    for p in base.glob("*.txt"):#dataディレクトリ内の.txtとつくファイルの一覧を１つ１つ見ていく
        try:
            text = p.read_text(encoding="utf-8")
            docs.append(
                {
                    "id": p.name,
                    "path": str(p),
                    "text": text,
                }
            )
            print(
            f"p={p}\n"
            f"id={docs[0]['id']}\n"
            f"path={docs[0]['path']}\n"
            f"text文字数={len(docs[0]['text'])}\n"
            f"text冒頭={docs[0]['text'][:100]!r}\n"
            )
        except Exception as e:
            st.warning(f"ファイル {p.name} の読み込みに失敗しました: {e}")
            
    return docs


# === 埋め込み生成 ===　テキストのベクトルをリストで返す。
def embed_texts(texts):
    """
    OpenAIの埋め込みAPIを利用して、テキストリストをベクトル化
    """
    try:
        resp = client.embeddings.create(#レスポンス(resp)にはエンベディング(ベクトル)とさまざまなメタデータが入っている。
            model=EMBEDDING_MODEL,
            input=texts,#テキストの全文が入っている
        )
        embeddings = [d.embedding for d in resp.data]#エンベディング(数字の羅列(テキストのベクトル))をリストに格納
        return np.array(embeddings, dtype="float32")#リスト返すよーーーーーーー！
    except Exception as e:
        st.error(f"Embeddingの生成に失敗しました: {e}")
        return None


# === ベクトルインデックスの構築 ===
@st.cache_resource(show_spinner="ドキュメントをベクトル化しています...")
def build_index():
    """
    ドキュメントを読み込み、ベクトル化し、Faissインデックスを構築する
    """
    docs = load_documents()
    if not docs:
        st.error("data/ 配下に .txt ファイルがありません。RAGの検索対象となるファイルを追加してください。")
        st.stop()

    texts = [d["text"] for d in docs]
    embeddings = embed_texts(texts)#テキストのベクトルをリストで返す。
    
    if embeddings is None:
        st.error("Embeddingの生成に失敗したため、インデックスを構築できません。")
        st.stop()

    dim = embeddings.shape[1]#ここ何してんだー？？？？？？？？？
    index = faiss.IndexFlatL2(dim)  # L2距離（ユークリッド距離）
    index.add(embeddings)

    return index, embeddings, docs


# === 検索（Retrieval） ===
def search_similar_docs(query: str, index, docs, k: int = TOP_K):
    """
    質問文をベクトル化し、Faissで類似ドキュメントを検索する
    """
    query_emb = embed_texts([query])  # shape: (1, dim)
    if query_emb is None:
        return []
        
    distances, indices = index.search(query_emb, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = docs[int(idx)]
        results.append(
            {
                "score": float(dist),
                "doc_id": doc["id"],
                "path": doc["path"],
                "text": doc["text"],
            }
        )
    return results


# === プロンプト組み立て ===
def build_rag_prompt(question: str, retrieved_docs):
    """
    検索結果と質問文を組み合わせて、LLMへのプロンプトを作成する
    """
    # コンテキストとして使うテキスト（長すぎるときは適当に切る）
    max_chars = 1000
    context_parts = []
    for r in retrieved_docs:
        t = r["text"]
        if len(t) > max_chars:
            t = t[:max_chars] + "\n...(以下略)"
        context_parts.append(f"[{r['doc_id']}]\n{t}")

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "あなたは社内ドキュメントに基づいて回答するアシスタントです。"
        "コンテキストに書かれていないことは推測せず、「分かりません」と答えてください。"
    )

    user_prompt = f"""以下は社内ドキュメントから抽出したコンテキストです。

# コンテキスト
{context}

---
# ユーザーからの質問
{question}

---
上記コンテキストの内容だけを根拠に、日本語で丁寧に回答してください。
コンテキストに十分な情報がない場合は、その旨を正直に伝えてください。
"""

    return system_prompt, user_prompt


# === 回答生成（Generation） ===
def generate_answer(system_prompt: str, user_prompt: str):
    """
    OpenAI Responses APIを叩いて回答を生成する
    """
    try:
        resp = client.responses.create(
            model=CHAT_MODEL,
            instructions=system_prompt,
            input=user_prompt,
            # GPT-5は temperature 固定なので指定しない
        )
        # すべてのテキスト出力が一つにまとまったプロパティ
        return resp.output_text
    except Exception as e:
        st.error(f"OpenAI APIの呼び出しに失敗しました: {e}")
        return None


# === Streamlit UI ===
def main():
    st.set_page_config(page_title="RAGをゼロから実装する【2025年版】", layout="wide")
    st.title("RAGをゼロから実装して仕組みを学ぶ【2025年版】")
    st.caption(f"モデル: {CHAT_MODEL} | Embedding: {EMBEDDING_MODEL} | 検索: Faiss")

    st.write(
        f"このデモでは、ローカルの `{Path('data').resolve()}` フォルダ内にある `.txt` ドキュメントを検索対象にした、シンプルなRAGを実装しています。"
    )

    # インデックス構築
    try:
        index, embeddings, docs = build_index()
    except Exception as e:
        st.error(f"インデックスの構築に失敗しました。: {e}")
        st.stop()

    with st.sidebar:
        st.header("設定")
        top_k = st.slider("参照するドキュメント数", 1, 10, TOP_K)

        st.markdown("### 読み込まれたドキュメント一覧")
        if docs:
            for d in docs:
                st.markdown(f"- `{d['id']}`")
        else:
            st.warning("ドキュメントがありません。")

    question = st.text_input("質問を入力してください（例：ナレッジセンスとは？）")
    run = st.button("RAGに聞いてみる")

    if run and question:
        with st.spinner("検索 & 回答生成中..."):
            # 1. 検索
            retrieved = search_similar_docs(question, index, docs, k=top_k)
            
            if not retrieved:
                st.error("検索に失敗しました。")
                st.stop()

            # 2. プロンプト作成
            system_prompt, user_prompt = build_rag_prompt(question, retrieved)

            # 3. 回答生成
            answer = generate_answer(system_prompt, user_prompt)

        if answer:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🤖 回答")
                st.write(answer)

            with col2:
                st.subheader("📚 検索されたコンテキスト")
                for r in retrieved:
                    with st.expander(f"`{r['doc_id']}`（類似スコア: {r['score']:.4f}）"):
                        st.text(r["text"][:1500])  # 表示しすぎると重いので適当に切る
        else:
            st.error("回答の生成に失敗しました。")

    elif run and not question:
        st.warning("質問を入力してください。")


if __name__ == "__main__":
    main()