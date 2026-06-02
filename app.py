import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="ゼロから育てる！志望動機作成アシスタント", layout="wide")

# --- カスタムCSS（壁紙・明朝体・桜色テーマ・スマホ対応） ---
st.markdown("""
<style>
/* 1. 全体のフォントを游明朝に統一 */
html, body, p, div, span, a, button, h1, h2, h3, h4, h5, h6, label {
    font-family: 'Yu Mincho', '游明朝', 'YuMincho', 'Hiragino Mincho ProN', 'HGS明朝E', serif !important;
}

/* 2. ページ全体の壁紙（和紙風テクスチャ） */
.stApp {
    background-color: #FCFAFA;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
    background-attachment: fixed;
}

/* 3. ヘッダーデザイン（PC用） */
.header-box {
    text-align: center;
    padding: 3rem 1rem;
    background-color: rgba(255, 255, 255, 0.8);
    border-bottom: 2px solid #DB90A0;
    margin-bottom: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.header-title { font-size: 2.2rem; font-weight: 700; color: #3D2D2E; }
.header-subtitle { font-size: 1.1rem; color: #5C4B4D; margin-top: 0.8rem; line-height: 1.6; }

/* 4. チャットボックスとフォームのデザイン */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 8px !important;
    padding: 25px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    margin-top: 20px;
}
.ai-box {
    background-color: #FDFEFE;
    padding: 20px 25px;
    border-radius: 8px;
    border-left: 5px solid #DB90A0;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-size: 1.05rem;
    line-height: 1.8;
}
.user-box {
    background-color: #EAE1E3;
    padding: 20px 25px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 1.05rem;
    line-height: 1.8;
}

/* サブヘッダー色 */
h3 { color: #3D2D2E !important; }

/* ★5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    /* タイトル周りの縮小 */
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; margin-bottom: 1.5rem !important; }
    
    /* チャットやフォームの余白を詰める */
    div[data-testid="stForm"] { padding: 15px !important; }
    .ai-box, .user-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    /* 見出しとテキストの縮小 */
    h3 { font-size: 1.2rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
    /* スマホ用ボタン調整（横幅いっぱいにしてタップしやすく） */
    [data-testid="stFormSubmitButton"] button, 
    .stButton button, 
    [data-testid="stLinkButton"] a {
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: center;
    }
}

/* 6. ボタンのデザイン（PC用ベース） */
[data-testid="stFormSubmitButton"] button, 
.stButton button,
[data-testid="stLinkButton"] a {
    background-color: #DB90A0 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    padding: 0.7rem 3rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    text-align: center;
    text-decoration: none !important;
    transition: all 0.3s ease;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover,
[data-testid="stLinkButton"] a:hover {
    background-color: #C27082 !important;
    transform: translateY(-2px);
}
[data-testid="stLinkButton"] a * {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown('''
<div class="header-box">
    <div class="header-title">🌱 ゼロから育てる！志望動機作成アシスタント</div>
    <div class="header-subtitle">
        まだ志望動機がまとまっていなくても大丈夫です。<br>
        AIとの対話を通じて、あなたの中にある強みや想いを引き出し、納得のいく志望動機をゼロから一緒に作り上げます。
    </div>
</div>
''', unsafe_allow_html=True)

# --- APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password")

# --- チャット履歴の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "こんにちは！志望動機作成アシスタントです。\nまずは、今回応募しようと考えている「職種」や「業界」、あるいは「気になっていること」を自由に教えてください。まとまっていなくても大丈夫ですよ。"
    })

# --- チャット履歴の表示 ---
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"<div class='ai-box'><strong>🤖 キャリアコンサルタントAI：</strong><br>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='user-box'><strong>💬 あなた：</strong><br>{msg['content']}</div>", unsafe_allow_html=True)

# --- メッセージ入力フォーム ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💻 キーボード入力、または 📱 マイクマークを押して声で回答してください", placeholder="例：事務職に挑戦したいのですが、未経験で不安です...")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        submit_btn = st.form_submit_button("💬 メッセージを送信する")
    with col2:
        reset_btn = st.form_submit_button("🔄 最初からやり直す")

# --- 送信時の処理 ---
if submit_btn and user_input:
    if not api_key:
        st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
    else:
        # ユーザーの入力を追加
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # APIの設定
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # AIへの指示（プロンプト）
        system_prompt = """
        あなたはプロのキャリアコンサルタントです。
        求職者が志望動機を作るためのサポートを行います。
        
        【ルール】
        1. 求職者の回答に対して、まずは受容と共感を示してください。
        2. その後、強みや経験を深掘りするための質問を【1回につき1つだけ】投げかけてください。
        3. 質問責めにせず、対話を引き出すような温かいトーン（寄り添い型）を維持してください。
        4. 会話を通じて「応募理由」「活かせる強み」「将来の展望」が十分に集まったと判断したら、これまでの内容をまとめた「志望動機の原案（履歴書に書けるレベル）」を提案してください。
        5. 出力にHTMLタグは使用しないでください。
        """
        
        # 履歴をまとめて送信
        chat_history = system_prompt + "\n\n【これまでの会話】\n"
        for m in st.session_state.messages:
            chat_history += f"{m['role']}: {m['content']}\n"
        
        with st.spinner("⏳ キャリアコンサルタントが返答を考えています..."):
            try:
                response = model.generate_content(chat_history)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# リセット処理
if reset_btn:
    st.session_state.messages = []
    st.rerun()

# ==================================================
# 共通最下部：ポータルサイトへの戻りボタン
# ==================================================
st.markdown("---")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
