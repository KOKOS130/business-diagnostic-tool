import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from datetime import datetime
import os

st.set_page_config(page_title="事業推進力診断ツール", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'scores' not in st.session_state:
    st.session_state.scores = {}

# 診断データ構造
diagnostic_data = {
    "経営ビジョンの明確さ": {
        "questions": [
            "将来のビジョン（3年後にどうなりたいか）を、社員や取引先に明確に説明できますか？",
            "自社の「強み」と「弱み」をそれぞれ3つ以上、すぐに答えることができますか？",
            "会社の経営方針や戦略を、文書やデータとして記録していますか？",
            "日々の経営判断をする際に、明確な判断基準や優先順位がありますか？",
            "幹部社員や管理職は、あなたの経営方針をしっかり理解していますか？",
            "重要な経営判断について、他の人に筋道立てて説明することができますか？"
        ]
    },
    "事業計画の実行管理": {
        "questions": [
            "今年度の事業計画書（売上目標、利益目標など）を作成していますか？",
            "事業計画の進捗状況を、定期的（週次または月次）にチェックしていますか？",
            "昨年立てた計画に対して、80%以上達成できましたか？",
            "計画と実績にズレが生じた時、その原因を分析していますか？",
            "計画が未達成の場合、修正や改善のアクションをすぐに実行していますか？",
            "全社員が、今年度の会社の目標数値（売上・利益など）を知っていますか？",
            "3ヶ月ごとに、目標達成のための具体的な行動計画がありますか？"
        ]
    },
    "組織体制の強さ": {
        "questions": [
            "あなたが1週間不在にしても、会社の業務は問題なく回りますか？",
            "事業運営を任せられる「右腕」となる人材がいますか？",
            "幹部社員や管理職に、適切に権限を委譲（任せる）ことができていますか？",
            "社員が、上司の指示を待たずに自分で判断して行動できていますか？",
            "業務のやり方が標準化され、マニュアルや手順書が整備されていますか？",
            "定例会議で、報告だけでなく、実質的な意思決定ができていますか？"
        ]
    },
    "経営者の時間の使い方": {
        "questions": [
            "1週間のうち、経営戦略を考える時間が20%以上（週8時間以上）ありますか？",
            "日々の業務に追われて、経営者としての本来の仕事に集中できていますか？",
            "現場の実務（営業・製造・事務作業など）に費やす時間は少ないですか？（週の20%未満）",
            "突発的なトラブル対応や問題解決に、時間を取られることは少ないですか？",
            "「やりたいけど時間がなくてできていないこと」は少ないですか？",
            "経営者がやるべき仕事と、他の人に任せるべき仕事を、明確に区別できていますか？"
        ]
    },
    "数値管理の仕組み": {
        "questions": [
            "重要な数値指標（売上、利益、顧客数など）を定め、週次で確認していますか？",
            "部門ごと、個人ごとに、明確な目標数値が設定されていますか？",
            "目標の達成状況を、グラフやダッシュボードなどで見える化していますか？",
            "目標未達成の時、必ず原因を分析して改善策を立てていますか？",
            "各社員が、自分の目標達成状況を常に把握できていますか？",
            "成果（業績）と報酬（給与・賞与）が、明確に連動する仕組みがありますか？"
        ]
    },
    "収益性の健全度": {
        "questions": [
            "過去3年間で、売上高は安定的に成長していますか？",
            "営業利益率（売上に対する利益の割合）は10%以上ありますか？",
            "主要な商品・サービスの粗利率（売上総利益率）を把握していますか？",
            "キャッシュフロー（現金の流れ）を毎月チェックし、資金繰りに問題はありませんか？",
            "不採算事業や赤字商品を定期的に見直し、改善または撤退の判断をしていますか？",
            "固定費（人件費・家賃など）は適正で、売上の変動に対応できる体質ですか？"
        ]
    }
}

# 選択肢（全軸共通）
options = {
    4: "非常に当てはまる",
    3: "やや当てはまる",
    2: "あまり当てはまらない",
    1: "全く当てはまらない"
}

def setup_japanese_font():
    """日本語フォントの設定 - Streamlit Cloud対応版"""
    # フォントキャッシュを再構築
    fm._load_fontmanager(try_read_cache=False)
    
    # 利用可能なフォントを確認
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # Noto Sans CJK JPを優先的に使用（packages.txtでインストール）
    japanese_fonts = [
        'Noto Sans CJK JP',
        'Noto Sans JP',
        'IPAGothic',
        'TakaoGothic',
        'DejaVu Sans'
    ]
    
    selected_font = None
    for font in japanese_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        plt.rcParams['font.sans-serif'] = [selected_font]
    else:
        # フォールバック: システムで利用可能な日本語フォントを検索
        cjk_fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'Gothic' in f.name or 'Noto' in f.name]
        if cjk_fonts:
            plt.rcParams['font.sans-serif'] = [cjk_fonts[0]]
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    plt.rcParams['axes.unicode_minus'] = False

