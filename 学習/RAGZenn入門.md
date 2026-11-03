![](2026-11-03-23-00-38.png)
http://zenn.dev/knowledgesense/articles/2619c6e5918d08
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
意味わかんなぁE��ラーでる、E
、E
PS C:\work\RAG_nyuumonn_Zenn\RAG_nyuumonn_Zenn2> powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
https://astral.sh/uv/install.ps1 : 用誁E'https://astral.sh/uv/install.ps1' は、E
コマンドレチE��、E��数、スクリプト ファイル、また�E操作可能なプログラムの名前とぁE
て認識されません。名前が正しく記述されてぁE��ことを確認し、パスが含まれてぁE��場吁E
はそ�Eパスが正しいことを確認してから、�E試行してください、E
発生場所 衁E1 斁E��E40
+ ... s://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex
+                                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (https://astral.sh/uv/install.ps1 
   :String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
、E

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
ならいけるみたい。いけた�E�E��E
ↁE
原因は、コマンドではなぁEMarkdown形式�Eリンク表記をそ�Eままコピ�Eしたことです、E
現在の入力には [URL](URL) が含まれており、PowerShellは角括弧めE番目のURLまでをコマンド名として解釈してぁE��す、E
uv --version
がエラー出る、E
PS C:\work\RAG_nyuumonn_Zenn\RAG_nyuumonn_Zenn2> $env:Path = "C:\Users\user\.local\bin;$env:Path"
PS C:\work\RAG_nyuumonn_Zenn\RAG_nyuumonn_Zenn2> uv --version                    
uv 0.13.6 (329bf9448 2026-10-26 x86_64-pc-windows-msvc)
でた。インスト�Eルしたときに黁E��ぁE��ころパワーシェルで実行してと出てぁE��。みおとしてぁE��ーーーーー�E�大事なんやな。コマンド見るの

uv init
で初期化？環墁E��築！E

uvとは�E�E
pipとかvenvとか�EチE�Eルが１つでできるみたい、E
https://qiita.com/junya__ya/items/2703c11e193d0e7bb303


今回使ぁE��チE��ージめEuv で追加
uv add streamlit faiss-cpu python-dotenv openai numpy


パッケージって�E�E
誰かが作った便利な機�Eの詰め合わせのこと。ありがたく使わせてもらぁE��E
openai
faiss-cpu
numpy
python-dotenv
が�EってぁE��みたい


(rag-nyuumonn-zenn2) PS C:\work\RAG_nyuumonn_Zenn\RAG_nyuumonn_Zenn2> uv add streamlit faiss-cpu python-dotenv openai numpy
Resolved 49 packages in 104ms
error: Distribution `faiss-cpu==1.15.1 @ registry+https://pypi.org/simple` can't be installed because it doesn't have a source distribution or wheel for the current platform

hint: You're on Windows (`win_amd64`), but `faiss-cpu` (v1.15.1) only has wheels for the following platforms: `manylinux_2_27_aarch64`, `manylinux_2_27_x86_64`, `manylinux_2_28_aarch64`, `manylinux_2_28_x86_64`, `musllinux_1_2_aarch64`, `musllinux_1_2_x86_64`, `macosx_14_0_arm64`, `macosx_15_0_x86_64`; consider adding "sys_platform == 'win32' and platform_machine == 'AMD64'" to `tool.uv.required-environments` to ensure uv resolves to a version with compatible wheels

エラー冁E��
faiss-cpu==1.15.1 めEWindows 64ビット環墁E��インスト�Eルできませんでした、E
�E�？？？？？？？？？？？？？？？！E
どめE��と、E
まずヒント通り、pyproject.toml の末尾に次を追加してください、E
[tool.uv]
required-environments = [
    "sys_platform == 'win32' and platform_machine == 'AMD64'",
]
またエラー出ぁE
Pythonのバ�EジョンめE.15だと、依存関係だめみたいで3.12にした。意味わからん。けど行けぁE
だるかった�Eーーーーー�E�E��E��E��E��E
学び�E�見てぁE��サイト�E更新日とか、Pytohnのバ�EジョンがめちめE��要とか、いろんなバ�Eジョンが地味にめちめE��要。動かなくなる�Eね。だるいマジで、E

OpenAPIキー
<YOUR_OPENAI_API_KEY>

持E��したパスワード！E
yugo0504

1.5 OpenAI APIキーの設宁E
プロジェクト直下に .env とぁE��名前のファイルを作�Eして、中身に、ご自身のOpenAI APIキーを記述します、E
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

ソースコードコピ�E
チE��スト�E自刁E�E自己紹介�E容

src/rag_nyuumonn_zenn2/app.pyに
書ぁE��ため
streamlit run .\src\rag_nyuumonn_zenn2\app.py
と実行！E

開いた！E��E��E��E
ん！E


�E�ドルクレジチE��として購入

出来た！E��E��E��E��E


app.pyのソースコード読み込んでぁE��。。。。。�EつづぁE
