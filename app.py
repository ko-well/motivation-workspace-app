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

/* 4. フォームとコンテナのデザイン */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 8px !important;
    padding: 30px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
}

/* AIのアドバイス枠（元の青色から桜色テーマへ変更） */
.ai-box { 
    background-color: #FDFEFE; 
    padding: 25px; 
    border-radius: 8px; 
    border-left: 5px solid #DB90A0; 
    margin-bottom: 20px; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-size: 1.05rem;
    line-height: 1.8;
}

/* ユーザーの作業机枠（元の黄色から落ち着いた和紙風へ変更） */
.draft-box { 
    background-color: rgba(255, 255, 255, 0.7); 
    padding: 25px; 
    border-radius: 8px; 
    border: 2px solid #EAE1E3; 
    margin-top: 20px;
    margin-bottom: 20px;
}

/* サブヘッダー色 */
h1, h2, h3 { color: #3D2D2E !important; }

/* ★5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; }
    
    div[data-testid="stForm"] { padding: 15px !important; }
    .ai-box, .draft-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
    /* スマホ用ボタン調整（横幅いっぱい） */
    [data-testid="stFormSubmitButton"] button, 
    .stButton button, 
    [data-testid="stLinkButton"] a {
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: center;
        margin-bottom: 10px !important;
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
    background-color: #C2
