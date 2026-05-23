import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="ゼロから育てる！志望動機作成アシスタント", layout="wide")

st.markdown("""
<style>
h1, h2, h3 { color: #2C3E50 !important; }
.ai-box { background-color: #EBF5FB; padding: 20px; border-radius: 10px; border-left: 5px solid #3498DB; margin-bottom: 20px; }
.draft-box { background-color: #FEF9E7; padding: 15px; border-radius: 10px; border: 2px solid #F1C40F; }
[data-testid="stFormSubmitButton"] button, .main-btn button { background-color: #E67E22 !important; color: white !important; font-size: 18px !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; }
.sub-btn button { background-color: #95A5A6 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 ゼロから育てる！志望動機作成アシスタント")
st.write("AIと一緒に、あなたの中に眠っている強みを引き出し、あなただけの志望動機を少しずつ育てていきましょう！")
st.markdown("---")

# --- APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password")

# --- セッション状態の初期化 ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'action_count' not in st.session_state:
    st.session_state.action_count = 1
if 'draft' not in st.session_state:
    st.session_state.draft = ""
if 'ai_message' not in st.session_state:
    st.session_state.ai_message = ""

# ==================================================
# ステップ0：準備（情報の入力）
# ==================================================
if st.session_state.step == 0:
    st.header("ステップ0：まずはあなたのことを教えてください")
    st.write("完璧な文章じゃなくて大丈夫です。箇条書きや、短い言葉で思いつくままに入力してください。")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.text_input("年齢（例：30代）")
            gender = st.selectbox("性別", ["回答しない", "男性", "女性", "その他"])
            history = st.text_area("簡単な職歴（例：事務職5年、販売職3年など）")
        
        with col2:
            passion = st.text_area("仕事で「こだわったこと」「評価されたこと」「時間を忘れて夢中になったこと」")
            strengths = st.text_input("あなたの「強み」や「大切にしている価値観」")
            company_appeal = st.text_area("応募先の会社の「ここがいいな」と思ったところ")
            
        st.subheader("📝 今の志望動機のメモ（最初のタネ）")
        initial_memo = st.text_area("上手く書けていなくてもOKです。今の段階で書けることを入力してください。", height=100)
        
        submit_0 = st.form_submit_button("AIと一緒に志望動機を育て始める ✨")
        
    if submit_0:
        if not api_key:
            st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
        elif not initial_memo or not passion:
            st.warning("⚠️ 必須項目（こだわったこと、志望動機メモ）を入力してください。")
        else:
            # データを保存
            st.session_state.user_info = f"年齢:{age}, 性別:{gender}, 職歴:{history}, 夢中になったこと:{passion}, 強み:{strengths}"
            st.session_state.company_appeal = company_appeal
            st.session_state.draft = initial_memo
            
            # 初回のAIメッセージ生成
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt0 = f"""
            あなたは初学者に寄り添う、温かく肯定的なキャリアコンサルタントです。
            以下の求職者情報と「志望動機のメモ」を読み、絶対に全文を代筆せず、以下の要件でアドバイスしてください。
            
            【情報】
            - 求職者: {st.session_state.user_info}
            - 企業の魅力: {st.session_state.company_appeal}
            - メモ: {initial_memo}
            
            【出力構成】
            1. 徹底的な承認：メモや経験から素晴らしい強み（原石）を見つけて全力で褒めてください。
            2. やさしい質問（行動の深掘り）：その業務で一番大変だった時、どんな工夫をして乗り越えたか、短い言葉で教えてもらう質問を1つだけ投げかけてください。
            """
            with st.spinner("AIがあなたのメモを読んでいます..."):
                response = model.generate_content(prompt0)
                st.session_state.ai_message = response.text
                st.session_state.step = 1
                st.rerun()

# ==================================================
# 共通ワークスペース（ステップ1〜3）
# ==================================================
elif st.session_state.step in [1, 2, 3]:
    # 進捗バー
    progress_val = 0.25 if st.session_state.step == 1 else (0.6 if st.session_state.step == 2 else 0.9)
    st.progress(progress_val)
    
    # ステップタイトルの表示
    if st.session_state.step == 1:
        st.header(f"ステップ1：強みの発掘と具体化（対話 {st.session_state.action_count}/3）")
    elif st.session_state.step == 2:
        st.header("ステップ2：構成の「型」と表現のパーツ選び")
    else:
        st.header("ステップ3：最終研磨と仕上げ")

    # 画面を上下に分割：上部＝AIからのメッセージ
    st.markdown("<div class='ai-box'>", unsafe_allow_html=True)
    st.markdown(f"**🗣️ AIコンサルタントより：**\n\n{st.session_state.ai_message}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 軌道修正ボタン（ちゃぶ台返し）
    if st.button("🔄 ちょっとアドバイスが自分らしくない（別の視点で聞き直す）"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        reset_prompt = "求職者から「先ほどのアドバイスは自分らしくない」とフィードバックがありました。温かく受け止め、全く別の角度（素直な気持ちを聞くなど）から、やさしい質問を1つだけ投げかけてください。全文の代筆は厳禁です。"
        with st.spinner("別の視点を考えています..."):
            res = model.generate_content(reset_prompt)
            st.session_state.ai_message = res.text
            st.rerun()

    st.markdown("---")
    
    # 下部＝ユーザーのワークスペース（作業机）
    st.markdown("<div class='draft-box'>", unsafe_allow_html=True)
    st.subheader("📝 あなたの作業机（現在の志望動機）")
    st.write("AIのアドバイスを見ながら、下の文章を自由に書き換えたり、付け足したりしてください。")
    
    with st.form("workspace_form"):
        # 回答欄（ステップ1の対話中のみ表示）
        user_reply = ""
        if st.session_state.step == 1:
            user_reply = st.text_input("💡 AIの質問への回答（短い言葉でOKです）")
        
        # 常に保持される志望動機エディタ
        updated_draft = st.text_area("現在の文章", value=st.session_state.draft, height=200)
        
        # ボタンの出し分け
        if st.session_state.step == 1:
            if st.session_state.action_count < 3:
                btn_label = "回答と文章を更新して、さらに深掘りする 💬"
            else:
                btn_label = "ステップ2（構成とパーツ選び）へ進む 🚀"
        elif st.session_state.step == 2:
            btn_label = "ステップ3（最終チェック）へ進む 🚀"
        else:
            btn_label = "🎉 これで完成にする！（ダウンロード画面へ）"
            
        submit_work = st.form_submit_button(btn_label)

    # 処理ロジック
    if submit_work:
        st.session_state.draft = updated_draft # 常に最新の文章を保存
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if st.session_state.step == 1:
            st.session_state.action_count += 1
            if st.session_state.action_count == 2:
                # 2回目のAI（数字・具体性の引き出し）
                prompt1_2 = f"求職者の回答: {user_reply}\n現在の文章: {updated_draft}\n回答を褒めた上で、説得力を持たせるため「何年くらい？」「1日に何件くらい？」など、やさしく数字を引き出す質問を1つしてください。代筆厳禁。"
                with st.spinner("AIが考えています..."):
                    st.session_state.ai_message = model.generate_content(prompt1_2).text
            elif st.session_state.action_count == 3:
                # 3回目のAI（企業への貢献）
                prompt1_3 = f"求職者の回答: {user_reply}\n現在の文章: {updated_draft}\n企業の魅力({st.session_state.company_appeal})と結びつけ、「この強みを活かして入社後どう貢献したいか」を聞く質問を1つしてください。代筆厳禁。"
                with st.spinner("AIが考えています..."):
                    st.session_state.ai_message = model.generate_content(prompt1_3).text
            else:
                # ステップ2へ移行
                prompt2 = f"現在の文章: {updated_draft}\nこれまでのやり取りを褒め、「即戦力型」か「熱意型」の構成の型を提案してください。また、「未経験ですが」などの言葉を避けた、前向きな文章パーツ（空欄【 】付き）を3パターン提案し、自分で組み合わせてみるよう促してください。代筆厳禁。"
                with st.spinner("構成とパーツを準備しています..."):
                    st.session_state.ai_message = model.generate_content(prompt2).text
                    st.session_state.step = 2
            st.rerun()
            
        elif st.session_state.step == 2:
            # ステップ3へ移行
            prompt3 = f"現在の文章: {updated_draft}\n最終チェックです。「未経験ですが」などの不自然な言葉がないか確認し、250〜300字に収まるよう優しい言葉でアドバイスしてください。最後に、面接へ向けて強く背中を押してください。代筆厳禁。"
            with st.spinner("最終チェックを行っています..."):
                st.session_state.ai_message = model.generate_content(prompt3).text
                st.session_state.step = 3
            st.rerun()
            
        elif st.session_state.step == 3:
            # ゴールへ
            st.session_state.step = 4
            st.rerun()

# ==================================================
# ステップ4：完成・ダウンロード
# ==================================================
elif st.session_state.step == 4:
    st.balloons()
    st.header("🎉 おめでとうございます！あなただけの志望動機が完成しました！")
    st.success("AIが作ったのではなく、あなたが自分自身と向き合い、何度も考えて生み出した素晴らしい文章です。自信を持って伝えてきてください！")
    
    st.markdown("### 📜 完成した志望動機")
    st.info(st.session_state.draft)
    
    # ダウンロード用テキスト
    final_text = f"【完成した志望動機】\n\n{st.session_state.draft}"
    st.download_button(
        label="📝 完成した志望動機を保存（ダウンロード）する",
        data=final_text,
        file_name="my_motivation_letter.txt",
        mime="text/plain"
    )
    
    st.markdown("---")
    st.write("※もう一度初めから作成する場合は、ブラウザを更新してください。")
    st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
