import streamlit as st
import google.generativeai as genai
import json

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

/* 5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; }
    
    div[data-testid="stForm"] { padding: 15px !important; }
    .ai-box, .draft-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
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
    background-color: #C27082 !important;
    transform: translateY(-2px);
}
[data-testid="stLinkButton"] a * {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown("""
<div class="header-box">
    <div class="header-title">🌱 ゼロから育てる！志望動機作成アシスタント</div>
    <div class="header-subtitle">
        AIと一緒に、あなたの中に眠っている強みを引き出し、あなただけの志望動機を少しずつ育てていきましょう！
    </div>
</div>
""", unsafe_allow_html=True)

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
if 'proposed_issues' not in st.session_state:
    st.session_state.proposed_issues = []
if 'company_issue' not in st.session_state:
    st.session_state.company_issue = ""
if 'amulet' not in st.session_state:
    st.session_state.amulet = ""

# ==================================================
# ステップ0：企業情報の入力と課題予測（新規追加フェーズ）
# ==================================================
if st.session_state.step == 0:
    st.header("ステップ0：まずは応募先の「課題」を探りましょう")
    st.write("求人票や企業のホームページの文章を、そのままコピー＆ペーストしてください。AIが企業の裏側にある課題を予測します。")
    
    with st.form("company_info_form"):
        job_text = st.text_area("📄 企業の求人票やHPの情報（メニューバーの文字などが入ってぐちゃぐちゃでも構いません）", height=200)
        
        st.write("企業の現在の状況について、直感で教えてください。")
        growth_stage = st.radio(
            "🏢 この会社は今、どの「成長ステージ」にいると感じますか？",
            options=[
                "立ち上げ・急成長期（歴史は浅いが勢いがある。ルールや仕組みがまだ整っていなそう）",
                "安定・成熟期（歴史があり基盤はしっかりしているが、組織の高齢化や業務のマンネリ化がありそう）",
                "変革・第二創業期（老舗だが、新しい事業を始めたり、IT化など社内を大きく変えようとしていそう）",
                "よくわからない（AIにお任せする）"
            ]
        )
        
        submit_company = st.form_submit_button("AIに企業の「現場の課題」を分析させる 🔍")
        
        if submit_company:
            if not api_key:
                st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
            elif not job_text:
                st.warning("⚠️ 企業情報を入力してください。")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 課題を3つ出させるプロンプト（JSON配列形式で要求）
                issue_prompt = f"""
                以下の企業情報と成長ステージから、この企業が現場レベルで抱えているであろう「課題」を3つ予測してください。
                出力は必ず以下の3つの視点から1つずつ抽出し、JSONの配列（文字列のリスト）のみを出力してください。
                
                【視点】
                1. 現場の泥臭い実務に関する課題（例：アナログ作業、属人化など）
                2. 組織・人材に関する課題（例：若手育成、世代交代など）
                3. 顧客・サービスに関する課題（例：新規開拓、顧客満足度など）
                
                【企業情報】
                {job_text}
                
                【成長ステージ】
                {growth_stage}
                
                出力例: ["現場のアナログ作業が多く、業務の属人化が発生していそう", "若手育成のノウハウが不足しており、技術継承が遅れていそう", "既存顧客へのルート営業に留まり、新規開拓の力が不足していそう"]
                """
                
                with st.spinner("企業情報を分析し、現場の課題を予測しています..."):
                    try:
                        res = model.generate_content(issue_prompt)
                        # Markdownのコードブロック記号を削除してJSONとしてパース
                        clean_text = res.text.strip().replace("```json", "").replace("```", "").strip()
                        issues = json.loads(clean_text)
                        if isinstance(issues, list) and len(issues) >= 3:
                            st.session_state.proposed_issues = issues[:3]
                        else:
                            # 万が一パースに失敗した場合のフォールバック
                            st.session_state.proposed_issues = ["業務の効率化やマニュアル整備の不足", "人材育成やサポート体制の課題", "新しい取り組みやIT化の遅れ"]
                    except Exception as e:
                        st.session_state.proposed_issues = ["業務の効率化やマニュアル整備の不足", "人材育成やサポート体制の課題", "新しい取り組みやIT化の遅れ"]
                    
                    st.session_state.step = 1
                    st.rerun()

# ==================================================
# ステップ1：自身の情報入力と課題への紐付け
# ==================================================
elif st.session_state.step == 1:
    st.header("ステップ1：あなたの経験と企業の課題を結びつける")
    st.write("AIが予測した企業の課題から、あなたが「力になれそう」と思うものを選んでください。")
    
    with st.form("input_form"):
        # 課題の選択
        st.subheader("🎯 アプローチする課題の選択")
        options = st.session_state.proposed_issues + ["その他（自分で入力する）"]
        selected_issue = st.radio("どの課題なら、あなたの経験で手助けできそうですか？", options=options)
        
        custom_issue = ""
        if selected_issue == "その他（自分で入力する）":
            st.caption("HPや求人を見て、「この会社、こんなことで困っているんじゃないか？」と直感したことを短い言葉で教えてください。")
            custom_issue = st.text_input("ご自身で感じた課題（例：エクセルでの手作業が多くて現場の残業が多そう）")
        
        st.markdown("---")
        st.subheader("👤 あなたのご経歴について")
        col1, col2 = st.columns(2)
        with col1:
            age = st.text_input("年齢（例：40代）")
            gender = st.selectbox("性別", ["回答しない", "男性", "女性", "その他"])
            history = st.text_area("簡単な職歴（例：事務職5年、販売職3年など）")
        
        with col2:
            passion = st.text_area("仕事で「こだわったこと」「評価されたこと」「時間を忘れて夢中になったこと」")
            strengths = st.text_input("あなたの「強み」や「大切にしている価値観」")
            
        st.subheader("📝 今の志望動機のメモ（最初のタネ）")
        st.caption("選んだ課題に対して、あなたの経験をどう活かして手伝えそうか、一言で教えてください。")
        initial_memo = st.text_area("上手く書けていなくてもOKです。今の段階で書けることを入力してください。", height=100)
        
        submit_1 = st.form_submit_button("AIと一緒に志望動機を育て始める ✨")
        
        if submit_1:
            if not api_key:
                st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
            elif not initial_memo or not passion:
                st.warning("⚠️ 必須項目（こだわったこと、志望動機のメモ）を入力してください。")
            elif selected_issue == "その他（自分で入力する）" and not custom_issue:
                st.warning("⚠️ ご自身で感じた課題を入力してください。")
            else:
                final_issue = custom_issue if selected_issue == "その他（自分で入力する）" else selected_issue
                st.session_state.company_issue = final_issue
                
                # データを保存
                st.session_state.user_info = f"年齢:{age}, 性別:{gender}, 職歴:{history}, 夢中になったこと:{passion}, 強み:{strengths}"
                st.session_state.draft = initial_memo
                
                # 初回のAIメッセージ生成（厳格なバイアス排除指示を追加）
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt1 = f"""
                あなたは初学者に寄り添い、未来志向でキャリアを支援する温かいキャリアコンサルタントです。
                以下の情報を読み、絶対に全文を代筆せず、以下の要件でアドバイスしてください。
                
                【情報】
                - 求職者: {st.session_state.user_info}
                - 企業が抱える課題（求職者が解決したいこと）: {final_issue}
                - メモ: {initial_memo}
                
                【AIへの厳格な出力ルール：属性情報の扱いについて】
                対象者の「年齢」「性別」は、これまでのキャリアの長さやライフステージの背景を理解するためのコンテキストとしてのみ使用してください。
                出力するメッセージや志望動機の提案において、「女性ならではの」「〇代だから」といった性別・年齢に基づく一般化やアンコンシャス・バイアス（無意識の偏見）を助長する表現は**絶対に**使用しないでください。
                常に、属性ではなく「その人個人の具体的な経験・事実・強み」に焦点を当てて対話を行ってください。
                
                【出力構成】
                1. 徹底的な承認：メモや経験から素晴らしい強み（原石）を見つけ、企業の課題解決に繋がる点を全力で褒めてください。
                2. やさしい質問（行動の深掘り）：その業務で一番大変だった時、どんな工夫をして乗り越えたか、短い言葉で教えてもらう質問を1つだけ投げかけてください。
                """
                with st.spinner("AIがあなたのメモを読んでいます..."):
                    response = model.generate_content(prompt1)
                    st.session_state.ai_message = response.text
                    st.session_state.step = 2
                    st.rerun()

# ==================================================
# 共通ワークスペース（ステップ2〜4）
# ==================================================
elif st.session_state.step in [2, 3, 4]:
    # 進捗バー
    progress_val = 0.4 if st.session_state.step == 2 else (0.7 if st.session_state.step == 3 else 0.9)
    st.progress(progress_val)
    
    # ステップタイトルの表示
    if st.session_state.step == 2:
        st.header(f"ステップ2：強みの発掘と具体化（対話 {st.session_state.action_count}/3）")
    elif st.session_state.step == 3:
        st.header("ステップ3：構成の「型」と表現のパーツ選び")
    else:
        st.header("ステップ4：最終研磨と仕上げ")

    # 画面を上下に分割：上部＝AIからのメッセージ
    st.markdown("<div class='ai-box'>", unsafe_allow_html=True)
    st.markdown(f"**🗣️ AIコンサルタントより：**\n\n{st.session_state.ai_message}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 軌道修正ボタン（ちゃぶ台返し）
    if st.button("🔄 ちょっとアドバイスが自分らしくない（別の視点で聞き直す）"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        reset_prompt = "求職者から「先ほどのアドバイスは自分らしくない」とフィードバックがありました。温かく受け止め、全く別の角度から、やさしい質問を1つだけ投げかけてください。年齢・性別のバイアス表現は厳禁。全文の代筆も厳禁。"
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
        # 回答欄（ステップ2の対話中のみ表示）
        user_reply = ""
        if st.session_state.step == 2:
            user_reply = st.text_input("💡 AIの質問への回答（短い言葉でOKです）")
        
        # 常に保持される志望動機エディタ
        updated_draft = st.text_area("現在の文章", value=st.session_state.draft, height=200)
        
        # ボタンの出し分け
        if st.session_state.step == 2:
            if st.session_state.action_count < 3:
                btn_label = "回答と文章を更新して、さらに深掘りする 💬"
            else:
                btn_label = "ステップ3（構成とパーツ選び）へ進む 🚀"
        elif st.session_state.step == 3:
            btn_label = "ステップ4（最終チェック）へ進む 🚀"
        else:
            btn_label = "🎉 これで完成にする！（面接対策へ進む）"
            
        submit_work = st.form_submit_button(btn_label)

    st.markdown("</div>", unsafe_allow_html=True)

    # 処理ロジック
    if submit_work:
        st.session_state.draft = updated_draft # 常に最新の文章を保存
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if st.session_state.step == 2:
            st.session_state.action_count += 1
            if st.session_state.action_count == 2:
                # 2回目のAI（数字・具体性の引き出し）
                prompt2_2 = f"求職者の回答: {user_reply}\n現在の文章: {updated_draft}\n回答を褒めた上で、説得力を持たせるため「何年くらい？」「1日に何件くらい？」など、やさしく数字を引き出す質問を1つしてください。代筆厳禁。"
                with st.spinner("AIが考えています..."):
                    st.session_state.ai_message = model.generate_content(prompt2_2).text
            elif st.session_state.action_count == 3:
                # 3回目のAI（企業への貢献）
                prompt2_3 = f"求職者の回答: {user_reply}\n現在の文章: {updated_draft}\n企業の課題({st.session_state.company_issue})と結びつけ、「この強みを活かして入社後どう課題解決に貢献したいか」を聞く質問を1つしてください。代筆厳禁。"
                with st.spinner("AIが考えています..."):
                    st.session_state.ai_message = model.generate_content(prompt2_3).text
            else:
                # ステップ3へ移行
                prompt3 = f"現在の文章: {updated_draft}\nこれまでのやり取りを褒め、「課題解決型」か「現場サポート型」の構成の型を提案してください。また、「未経験ですが」などの言葉を避けた、未来志向の文章パーツ（空欄【 】付き）を3パターン提案し、自分で組み合わせてみるよう促してください。代筆厳禁。"
                with st.spinner("構成とパーツを準備しています..."):
                    st.session_state.ai_message = model.generate_content(prompt3).text
                    st.session_state.step = 3
            st.rerun()
            
        elif st.session_state.step == 3:
            # ステップ4へ移行
            prompt4 = f"現在の文章: {updated_draft}\n最終チェックです。「未経験ですが」などの不自然な言葉がないか確認し、250〜300字に収まるよう優しい言葉でアドバイスしてください。最後に、面接へ向けて強く背中を押してください。代筆厳禁。"
            with st.spinner("最終チェックを行っています..."):
                st.session_state.ai_message = model.generate_content(prompt4).text
                st.session_state.step = 4
            st.rerun()
            
        elif st.session_state.step == 4:
            # 完成・お守りの生成（ステップ5へ）
            amulet_prompt = f"""
            以下の完成した志望動機を読み、上場企業の人事・面接官の視点から、面接で必ず聞かれるであろう「鋭いツッコミ（想定質問）」を1つ作成してください。
            さらに、その質問に対して、求職者が緊張せず自分の言葉で答えられるような「回答のヒント（お守り）」を温かい口調で作成してください。
            
            【志望動機】
            {st.session_state.draft}
            
            【出力構成】
            ### ⚠️ 面接官はここを聞いてきます（想定質問）
            （質問文）
            
            ### 💡 こう答えれば大丈夫です（あなたへのお守り）
            （回答のヒントと励まし）
            """
            with st.spinner("面接に向けた「お守り」を作成しています..."):
                st.session_state.amulet = model.generate_content(amulet_prompt).text
                st.session_state.step = 5
            st.rerun()

# ==================================================
# ステップ5：完成・ダウンロード・お守り表示
# ==================================================
elif st.session_state.step == 5:
    st.balloons()
    st.header("🎉 おめでとうございます！あなただけの志望動機が完成しました！")
    st.success("AIが考えたものではなく、あなたがご自身の経験から企業の課題を見抜き、ご自身の天職（Calling）と結びつけて生み出した素晴らしい文章です。自信を持って面接で伝えてきてください！")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("### 📜 完成した志望動機")
        st.info(st.session_state.draft)
        
    with col_b:
        st.markdown("### 🎁 面接へ持っていく「お守り」")
        st.warning(st.session_state.amulet)
    
    # ダウンロード用テキスト（志望動機＋お守り）
    final_text = f"【完成した志望動機】\n\n{st.session_state.draft}\n\n=========================\n\n【面接想定問答（お守り）】\n\n{st.session_state.amulet}"
    
    # ダウンロードボタン
    st.markdown("---")
    st.download_button(label="📝 志望動機と面接対策（お守り）を保存する", data=final_text, file_name="my_motivation_and_amulet.txt", mime="text/plain")
    
    st.markdown("---")
    st.write("※もう一度初めから作成する場合は、ブラウザを更新してください。")

st.markdown("---")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
