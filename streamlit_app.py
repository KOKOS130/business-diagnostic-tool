import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from datetime import datetime
import json
import base64
from io import BytesIO

st.set_page_config(page_title="ADAMS 事業推進力診断ツール", layout="wide", initial_sidebar_state="collapsed")

# ADAMSブランドカラー(ネイビー)
ADAMS_NAVY = "#243666"
ADAMS_LIGHT_NAVY = "#3d5a8f"
ADAMS_ACCENT = "#4a90e2"
ADAMS_GOLD = "#d4af37"

# カスタムCSS - モダンでおしゃれなデザイン
st.markdown(f"""
<style>
    /* 全体の背景にグラデーション */
    .stApp {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }}
    
    /* 印刷時の背景色 */
    @media print {{
        .stApp {{
            background: white !important;
        }}
        .no-print {{
            display: none !important;
        }}
        .print-only {{
            display: block !important;
        }}
    }}
    
    /* メインコンテンツエリア */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    
    /* ヘッダースタイル */
    .main-header {{
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_ACCENT} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }}
    
    .sub-header {{
        font-size: 1.1rem;
        text-align: center;
        color: #5a6c7d;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    
    /* Streamlitカラムの上部余白を完全に削除 */
    [data-testid="column"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    [data-testid="column"] > div {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    div[data-testid="stVerticalBlock"] > div {{
        padding-top: 0 !important;
    }}
    
    .element-container {{
        margin-top: 0 !important;
    }}
    
    /* カードスタイル */
    .info-card {{
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        margin-top: 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(36, 54, 102, 0.1);
    }}
    
    .info-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.06);
    }}
    
    /* 中央揃えコンテナ */
    .center-content {{
        text-align: center;
    }}
    
    .center-content h2, .center-content h3 {{
        text-align: center;
    }}
    
    /* ボタンスタイル */
    .stButton>button {{
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_LIGHT_NAVY} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        height: 3.5rem !important;
        min-height: 3.5rem !important;
        max-height: 3.5rem !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1.5 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(36, 54, 102, 0.3);
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {ADAMS_LIGHT_NAVY} 0%, {ADAMS_ACCENT} 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(36, 54, 102, 0.4);
    }}
    
    .stDownloadButton>button {{
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_LIGHT_NAVY} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        height: 3.5rem !important;
        min-height: 3.5rem !important;
        max-height: 3.5rem !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1.5 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(36, 54, 102, 0.3);
    }}
    
    .stDownloadButton>button:hover {{
        background: linear-gradient(135deg, {ADAMS_LIGHT_NAVY} 0%, {ADAMS_ACCENT} 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(36, 54, 102, 0.4);
    }}
    
    /* プログレスバー */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {ADAMS_NAVY} 0%, {ADAMS_ACCENT} 100%);
        border-radius: 10px;
    }}
    
    /* ラジオボタン */
    .stRadio > div {{
        background: transparent;
        padding: 0;
        margin-top: 0.5rem;
    }}
    
    /* 質問カード内のラジオボタン */
    .question-card .stRadio {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    .question-card .stRadio > div {{
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    /* メトリックカード */
    div[data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {ADAMS_NAVY};
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 1rem;
        color: #5a6c7d;
        font-weight: 500;
    }}
    
    /* エクスパンダー */
    .streamlit-expanderHeader {{
        background: white;
        border-radius: 12px;
        font-weight: 600;
        color: {ADAMS_NAVY};
        padding: 1rem;
        border: 1px solid rgba(36, 54, 102, 0.1);
    }}
    
    .streamlit-expanderHeader:hover {{
        background: #f8f9fa;
        border-color: {ADAMS_NAVY};
    }}
    
    /* フッター */
    .adams-footer {{
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_LIGHT_NAVY} 100%);
        color: white;
        text-align: center;
        font-size: 0.95rem;
        margin-top: 3rem;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(36, 54, 102, 0.2);
    }}
    
    .copyright-notice {{
        text-align: center;
        color: #8090a0;
        font-size: 0.85rem;
        margin-top: 1.5rem;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* インフォボックス */
    .stInfo {{
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid {ADAMS_ACCENT};
        border-radius: 12px;
        padding: 1rem;
    }}
    
    .stSuccess {{
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        border-radius: 12px;
    }}
    
    .stWarning {{
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 4px solid #ff9800;
        border-radius: 12px;
    }}
    
    .stError {{
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 4px solid #f44336;
        border-radius: 12px;
    }}
    
    /* ランクバッジ */
    .rank-badge {{
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{
            transform: scale(1);
        }}
        50% {{
            transform: scale(1.05);
        }}
    }}
    
    /* 質問カード */
    .question-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border-left: 4px solid {ADAMS_NAVY};
        transition: all 0.3s ease;
    }}
    
    .question-card:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }}
    
    .print-only {{
        display: none;
    }}
    
    /* ロゴコンテナ */
    .logo-container {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        display: inline-block;
        margin-bottom: 1.5rem;
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
        "icon": "🎯",
        "questions": [
            "将来のビジョン（3年後にどうなりたいか）を、社員や取引先に明確に説明できますか？",
            "自社の「強み」と「弱み」をそれぞれ3つ以上、すぐに答えることができますか？",
            "会社の経営方針や戦略を、文書やデータとして記録していますか？",
            "日々の経営判断をする際に、明確な判断基準や優先順位がありますか？",
            "幹部社員や管理職は、あなたの経営方針をしっかり理解していますか？",
            "重要な経営判断について、他の人に筋道立てて説明することができますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ ビジョンの定期的な見直しと進化",
                "✓ より具体的な中長期目標の設定",
                "✓ ビジョンの社外への発信強化"
            ],
            "medium": [
                "✓ ビジョンの言語化と可視化",
                "✓ 経営層から現場への伝達方法の改善",
                "✓ ビジョンと日常業務のつながりの明確化",
                "✓ 社員の理解度を測る仕組みづくり"
            ],
            "low": [
                "✓ 経営ビジョンの策定と明文化",
                "✓ 自社の強み・弱みの棚卸し",
                "✓ 経営判断の基準づくり",
                "✓ 経営方針の社内共有の仕組みづくり",
                "✓ 幹部層との認識合わせ"
            ]
        }
    },
    "事業計画の実行管理": {
        "english_label": "Planning",
        "icon": "📋",
        "questions": [
            "今年度の事業計画書（売上目標、利益目標など）を作成していますか？",
            "事業計画の進捗状況を、定期的（週次または月次）にチェックしていますか？",
            "昨年立てた計画に対して、80%以上達成できましたか？",
            "計画と実績にズレが生じた時、その原因を分析していますか？",
            "計画が未達成の場合、修正や改善のアクションをすぐに実行していますか？",
            "全社員が、今年度の会社の目標数値（売上・利益など）を知っていますか？",
            "3ヶ月ごとに、目標達成のための具体的な行動計画がありますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 計画精度のさらなる向上",
                "✓ より高度なPDCAサイクルの実践",
                "✓ 中長期計画との連動性強化"
            ],
            "medium": [
                "✓ 進捗管理の頻度と精度の向上",
                "✓ 計画未達時の原因分析の深掘り",
                "✓ 修正アクションの実行スピード向上",
                "✓ 全社員への目標浸透の仕組み"
            ],
            "low": [
                "✓ 事業計画書の作成習慣の確立",
                "✓ 定期的な進捗確認の仕組みづくり",
                "✓ 実現可能な目標設定の方法",
                "✓ 計画と実績の差異分析の基本",
                "✓ 四半期単位の行動計画の策定"
            ]
        }
    },
    "組織体制の強さ": {
        "english_label": "Organization",
        "icon": "👥",
        "questions": [
            "あなたが1週間不在にしても、会社の業務は問題なく回りますか？",
            "事業運営を任せられる「右腕」となる人材がいますか？",
            "幹部社員や管理職に、適切に権限を委譲（任せる）ことができていますか？",
            "社員が、上司の指示を待たずに自分で判断して行動できていますか？",
            "業務のやり方が標準化され、マニュアルや手順書が整備されていますか？",
            "定例会議で、報告だけでなく、実質的な意思決定ができていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 次世代リーダーの育成",
                "✓ 組織の自律性のさらなる向上",
                "✓ イノベーションを促す組織文化の醸成"
            ],
            "medium": [
                "✓ 権限委譲の範囲の明確化と拡大",
                "✓ 社員の自律的判断力の育成",
                "✓ 業務標準化とマニュアル整備",
                "✓ 会議の質と意思決定スピードの向上"
            ],
            "low": [
                "✓ 経営者不在時の業務運営体制の構築",
                "✓ 右腕人材の発掘と育成",
                "✓ 権限委譲の第一歩（小さな権限から）",
                "✓ 基本的な業務手順の文書化",
                "✓ 定例会議の運営ルールづくり"
            ]
        }
    },
    "経営者の時間の使い方": {
        "english_label": "Time Mgmt",
        "icon": "⏰",
        "questions": [
            "1週間のうち、経営戦略を考える時間が20%以上（週8時間以上）ありますか？",
            "日々の業務に追われて、経営者としての本来の仕事に集中できていますか？",
            "現場の実務（営業・製造・事務作業など）に費やす時間は少ないですか？（週の20%未満）",
            "突発的なトラブル対応や問題解決に、時間を取られることは少ないですか？",
            "「やりたいけど時間がなくてできていないこと」は少ないですか？",
            "経営者がやるべき仕事と、他の人に任せるべき仕事を、明確に区別できていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 戦略思考時間のさらなる質の向上",
                "✓ 外部ネットワークの構築と活用",
                "✓ 学習と自己投資の時間確保"
            ],
            "medium": [
                "✓ 現場業務からの段階的な脱却",
                "✓ 突発対応を減らす仕組みづくり",
                "✓ 重要事項への時間配分の最適化",
                "✓ やるべきこと・任せることの明確化"
            ],
            "low": [
                "✓ 経営者の時間の使い方の現状把握",
                "✓ 戦略思考時間の確保（まず週2時間から）",
                "✓ 現場業務の他者への引き継ぎ開始",
                "✓ トラブル予防の基本的な仕組み",
                "✓ 経営者業務の定義と優先順位づけ"
            ]
        }
    },
    "数値管理の仕組み": {
        "english_label": "KPI",
        "icon": "📊",
        "questions": [
            "重要な数値指標（売上、利益、顧客数など）を定め、週次で確認していますか？",
            "部門ごと、個人ごとに、明確な目標数値が設定されていますか？",
            "目標の達成状況を、グラフやダッシュボードなどで見える化していますか？",
            "目標未達成の時、必ず原因を分析して改善策を立てていますか？",
            "各社員が、自分の目標達成状況を常に把握できていますか？",
            "成果（業績）と報酬（給与・賞与）が、明確に連動する仕組みがありますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 先行指標の活用と予測精度向上",
                "✓ データ分析の高度化",
                "✓ 評価制度のさらなる精緻化"
            ],
            "medium": [
                "✓ KPIの見える化と共有の強化",
                "✓ 目標未達時の分析の深掘り",
                "✓ 社員の目標意識の向上",
                "✓ 成果と報酬の連動性の明確化"
            ],
            "low": [
                "✓ 重要指標（KPI）の選定と定義",
                "✓ 週次での数値確認習慣の確立",
                "✓ 部門・個人別目標の設定方法",
                "✓ 基本的な数値の見える化",
                "✓ 目標管理の仕組みづくり"
            ]
        }
    },
    "収益性の健全度": {
        "english_label": "Profitability",
        "icon": "💰",
        "questions": [
            "過去3年間で、売上高は安定的に成長していますか？",
            "営業利益率（売上に対する利益の割合）は10%以上ありますか？",
            "主要な商品・サービスの粗利率（売上総利益率）を把握していますか？",
            "キャッシュフロー（現金の流れ）を毎月チェックし、資金繰りに問題はありませんか？",
            "不採算事業や赤字商品を定期的に見直し、改善または撤退の判断をしていますか？",
            "固定費（人件費・家賃など）は適正で、売上の変動に対応できる体質ですか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 新規事業・新商品開発への投資",
                "✓ 収益性のさらなる向上施策",
                "✓ 財務体質の強化と成長投資"
            ],
            "medium": [
                "✓ 営業利益率の改善策の実行",
                "✓ 商品・サービス別の収益性分析",
                "✓ キャッシュフロー管理の精度向上",
                "✓ 不採算事業の見極めと改善"
            ],
            "low": [
                "✓ 売上成長のための基本戦略",
                "✓ 利益率の現状把握と目標設定",
                "✓ 粗利率の計算と商品別分析",
                "✓ 月次でのキャッシュフロー確認",
                "✓ 固定費の適正化と変動費化"
            ]
        }
    }
}

# 選択肢（全軸共通）
options = {
    4: "非常に当てはまる",
    3: "やや当てはまる",
    2: "あまり当てはまらない",
    1: "全く当てはまらない"
}

def get_improvement_themes(axis_name, percentage):
    """改善すべきテーマを取得"""
    themes_data = diagnostic_data[axis_name].get("improvement_themes", {})
    
    if percentage >= 75:
        return themes_data.get("high", [])
    elif percentage >= 50:
        return themes_data.get("medium", [])
    else:
        return themes_data.get("low", [])

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

def create_radar_chart_for_pdf(axis_scores, axis_max_scores, labels):
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
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('white')
    
    return fig

def generate_pdf_report(axis_scores, axis_max_scores, total_score, max_total_score, percentage, rank, rank_label):
    """PDF診断レポート生成（改善版）"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    
    buffer = BytesIO()
    
    # 日本語フォント設定
    font_name = 'Helvetica'
    try:
        import matplotlib.font_manager as fm
        font_files = fm.findSystemFonts()
        noto_fonts = {}
        for font_file in font_files:
            if 'NotoSansCJK' in font_file or 'NotoSans-' in font_file:
                if 'Regular' in font_file or 'normal' in font_file.lower():
                    noto_fonts['regular'] = font_file
                elif 'Bold' in font_file or 'bold' in font_file.lower():
                    noto_fonts['bold'] = font_file
        
        if 'regular' in noto_fonts:
            pdfmetrics.registerFont(TTFont('Japanese', noto_fonts['regular']))
            if 'bold' in noto_fonts:
                pdfmetrics.registerFont(TTFont('Japanese-Bold', noto_fonts['bold']))
                registerFontFamily('Japanese', normal='Japanese', bold='Japanese-Bold')
            font_name = 'Japanese'
    except Exception as e:
        print(f"日本語フォント設定エラー: {e}")
    
    # PDFドキュメント設定
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # カスタムスタイル定義
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=22,
        textColor=colors.HexColor(ADAMS_NAVY),
        alignment=TA_CENTER,
        spaceAfter=10,
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor(ADAMS_NAVY),
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=13,
        textColor=colors.HexColor(ADAMS_NAVY),
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=16
    )
    
    # タイトルページ
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph('事業推進力診断レポート', title_style))
    story.append(Paragraph('Business Promotion Diagnostic Report', subtitle_style))
    story.append(Paragraph(f'診断日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}', subtitle_style))
    story.append(Spacer(1, 10*mm))
    
    # 総合評価
    story.append(Paragraph('総合評価 / Overall Evaluation', heading1_style))
    
    eval_data = [
        ['項目', '結果'],
        ['ランク / Rank', f'{rank} ({rank_label})'],
        ['総合スコア / Total Score', f'{total_score} / {max_total_score} 点'],
        ['達成率 / Achievement Rate', f'{percentage:.1f}%']
    ]
    
    eval_table = Table(eval_data, colWidths=[80*mm, 80*mm])
    eval_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), font_name, 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ADAMS_NAVY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 10*mm))
    
    # レーダーチャート
    story.append(Paragraph('6軸バランス分析 / 6-Axis Balance Analysis', heading1_style))
    
    labels = list(axis_scores.keys())
    radar_fig = create_radar_chart_for_pdf(axis_scores, axis_max_scores, labels)
    
    img_buffer = BytesIO()
    radar_fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(radar_fig)
    
    chart_image = Image(img_buffer, width=120*mm, height=120*mm)
    story.append(chart_image)
    story.append(Spacer(1, 8*mm))
    
    # 凡例テーブル
    story.append(Paragraph('軸の説明 / Legend', heading2_style))
    legend_data = [['英語 / English', '日本語 / Japanese']]
    for axis_name in axis_scores.keys():
        english_label = diagnostic_data[axis_name]["english_label"]
        legend_data.append([english_label, axis_name])
    
    legend_table = Table(legend_data, colWidths=[50*mm, 110*mm])
    legend_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), font_name, 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ADAMS_NAVY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 10*mm))
    
    # 各軸の詳細スコア
    story.append(Paragraph('各軸スコア詳細 / Detailed Scores by Axis', heading1_style))
    
    score_data = [['軸 / Axis', 'スコア / Score', '達成率 / Rate']]
    for axis_name, score in axis_scores.items():
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        english_label = diagnostic_data[axis_name]['english_label']
        icon = diagnostic_data[axis_name].get('icon', '')
        score_data.append([
            f'{icon} {axis_name} / {english_label}',
            f'{score} / {max_score}',
            f'{pct:.1f}%'
        ])
    
    score_table = Table(score_data, colWidths=[90*mm, 35*mm, 35*mm])
    score_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), font_name, 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ADAMS_NAVY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10*mm))
    
    # 改善すべきテーマ（優先順位TOP3）
    story.append(Paragraph('優先改善テーマ / Priority Improvement Themes', heading1_style))
    
    sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1] / axis_max_scores[x[0]] if axis_max_scores[x[0]] > 0 else 0)
    
    for idx, (axis_name, score) in enumerate(sorted_axes[:3], 1):
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        icon = diagnostic_data[axis_name].get('icon', '')
        
        story.append(Paragraph(f'{idx}. {icon} {axis_name} ({pct:.1f}%)', heading2_style))
        
        themes = get_improvement_themes(axis_name, pct)
        themes_text = '<br/>'.join(themes)
        story.append(Paragraph(themes_text, body_style))
        story.append(Spacer(1, 5*mm))
    
    story.append(Spacer(1, 5*mm))
    
    # フッター
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph('詳しい改善アクションプランについては、ADAMSコンサルタントにお問い合わせください', footer_style))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('© 2024 ADAMS Management Consulting Office. All Rights Reserved.', footer_style))
    story.append(Paragraph('本診断ツールの無断転用・複製を禁じます', footer_style))
    
    # PDFビルド
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_intro():
    """イントロページ"""
    # ロゴコンテナ（左寄せ） - 上部余白を完全排除
    st.markdown('<div class="logo-container" style="margin-top: 0; padding-top: 0;">', unsafe_allow_html=True)
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=140)
    except:
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 1.1rem;">
            ㈱ADAMS Management Consulting Office
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 中央揃えコンテンツ
    st.markdown('<div class="center-content">', unsafe_allow_html=True)
    st.markdown('<div class="main-header">事業推進力診断ツール</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">✨ 所要時間: 約15分 | 全36問 | その場で結果がわかります ✨</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h2 style="text-align: center; margin-top: 2rem; margin-bottom: 1rem; color: #243666;">🎯 この診断について</h2>', unsafe_allow_html=True)
    
    # HTMLで直接2カラムレイアウトを実装（Streamlitのカラムを使わない）
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 0;">
        <div>
            <div class="info-card">
                <h3>📋 診断内容</h3>
                <p>事業推進力を<strong>6つの軸</strong>で診断します</p>
                <p><strong>所要時間</strong>: 約15分<br>
                <strong>設問数</strong>: 全36問<br>
                <strong>結果</strong>: その場で確認可能</p>
            </div>
            <div class="info-card">
                <h3>📊 わかること</h3>
                <ul style="margin: 0; padding-left: 1.5rem;">
                    <li>総合スコアとランク評価</li>
                    <li>6軸のバランス（レーダーチャート）</li>
                    <li>具体的な改善ポイント</li>
                    <li>優先的に取り組むべき課題</li>
                </ul>
            </div>
        </div>
        <div>
            <div class="info-card">
                <h3>🔍 6つの診断軸</h3>
                <p>🎯 <strong>経営ビジョンの明確さ</strong> (6問)<br>
                📋 <strong>事業計画の実行管理</strong> (7問)<br>
                👥 <strong>組織体制の強さ</strong> (6問)<br>
                ⏰ <strong>経営者の時間の使い方</strong> (6問)<br>
                📊 <strong>数値管理の仕組み</strong> (6問)<br>
                💰 <strong>収益性の健全度</strong> (6問)</p>
            </div>
            <div class="info-card">
                <h3>✅ 回答方法</h3>
                <p>各設問に対して、現状を最も表している選択肢を選んでください</p>
                <ul style="margin: 0; padding-left: 1.5rem;">
                    <li><strong>非常に当てはまる</strong></li>
                    <li><strong>やや当てはまる</strong></li>
                    <li><strong>あまり当てはまらない</strong></li>
                    <li><strong>全く当てはまらない</strong></li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    💡 **診断のポイント**  
    ✓ 直感で正直に回答してください  
    ✓ 理想ではなく、**現状**を評価してください  
    ✓ 全ての設問に回答してください
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
    # ロゴ（小サイズ、左寄せ）
    st.markdown('<div class="logo-container" style="margin-top: 0; padding-top: 0;">', unsafe_allow_html=True)
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 0.95rem;">
            ㈱ADAMS 事業推進力診断ツール
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("## 📝 診断設問")
    
    # プログレスバー
    total_questions = sum(len(data["questions"]) for data in diagnostic_data.values())
    answered = len(st.session_state.scores)
    progress = answered / total_questions if total_questions > 0 else 0
    st.progress(progress)
    st.write(f"**進捗: {answered}/{total_questions} 問回答済み** ({int(progress*100)}%)")

    # 各軸の質問を表示
    for axis_idx, (axis_name, axis_data) in enumerate(diagnostic_data.items(), 1):
        icon = axis_data.get('icon', '📌')
        st.markdown(f"### {icon} 軸{axis_idx}: {axis_name}")
        
        for q_idx, question in enumerate(axis_data['questions'], 1):
            key = f"{axis_name}_{q_idx}"
            
            # 質問カードの開始
            st.markdown(f'<div class="question-card"><p style="margin: 0 0 0.5rem 0; font-weight: 600; font-size: 1.05rem; color: {ADAMS_NAVY};">問{q_idx}. {question}</p>', unsafe_allow_html=True)
            
            if key in st.session_state.scores:
                default_value = st.session_state.scores[key]
            else:
                default_value = 4
            
            # ラジオボタン（カード内）
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
            
            # 質問カードの終了
            st.markdown('</div>', unsafe_allow_html=True)
        
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
    # ロゴ（小サイズ、左寄せ）
    st.markdown('<div class="logo-container" style="margin-top: 0; padding-top: 0;">', unsafe_allow_html=True)
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f"""
        <div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 0.95rem;">
            ㈱ADAMS 事業推進力診断ツール
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    # 総合スコア表示（上部余白を完全に削除）
    st.markdown('<h3 style="margin-top: 0; margin-bottom: 1rem; padding-top: 0;">🎯 総合評価</h3>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; margin-top: 0;">
        <div style='text-align: center; padding: 2.5rem; background: linear-gradient(135deg, {rank_color} 0%, {rank_color}dd 100%); color: white; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.15);'>
            <div style='font-size: 4rem; margin-bottom: 0.5rem;'>{rank_icon}</div>
            <div style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;'>ランク {rank}</div>
            <div style='font-size: 1.3rem; font-weight: 500;'>{rank_label}</div>
        </div>
        <div class="info-card">
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: #5a6c7d; margin-bottom: 0.5rem;">総合スコア</div>
                <div style="font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY};">{total_score} / {max_total_score} 点</div>
            </div>
            <div style="text-align: center; margin-top: 1.5rem;">
                <div style="font-size: 0.9rem; color: #5a6c7d; margin-bottom: 0.5rem;">達成率</div>
                <div style="font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY};">{percentage:.1f}%</div>
            </div>
        </div>
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: {ADAMS_NAVY};">📋 ランク基準</h4>
            <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8;">
                <li><strong>A</strong>: 85%以上（優良）</li>
                <li><strong>B</strong>: 70-84%（標準）</li>
                <li><strong>C</strong>: 55-69%（要改善）</li>
                <li><strong>D</strong>: 55%未満（危機）</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # レーダーチャートと詳細スコア
    st.markdown('<h3 style="margin-top: 2rem; margin-bottom: 1rem;">📈 6軸バランス分析</h3>', unsafe_allow_html=True)
    
    # HTMLでコンテナを開始
    st.markdown('<div style="display: grid; grid-template-columns: 2fr 3fr; gap: 1.5rem; margin-top: 0;">', unsafe_allow_html=True)
    
    # 左側: レーダーチャート
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    
    # レーダーチャート生成
    labels = list(axis_scores.keys())
    scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles_plot = angles + angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    
    # グラデーション効果
    ax.plot(angles_plot, scores_plot, 'o-', linewidth=3, color=ADAMS_NAVY, markersize=10)
    ax.fill(angles_plot, scores_plot, alpha=0.3, color=ADAMS_ACCENT)
    
    # 英語ラベルを使用（文字化け対策）
    english_labels = [diagnostic_data[label]["english_label"] for label in labels]
    
    ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=11, weight='bold')
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['1', '2', '3', '4'], fontsize=9)
    ax.grid(True, linewidth=1, alpha=0.3, color=ADAMS_NAVY)
    
    # 背景色
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # Streamlitでチャートを表示
    st.pyplot(fig)
    plt.close()
    
    # 凡例
    st.markdown("""
    <div style="margin-top: 1rem; padding: 0.8rem; background: #f8f9fa; border-radius: 8px; font-size: 0.85rem; line-height: 1.6;">
        <strong>凡例</strong>:<br>
        Vision = 経営ビジョンの明確さ<br>
        Planning = 事業計画の実行管理<br>
        Organization = 組織体制の強さ<br>
        Time Mgmt = 経営者の時間の使い方<br>
        KPI = 数値管理の仕組み<br>
        Profitability = 収益性の健全度
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 右側: 各軸スコア
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(f'<h4 style="margin: 0 0 1rem 0; color: {ADAMS_NAVY};">📊 各軸スコア</h4>', unsafe_allow_html=True)
    
    for idx, (axis_name, score) in enumerate(axis_scores.items(), 1):
        icon = diagnostic_data[axis_name].get('icon', '📌')
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        
        if pct >= 75:
            color = "🟢"
            badge_color = "#d4edda"
        elif pct >= 50:
            color = "🟡"
            badge_color = "#fff3cd"
        else:
            color = "🔴"
            badge_color = "#f8d7da"
        
        st.markdown(f"""
        <div style='background: {badge_color}; padding: 0.8rem; border-radius: 10px; margin-bottom: 0.8rem;'>
            <strong>{color} {icon} {axis_name}</strong><br>
            <span style='font-size: 1.1rem;'>{score} / {max_score} 点 ({pct:.1f}%)</span>
            <div style='width: 100%; background: #e0e0e0; border-radius: 10px; height: 8px; margin-top: 0.5rem; overflow: hidden;'>
                <div style='width: {pct}%; background: {ADAMS_NAVY}; height: 100%; border-radius: 10px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # コンテナを閉じる
    st.markdown('</div>', unsafe_allow_html=True)

    # 優先改善課題
    st.write("### 🎯 優先改善課題 TOP3")
    
    sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1] / axis_max_scores[x[0]] if axis_max_scores[x[0]] > 0 else 0)
    
    medals = ["🥇", "🥈", "🥉"]
    priorities = ["最優先課題", "第2優先", "第3優先"]
    
    for idx, (axis_name, score) in enumerate(sorted_axes[:3]):
        pct = (score / axis_max_scores[axis_name]) * 100 if axis_max_scores[axis_name] > 0 else 0
        icon = diagnostic_data[axis_name].get('icon', '📌')
        
        with st.expander(f"{medals[idx]} {priorities[idx]}: {icon} {axis_name} ({pct:.1f}%)", expanded=(idx==0)):
            st.write(f"**現状スコア**: {score} / {axis_max_scores[axis_name]} 点")

            st.write("**💡 改善すべきテーマ**")
            
            # 改善すべきテーマを取得して表示
            themes = get_improvement_themes(axis_name, pct)
            for theme in themes:
                st.write(theme)

    # ランク別のメッセージ
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    st.info("💬 詳しい改善アクションプランについては、ADAMSコンサルタントにお問い合わせください")

    # 印刷・PDF出力ボタン（no-printクラスで印刷時非表示）
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    # PDFダウンロードボタン用のデータ準備
    pdf_buffer = generate_pdf_report(axis_scores, axis_max_scores, total_score, 
                                     max_total_score, percentage, rank, rank_label)
    
    # ボタンをHTML Gridで配置（白いブロック対策）
    st.markdown('<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0;">', unsafe_allow_html=True)
    
    # 左側: 印刷ボタン（HTML Gridの1列目）
    st.markdown('<div style="grid-column: 1;">', unsafe_allow_html=True)
    if st.button("🖨️ 印刷する", use_container_width=True, key="print_btn"):
        st.markdown("""
        <script>
        setTimeout(function() {
            window.print();
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 右側: PDFダウンロードボタン（HTML Gridの2列目）
    st.markdown('<div style="grid-column: 2;">', unsafe_allow_html=True)
    st.download_button(
        label="📄 PDFダウンロード",
        data=pdf_buffer,
        file_name=f"ADAMS_診断結果_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 診断をやり直すボタン
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