def show_intro():
    """イントロページ"""
    st.markdown('<div class="main-header">📊 事業推進力診断ツール</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">所要時間: 約15分 | 全36問 | その場で結果がわかります</div>', unsafe_allow_html=True)
    
    st.write("## 🎯 この診断について")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        ### 📋 診断内容
        事業推進力を**6つの軸**で診断します
        
        **所要時間**: 約15分  
        **設問数**: 全36問  
        **結果**: その場で確認可能
        """)
        
        st.write("""
        ### 📊 わかること
        - 総合スコアとランク評価
        - 6軸のバランス（レーダーチャート）
        - 具体的な改善ポイント
        - 優先的に取り組むべき課題
        """)
    
    with col2:
        st.write("""
        ### 🔍 6つの診断軸
        1. **経営ビジョンの明確さ** (6問)
        2. **事業計画の実行管理** (7問)
        3. **組織体制の強さ** (6問)
        4. **経営者の時間の使い方** (6問)
        5. **数値管理の仕組み** (6問)
        6. **収益性の健全度** (6問)
        """)
        
        st.write("""
        ### ✅ 回答方法
        各設問に対して、現状を最も表している選択肢を選んでください
        
        - **非常に当てはまる**
        - **やや当てはまる**
        - **あまり当てはまらない**
        - **全く当てはまらない**
        """)
    
    st.write("---")
    st.info("""
    💡 **診断のポイント**
    - 直感で正直に回答してください
    - 理想ではなく、**現状**を評価してください
    - 全ての設問に回答してください
    """)
    
    if st.button("📝 診断を開始する", type="primary", use_container_width=True):
        st.session_state.page = 'questions'
        st.rerun()

def show_questions():
    """質問ページ"""
    st.markdown('<div class="main-header">📊 事業推進力診断ツール</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">所要時間: 約15分 | 全36問 | その場で結果がわかります</div>', unsafe_allow_html=True)
    
    st.write("## 📝 診断設問")
    
    # プログレスバー
    total_questions = sum(len(data["questions"]) for data in diagnostic_data.values())
    answered = len(st.session_state.scores)
    progress = answered / total_questions if total_questions > 0 else 0
    st.progress(progress)
    st.write(f"**進捗: {answered}/{total_questions} 問回答済み** ({int(progress*100)}%)")
    
    st.write("---")
    
    # 各軸の質問を表示
    for axis_idx, (axis_name, axis_data) in enumerate(diagnostic_data.items(), 1):
        st.write(f"### 📊 軸{axis_idx}: {axis_name}")
        
        for q_idx, question in enumerate(axis_data['questions'], 1):
            key = f"{axis_name}_{q_idx}"
            
            st.write(f"**問{q_idx}. {question}**")
            
            # ラジオボタンのデフォルト値を設定
            if key in st.session_state.scores:
                # 既に回答がある場合
                default_value = st.session_state.scores[key]
            else:
                # 初回はNoneではなく、最初の選択肢をデフォルトに
                default_value = 4
            
            score = st.radio(
                f"回答を選択してください",
                options=[4, 3, 2, 1],
                format_func=lambda x: options[x],
                horizontal=True,
                key=f"q_{axis_idx}_{q_idx}",
                index=[4, 3, 2, 1].index(default_value),
                label_visibility="collapsed"
            )
            
            # スコアを保存
            st.session_state.scores[key] = score
            
            st.write("")
        
        st.write("---")
    
    # 診断結果を見るボタン
    st.success("✅ 全ての設問に回答しました！")
    if st.button("📊 診断結果を見る", type="primary", use_container_width=True):
        st.session_state.page = 'results'
        st.rerun()

def calculate_scores():
    """スコア計算"""
    axis_scores = {}
    axis_max_scores = {}
    
    for axis_name, axis_data in diagnostic_data.items():
        total = 0
        max_score = len(axis_data['questions']) * 4
        
        for q_idx in range(1, len(axis_data['questions']) + 1):
            key = f"{axis_name}_{q_idx}"
            total += st.session_state.scores.get(key, 0)
        
        axis_scores[axis_name] = total
        axis_max_scores[axis_name] = max_score
    
    total_score = sum(axis_scores.values())
    max_total_score = sum(axis_max_scores.values())
    percentage = (total_score / max_total_score) * 100 if max_total_score > 0 else 0
    
    return axis_scores, axis_max_scores, total_score, max_total_score, percentage

def get_rank(percentage):
    """ランク判定"""
    if percentage >= 85:
        return "A", "優良レベル", "🌟", "#28a745"
    elif percentage >= 70:
        return "B", "標準レベル", "✅", "#17a2b8"
    elif percentage >= 55:
        return "C", "要改善レベル", "⚠️", "#ffc107"
    else:
        return "D", "危機レベル", "🚨", "#dc3545"

def show_results():
    """結果ページ - ページトップから表示"""
    # ヘッダーを最上部に配置（これが最初に表示される）
    st.markdown('<div class="main-header">📊 事業推進力診断ツール</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">所要時間: 約15分 | 全36問 | その場で結果がわかります</div>', unsafe_allow_html=True)
    
    st.write("## 📊 診断結果")
    
    axis_scores, axis_max_scores, total_score, max_total_score, percentage = calculate_scores()
    rank, rank_label, rank_icon, rank_color = get_rank(percentage)
    
    # 総合スコア表示
    st.write("### 🎯 総合評価")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background-color: {rank_color}; color: white; border-radius: 1rem;'>
            <div style='font-size: 3rem;'>{rank_icon}</div>
            <div style='font-size: 2rem; font-weight: bold;'>ランク {rank}</div>
            <div style='font-size: 1.2rem;'>{rank_label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("総合スコア", f"{total_score} / {max_total_score} 点")
        st.metric("達成率", f"{percentage:.1f}%")
    
    with col3:
        st.write("#### 📋 ランク基準")
        st.write("""
        - **A**: 85%以上（優良）
        - **B**: 70-84%（標準）
        - **C**: 55-69%（要改善）
        - **D**: 55%未満（危機）
        """)
    
    st.write("---")
    
    # レーダーチャートと詳細スコア
    st.write("### 📈 6軸バランス分析")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # 日本語フォント設定
        setup_japanese_font()
        
        # レーダーチャート
        labels = list(axis_scores.keys())
        scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        scores_plot = scores + scores[:1]
        angles_plot = angles + angles[:1]
        
        # チャートサイズを縮小
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angles_plot, scores_plot, 'o-', linewidth=2.5, color='#1f77b4', markersize=8)
        ax.fill(angles_plot, scores_plot, alpha=0.25, color='#1f77b4')
        
        # ラベルを短縮
        short_labels = [
            "ビジョンの\n明確さ",
            "計画の\n実行管理",
            "組織体制の\n強さ",
            "時間の\n使い方",
            "数値管理の\n仕組み",
            "収益性の\n健全度"
        ]
        
        ax.set_thetagrids(np.degrees(angles), short_labels, fontsize=9)
        ax.set_ylim(0, 4)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['1', '2', '3', '4'], fontsize=8)
        ax.grid(True, linewidth=0.8, alpha=0.6)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.write("#### 📊 各軸スコア")
        for idx, (axis_name, score) in enumerate(axis_scores.items(), 1):
            max_score = axis_max_scores[axis_name]
            pct = (score / max_score) * 100 if max_score > 0 else 0
            
            if pct >= 75:
                color = "🟢"
            elif pct >= 50:
                color = "🟡"
            else:
                color = "🔴"
            
            st.write(f"{color} **{axis_name}**")
            st.write(f"　{score} / {max_score} 点 ({pct:.1f}%)")
            st.progress(pct / 100)
            st.write("")
    
    st.write("---")
    
    # 優先改善課題
    st.write("### 🎯 優先改善課題 TOP3")
    
    sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1] / axis_max_scores[x[0]] if axis_max_scores[x[0]] > 0 else 0)
    
    medals = ["🥇", "🥈", "🥉"]
    priorities = ["最優先課題", "第2優先", "第3優先"]
    
    for idx, (axis_name, score) in enumerate(sorted_axes[:3]):
        pct = (score / axis_max_scores[axis_name]) * 100 if axis_max_scores[axis_name] > 0 else 0
        
        with st.expander(f"{medals[idx]} {priorities[idx]}: {axis_name} ({pct:.1f}%)", expanded=(idx==0)):
            st.write(f"**現状スコア**: {score} / {axis_max_scores[axis_name]} 点")
            
            if axis_name == "経営ビジョンの明確さ":
                st.write("""
                **改善ポイント**:
                - ✅ 3年後のビジョンを文書化する
                - ✅ 自社の強み・弱みを分析し、明文化する
                - ✅ 経営方針を幹部と共有する定例会議を設定
                
                **具体的アクション**:
                1. 今週中に「経営ビジョンシート」を作成
                2. 月1回の幹部会議で経営方針を議論
                3. 戦略マップの作成
                """)
            
            elif axis_name == "事業計画の実行管理":
                st.write("""
                **改善ポイント**:
                - ✅ 年次事業計画書を作成する
                - ✅ 月次の進捗確認会議を設定
                - ✅ KPI管理表を導入
                
                **具体的アクション**:
                1. 今期の事業計画書を作成（簡易版でもOK）
                2. 月次進捗レビュー会議の設定
                3. 主要KPIの可視化（Excel/スプレッドシート）
                """)
            
            elif axis_name == "組織体制の強さ":
                st.write("""
                **改善ポイント**:
                - ✅ 右腕人材の育成計画を立てる
                - ✅ 権限委譲のルールを明確化
                - ✅ 業務マニュアルの整備
                
                **具体的アクション**:
                1. 次期幹部候補の選定と育成計画
                2. 決裁権限表の作成
                3. 主要業務のマニュアル化（1業務/週）
                """)
            
            elif axis_name == "経営者の時間の使い方":
                st.write("""
                **改善ポイント**:
                - ✅ 経営者の役割を再定義する
                - ✅ ルーティン業務を委譲する
                - ✅ 戦略思考の時間を確保する
                
                **具体的アクション**:
                1. 1週間の時間使途を記録・分析
                2. 委譲可能な業務をリストアップ
                3. 毎週金曜午後を「戦略思考タイム」に設定
                """)
            
            elif axis_name == "数値管理の仕組み":
                st.write("""
                **改善ポイント**:
                - ✅ 重要KPIを定義する
                - ✅ 目標管理の仕組みを導入
                - ✅ 進捗の可視化ツールを整備
                
                **具体的アクション**:
                1. 重要KPI 5つを選定
                2. 部門別・個人別の目標設定
                3. 週次KPIダッシュボードの作成
                """)
            
            else:  # 収益性の健全度
                st.write("""
                **改善ポイント**:
                - ✅ 売上・利益の推移を分析する
                - ✅ 粗利率の改善策を検討する
                - ✅ キャッシュフロー管理を徹底する
                
                **具体的アクション**:
                1. 過去3年間の売上・利益推移をグラフ化
                2. 商品別・サービス別の粗利率を算出
                3. 月次資金繰り表の作成と毎月の確認
                """)
    
    st.write("---")
    
    # ランク別のメッセージ
    st.write("### 💡 総合診断")
    
    if rank == "A":
        st.success(f"""
        {rank_icon} **おめでとうございます！優良レベルです**
        
        ✅ 経営の仕組みが確立されています  
        ✅ 事業推進力は高い状態です  
        
        **さらなる成長のために**:
        - より高度な経営戦略の立案
        - 新規事業展開の検討
        - 組織のさらなる進化
        """)
    
    elif rank == "B":
        st.info(f"""
        {rank_icon} **標準レベルです**
        
        基本的な仕組みはありますが、改善の余地があります。  
        特に弱い領域を強化することで、飛躍的な成長が期待できます。
        
        **次のステップ**:
        - 優先改善課題TOP3に着手
        - 3ヶ月後の再診断で進捗確認
        - 必要に応じて専門家への相談を検討
        """)
    
    elif rank == "C":
        st.warning(f"""
        {rank_icon} **要改善レベルです**
        
        事業推進に課題が多い状態です。  
        経営者の負担が過大になっている可能性があります。
        
        **早急な対応が必要**:
        - 優先課題への速やかな対応
        - 体制整備の実施
        - 専門家のサポート活用を推奨
        """)
    
    else:
        st.error(f"""
        {rank_icon} **危機レベルです**
        
        事業推進の仕組みが十分に機能していません。  
        このままでは成長の限界に直面する可能性があります。
        
        **緊急対応が必要**:
        - 早急な体制再構築
        - まずは最優先課題1つに集中
        - 専門家への相談を強く推奨
        """)
    
    st.write("---")
    
    # アクションボタン
    if st.button("🔄 診断をやり直す", use_container_width=True):
        st.session_state.scores = {}
        st.session_state.page = 'intro'
        st.rerun()
    
    # フッター
    st.write("---")
    st.caption(f"診断日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")

# ページルーティング
if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'questions':
    show_questions()
elif st.session_state.page == 'results':
    show_results()
