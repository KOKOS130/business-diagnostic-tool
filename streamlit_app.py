import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from datetime import datetime
import json
import base64
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(page_title="ADAMS 事業推進力診断ツール", layout="wide", initial_sidebar_state="collapsed")

# ADAMSブランドカラー（ネイビー）
ADAMS_NAVY = "#243666"
ADAMS_LIGHT_NAVY = "#3d5a8f"

# カスタムCSS - ADAMSブランディング
st.markdown(f"""
<style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {ADAMS_NAVY};
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    .sub-header {{
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 1rem;
    }}
    .adams-footer {{
        text-align: center;
        color: {ADAMS_NAVY};
        font-size: 0.9rem;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 2px solid {ADAMS_NAVY};
    }}
    .copyright-notice {{
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 1rem;
        padding: 0.5rem;
    }}
    .stButton>button {{
        background-color: {ADAMS_NAVY};
        color: white;
    }}
    .stButton>button:hover {{
        background-color: {ADAMS_LIGHT_NAVY};
        color: white;
    }}
    @media print {{
        .no-print {{
            display: none !important;
        }}
        .print-only {{
            display: block !important;
        }}
    }}
    .print-only {{
        display: none;
    }}
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'scores' not in st.session_state:
    st.session_state.scores = {}

# 診断データ構造（英語ラベル追加）
diagnostic_data = {
    "経営ビジョンの明確さ": {
        "english_label": "Vision",
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
        "english_label": "Planning",
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
        "english_label": "Organization",
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
        "english_label": "Time Mgmt",
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
        "english_label": "KPI",
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
        "english_label": "Profitability",
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

def save_to_google_sheets(result_data):
    """Googleスプレッドシートに結果を保存（将来実装）"""
    try:
        if 'saved_results' not in st.session_state:
            st.session_state.saved_results = []
        
        st.session_state.saved_results.append(result_data)
        return True
    except Exception as e:
        st.error(f"データ保存エラー: {str(e)}")
        return False

def create_radar_chart(axis_scores, axis_max_scores, labels):
    """レーダーチャート作成（PDF用）"""
    scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles_plot = angles + angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles_plot, scores_plot, 'o-', linewidth=2.5, color=ADAMS_NAVY, markersize=8)
    ax.fill(angles_plot, scores_plot, alpha=0.25, color=ADAMS_NAVY)
    
    # 英語ラベルを使用（文字化け対策）
    english_labels = [diagnostic_data[label]["english_label"] for label in labels]
    
    ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=12)
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['1', '2', '3', '4'], fontsize=10)
    ax.grid(True, linewidth=0.8, alpha=0.6)
    
    return fig

def generate_pdf_report(axis_scores, axis_max_scores, total_score, max_total_score, percentage, rank, rank_label):
    """PDF診断レポート生成"""
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    buffer = BytesIO()
    
    # フォント設定を試みる（失敗しても続行）
    try:
        import matplotlib.font_manager as fm
        font_files = fm.findSystemFonts()
        noto_fonts = [f for f in font_files if 'Noto' in f and 'CJK' in f and 'JP' in f]
        if noto_fonts:
            pdfmetrics.registerFont(TTFont('NotoSans', noto_fonts[0]))
            font_name = 'NotoSans'
        else:
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'
    
    # PDFドキュメント作成
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # カスタムスタイル
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor(ADAMS_NAVY),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor(ADAMS_NAVY),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        spaceAfter=12
    )
    
    # タイトル
    story.append(Paragraph('Business Promotion Diagnostic Report', title_style))
    story.append(Paragraph('Jigyou Suishin-ryoku Shindan Report', title_style))
    story.append(Paragraph(f'Date: {datetime.now().strftime("%Y/%m/%d %H:%M")}', normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 総合評価
    story.append(Paragraph(f'Overall Evaluation: Rank {rank} ({rank_label})', heading_style))
    story.append(Paragraph(f'Total Score: {total_score} / {max_total_score} points ({percentage:.1f}%)', normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # レーダーチャートを画像として挿入
    labels = list(axis_scores.keys())
    radar_fig = create_radar_chart(axis_scores, axis_max_scores, labels)
    
    img_buffer = BytesIO()
    radar_fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close(radar_fig)
    
    story.append(Image(img_buffer, width=4*inch, height=4*inch))
    story.append(Spacer(1, 0.2*inch))
    
    # 凡例
    story.append(Paragraph('Legend / Hanrei:', heading_style))
    legend_data = [
        ['Vision', 'Keiei Vision no Meikaku-sa'],
        ['Planning', 'Jigyo Keikaku no Jikko Kanri'],
        ['Organization', 'Soshiki Taisei no Tsuyosa'],
        ['Time Mgmt', 'Keieisha no Jikan no Tsukaikata'],
        ['KPI', 'Suuchi Kanri no Shikumi'],
        ['Profitability', 'Shueki-sei no Kenzendo']
    ]
    legend_table = Table(legend_data, colWidths=[1.5*inch, 3.5*inch])
    legend_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(ADAMS_NAVY)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 各軸スコア
    story.append(Paragraph('Detailed Scores by Axis:', heading_style))
    score_data = [['Axis', 'Score', 'Percentage']]
    for axis_name, score in axis_scores.items():
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        english_label = diagnostic_data[axis_name]['english_label']
        score_data.append([english_label, f'{score}/{max_score}', f'{pct:.1f}%'])
    
    score_table = Table(score_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    score_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ADAMS_NAVY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*inch))
    
    # フッター
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph('(C) 2024 ADAMS Management Consulting Office. All Rights Reserved.', footer_style))
    story.append(Paragraph('Unauthorized reproduction or copying of this diagnostic tool is prohibited.', footer_style))
    
    # PDF生成
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_intro():
    """イントロページ"""
    # ADAMSロゴを左上に配置
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=120)
    except:
        # ロゴが読み込めない場合はテキストで表示
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 0.9rem; margin-bottom: 1rem;">
            ㈱ADAMS Management Consulting Office
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">事業推進力診断ツール</div>', unsafe_allow_html=True)
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
    
    # ADAMSフッター
    st.markdown(f"""
    <div class="adams-footer">
        <strong>㈱ADAMS Management Consulting Office</strong><br>
        本診断ツールは㈱ADAMSが提供するクライアント様向けサービスです
    </div>
    <div class="copyright-notice">
        © 2024 ADAMS Management Consulting Office. All Rights Reserved.<br>
        本診断ツールの無断転用・複製を禁じます
    </div>
    """, unsafe_allow_html=True)

def show_questions():
    """質問ページ"""
    # ADAMSロゴを左上に配置（小サイズ）
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem;">
            ㈱ADAMS 事業推進力診断ツール
        </div>
        """, unsafe_allow_html=True)
    
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
            
            if key in st.session_state.scores:
                default_value = st.session_state.scores[key]
            else:
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
            
            st.session_state.scores[key] = score
            st.write("")
        
        st.write("---")
    
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
    """結果ページ"""
    # ADAMSロゴを左上に配置（小サイズ）
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem;">
            ㈱ADAMS 事業推進力診断ツール
        </div>
        """, unsafe_allow_html=True)
    
    st.write("## 📊 診断結果")
    
    axis_scores, axis_max_scores, total_score, max_total_score, percentage = calculate_scores()
    rank, rank_label, rank_icon, rank_color = get_rank(percentage)
    
    # 結果データの準備（スプレッドシート保存用）
    result_data = {
        "診断日時": datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
        "総合スコア": total_score,
        "最大スコア": max_total_score,
        "達成率": f"{percentage:.1f}%",
        "ランク": rank,
        **{f"{axis_name}スコア": score for axis_name, score in axis_scores.items()}
    }
    
    # 結果を保存
    save_to_google_sheets(result_data)
    
    # 印刷・PDF出力ボタン（no-printクラスで印刷時非表示）
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # ブラウザ印刷ボタン
        st.markdown("""
        <script>
        function printPage() {
            window.print();
        }
        </script>
        """, unsafe_allow_html=True)
        
        if st.button("🖨️ 印刷する", use_container_width=True, key="print_btn"):
            st.markdown("""
            <script>
            window.print();
            </script>
            """, unsafe_allow_html=True)
    
    with col_btn2:
        # PDFダウンロードボタン
        pdf_buffer = generate_pdf_report(axis_scores, axis_max_scores, total_score, 
                                         max_total_score, percentage, rank, rank_label)
        
        st.download_button(
            label="📄 PDFダウンロード",
            data=pdf_buffer,
            file_name=f"診断結果_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    
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
        # レーダーチャート（英語ラベル使用）
        labels = list(axis_scores.keys())
        scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        scores_plot = scores + scores[:1]
        angles_plot = angles + angles[:1]
        
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angles_plot, scores_plot, 'o-', linewidth=2.5, color=ADAMS_NAVY, markersize=8)
        ax.fill(angles_plot, scores_plot, alpha=0.25, color=ADAMS_NAVY)
        
        # 英語ラベルを使用（文字化け対策）
        english_labels = [diagnostic_data[label]["english_label"] for label in labels]
        
        ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=10)
        ax.set_ylim(0, 4)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['1', '2', '3', '4'], fontsize=8)
        ax.grid(True, linewidth=0.8, alpha=0.6)
        
        st.pyplot(fig)
        plt.close()
        
        # 凡例（日本語と英語の対応）
        st.caption("""
        **凡例**:  
        Vision = 経営ビジョンの明確さ  
        Planning = 事業計画の実行管理  
        Organization = 組織体制の強さ  
        Time Mgmt = 経営者の時間の使い方  
        KPI = 数値管理の仕組み  
        Profitability = 収益性の健全度
        """)
    
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
            st.write("詳しい改善ポイントと具体的アクションプランについては、ADAMSコンサルタントにお問い合わせください。")
    
    st.write("---")
    
    # ランク別のメッセージ
    st.write("### 💡 総合診断")
    
    if rank == "A":
        st.success(f"""
        {rank_icon} **おめでとうございます！優良レベルです**
        
        ✅ 経営の仕組みが確立されています  
        ✅ 事業推進力は高い状態です  
        """)
    elif rank == "B":
        st.info(f"""
        {rank_icon} **標準レベルです**
        
        基本的な仕組みはありますが、改善の余地があります。
        """)
    elif rank == "C":
        st.warning(f"""
        {rank_icon} **要改善レベルです**
        
        事業推進に課題が多い状態です。
        """)
    else:
        st.error(f"""
        {rank_icon} **危機レベルです**
        
        事業推進の仕組みが十分に機能していません。
        """)
    
    st.write("---")
    
    st.info("✅ 診断結果は自動的に記録されました")
    
    # アクションボタン（no-printクラス）
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    if st.button("🔄 診断をやり直す", use_container_width=True):
        st.session_state.scores = {}
        st.session_state.page = 'intro'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ADAMSフッター
    st.markdown(f"""
    <div class="adams-footer">
        <strong>㈱ADAMS Management Consulting Office</strong><br>
        本診断結果は㈱ADAMSにて記録・管理されます<br>
        診断日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
    </div>
    <div class="copyright-notice">
        © 2024 ADAMS Management Consulting Office. All Rights Reserved.<br>
        本診断ツールの無断転用・複製を禁じます
    </div>
    """, unsafe_allow_html=True)

# ページルーティング
if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'questions':
    show_questions()
elif st.session_state.page == 'results':
    show_results()
