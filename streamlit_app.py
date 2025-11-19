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

# カスタムCSS - 白いブロック完全排除版
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
    
    /* メインコンテンツエリア - 上部余白を完全削除 */
    .main .block-container {{
        padding-top: 0 !important;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin-top: 0 !important;
    }}
    
    /* すべてのStreamlit要素の余白を削除 */
    .main .block-container > div:first-child {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    /* Streamlitのデフォルト余白を完全削除 */
    [data-testid="column"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    [data-testid="column"] > div {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    div[data-testid="stVerticalBlock"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
        gap: 0 !important;
    }}
    
    div[data-testid="stVerticalBlock"] > div {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    .element-container {{
        margin-top: 0 !important;
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
        margin-top: 1rem;
        letter-spacing: -0.5px;
    }}
    
    .sub-header {{
        font-size: 1.1rem;
        text-align: center;
        color: #5a6c7d;
        margin-bottom: 2rem;
        margin-top: 0;
        font-weight: 400;
    }}
    
    /* カードスタイル */
    .info-card {{
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
        margin-bottom: 0;
        margin-top: 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(36, 54, 102, 0.08);
    }}
    
    .info-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.06);
    }}
    
    /* 中央揃えコンテナ */
    .center-content {{
        text-align: center;
    }}
    
    /* ボタンスタイル */
    .stButton>button {{
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_LIGHT_NAVY} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        height: 3.5rem !important;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(36, 54, 102, 0.3);
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(36, 54, 102, 0.4);
    }}
    
    /* 質問カードスタイル */
    .question-card {{
        background: white;
        border-left: 4px solid {ADAMS_ACCENT};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        margin-top: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    
    .question-card:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateX(4px);
    }}
    
    /* ロゴコンテナ - 余白完全削除 */
    .logo-container {{
        text-align: left;
        margin: 0;
        padding: 0.5rem 0;
    }}
    
    /* プログレスバー */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {ADAMS_NAVY} 0%, {ADAMS_ACCENT} 100%);
    }}
    
    /* 著作権表示 */
    .copyright {{
        text-align: center;
        color: #5a6c7d;
        font-size: 0.85rem;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid rgba(36, 54, 102, 0.1);
    }}
    
    /* 印刷時非表示 */
    .no-print {{
        display: block;
    }}
    
    @media print {{
        .no-print {{
            display: none !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# 診断データ（6軸36問）
diagnostic_data = {
    "経営ビジョンの明確さ": {
        "english_label": "Vision",
        "icon": "🎯",
        "questions": [
            "経営理念やビジョン（将来のあるべき姿）が明文化されていますか？",
            "経営理念やビジョンは、社員全員が理解し、共感できる内容ですか？",
            "経営理念やビジョンを、定期的に社員に伝え、浸透させる機会がありますか？",
            "3〜5年後の具体的な事業目標（売上、利益、顧客数など）を設定していますか？",
            "自社の強み（他社にない独自の価値）を明確に把握していますか？",
            "お客様から「この会社でなければならない」と選ばれる理由がありますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ ビジョンの更なる具体化と進化",
                "✓ 社会的価値の創造と発信",
                "✓ ブランド力の強化"
            ],
            "medium": [
                "✓ 理念の定期的な見直しと更新",
                "✓ 社員への浸透活動の強化",
                "✓ 中長期目標の明確化",
                "✓ 独自の強みの言語化"
            ],
            "low": [
                "✓ 経営理念・ビジョンの策定",
                "✓ 社員との対話機会の創出",
                "✓ 3〜5年後の目標設定",
                "✓ 自社の強みの棚卸し",
                "✓ 顧客価値の明確化"
            ]
        }
    },
    "事業計画の実行管理": {
        "english_label": "Planning",
        "icon": "📋",
        "questions": [
            "年間の事業計画（売上計画・利益計画）を作成していますか？",
            "事業計画を達成するための具体的な行動計画がありますか？",
            "計画の進捗状況を、月次または週次で確認していますか？",
            "計画と実績の差異（ギャップ）が生じた際、原因分析を行っていますか？",
            "計画が未達の場合、改善策を立て、すぐに行動していますか？",
            "年度末には計画の振り返りを行い、次年度の計画に活かしていますか？",
            "社員に対して、会社の計画や目標を明確に伝えていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 計画精度のさらなる向上",
                "✓ PDCAサイクルの高速化",
                "✓ データドリブン経営の推進"
            ],
            "medium": [
                "✓ 月次レビューの質の向上",
                "✓ 差異分析の深掘り",
                "✓ 改善策の実行スピード向上",
                "✓ 社員への計画共有の強化"
            ],
            "low": [
                "✓ 年間事業計画の策定",
                "✓ 行動計画への落とし込み",
                "✓ 進捗確認の仕組みづくり",
                "✓ 計画と実績の比較習慣",
                "✓ 振り返りと改善のサイクル確立"
            ]
        }
    },
    "組織体制の強さ": {
        "english_label": "Organization",
        "icon": "👥",
        "questions": [
            "各社員の役割分担が明確で、誰が何を担当しているか把握できていますか？",
            "社員が、経営者の指示を待たずに自律的に動ける組織ですか？",
            "経営者が不在でも、現場の業務が滞りなく回る仕組みがありますか？",
            "右腕となる「No.2人材」が育っていますか？",
            "重要な意思決定や業務を、経営者以外にも任せられていますか？",
            "定期的な会議やミーティングで、情報共有や意思決定が行われていますか？"
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
                "✓ 財務体質の強化"
            ],
            "medium": [
                "✓ 営業利益率の向上策",
                "✓ 商品別収益性の分析",
                "✓ キャッシュフロー管理の精緻化",
                "✓ 固定費の最適化"
            ],
            "low": [
                "✓ 売上成長戦略の策定",
                "✓ 利益率の現状把握",
                "✓ 粗利管理の開始",
                "✓ 月次資金繰り表の作成",
                "✓ 不採算事業の洗い出し"
            ]
        }
    }
}

# 回答選択肢
options = {
    4: "非常に当てはまる",
    3: "やや当てはまる",
    2: "あまり当てはまらない",
    1: "全く当てはまらない"
}

# セッションステートの初期化
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'page' not in st.session_state:
    st.session_state.page = 'intro'

def save_to_google_sheets(data):
    """Google Sheetsに結果を保存（ダミー実装）"""
    pass

def generate_pdf_report(axis_scores, axis_max_scores, total_score, max_total_score, percentage, rank, rank_label):
    """PDF診断結果レポート生成"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import mm
    
    buffer = BytesIO()
    
    # フォント登録
    try:
        pdfmetrics.registerFont(TTFont('NotoSans', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', subfontIndex=0))
        font_name = 'NotoSans'
    except:
        font_name = 'Helvetica'
    
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # タイトル
    c.setFont(font_name, 20)
    c.drawString(50, height - 50, "ADAMS 事業推進力診断結果")
    
    # 診断日時
    c.setFont(font_name, 10)
    c.drawString(50, height - 80, f"診断日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    
    # 総合評価
    c.setFont(font_name, 14)
    c.drawString(50, height - 120, f"総合スコア: {total_score} / {max_total_score} 点")
    c.drawString(50, height - 140, f"達成率: {percentage:.1f}%")
    c.drawString(50, height - 160, f"ランク: {rank} ({rank_label})")
    
    # 各軸スコア
    c.setFont(font_name, 12)
    y_position = height - 200
    c.drawString(50, y_position, "【各軸スコア】")
    y_position -= 20
    
    c.setFont(font_name, 10)
    for axis_name, score in axis_scores.items():
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        c.drawString(50, y_position, f"{axis_name}: {score}/{max_score} 点 ({pct:.1f}%)")
        y_position -= 20
    
    # 著作権表示
    c.setFont(font_name, 8)
    c.drawString(50, 30, "© 株式会社ADAMS Management Consulting Office - 無断転用を禁じます")
    
    c.save()
    buffer.seek(0)
    return buffer

def get_rank(percentage):
    """ランク判定"""
    if percentage >= 85:
        return "A", "優良レベル", "🏆", "#2ecc71"
    elif percentage >= 70:
        return "B", "標準レベル", "⭐", "#3498db"
    elif percentage >= 55:
        return "C", "要改善レベル", "⚠️", "#f39c12"
    else:
        return "D", "危機レベル", "🚨", "#e74c3c"

def show_intro():
    """イントロページ - 完全HTML Grid版"""
    # ロゴ（完全に余白なし）
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
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
    
    st.markdown('<h2 style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem; color: #243666;">🎯 この診断について</h2>', unsafe_allow_html=True)
    
    # HTMLで直接2カラムレイアウトを実装（カードを簡潔に）
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0; margin-bottom: 1rem;">
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div class="info-card">
                <h3 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem;">📋 診断内容</h3>
                <p style="margin: 0; line-height: 1.5; font-size: 0.95rem;">事業推進力を<strong>6つの軸</strong>で診断<br>
                <strong>所要時間</strong>: 約15分・<strong>全36問</strong></p>
            </div>
            <div class="info-card">
                <h3 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem;">📊 わかること</h3>
                <ul style="margin: 0; padding-left: 1.3rem; line-height: 1.6; font-size: 0.95rem;">
                    <li>総合スコアとランク評価</li>
                    <li>6軸バランス（レーダーチャート）</li>
                    <li>具体的な改善ポイント</li>
                </ul>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div class="info-card">
                <h3 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem;">🔍 6つの診断軸</h3>
                <p style="margin: 0; line-height: 1.5; font-size: 0.88rem;">
                🎯 経営ビジョンの明確さ (6問)<br>
                📋 事業計画の実行管理 (7問)<br>
                👥 組織体制の強さ (6問)<br>
                ⏰ 経営者の時間の使い方 (6問)<br>
                📊 数値管理の仕組み (6問)<br>
                💰 収益性の健全度 (6問)</p>
            </div>
            <div class="info-card">
                <h3 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem;">✅ 回答方法</h3>
                <p style="margin: 0 0 0.4rem 0; font-size: 0.95rem;">各設問について現状を選択</p>
                <ul style="margin: 0; padding-left: 1.3rem; line-height: 1.5; font-size: 0.88rem;">
                    <li>非常に当てはまる</li>
                    <li>やや当てはまる</li>
                    <li>あまり当てはまらない</li>
                    <li>全く当てはまらない</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ボタンを明確に分離（適切な余白を確保）
    st.markdown('<div style="margin-top: 2rem; margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    
    if st.button("🚀 診断を始める", type="primary", use_container_width=True):
        st.session_state.page = 'questions'
        st.rerun()
    
    # 著作権表示
    st.markdown(f"""
    <div class="copyright">
        © 株式会社ADAMS Management Consulting Office<br>
        本診断ツールの無断転用を禁じます
    </div>
    """, unsafe_allow_html=True)

def show_questions():
    """質問ページ - 既に修正済み（維持）"""
    # ロゴ（小サイズ、左寄せ）
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
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
    percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0
    
    return axis_scores, axis_max_scores, total_score, max_total_score, percentage

def show_results():
    """結果ページ - 完全HTML Grid版（st.columns()完全排除）"""
    # ロゴ（小サイズ、左寄せ）
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
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
    
    # 結果データの準備
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
    
    # ===== 総合評価セクション（HTML Grid 3カラム）=====
    st.markdown('<h3 style="margin-top: 1rem; margin-bottom: 0.8rem;">🎯 総合評価</h3>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 0;">
        <!-- カラム1: ランクカード -->
        <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {rank_color} 0%, {rank_color}dd 100%); 
                    color: white; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.15);'>
            <div style='font-size: 4rem; margin-bottom: 0.5rem;'>{rank_icon}</div>
            <div style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;'>ランク {rank}</div>
            <div style='font-size: 1.3rem; font-weight: 500;'>{rank_label}</div>
        </div>
        
        <!-- カラム2: 総合スコア -->
        <div class="info-card">
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: #5a6c7d; margin-bottom: 0.5rem;">総合スコア</div>
                <div style="font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY}; margin-bottom: 1.5rem;">{total_score} / {max_total_score} 点</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: #5a6c7d; margin-bottom: 0.5rem;">達成率</div>
                <div style="font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY};">{percentage:.1f}%</div>
            </div>
        </div>
        
        <!-- カラム3: ランク基準 -->
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: {ADAMS_NAVY};">📋 ランク基準</h4>
            <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8; font-size: 0.95rem;">
                <li><strong>A</strong>: 85%以上（優良レベル）</li>
                <li><strong>B</strong>: 70-84%（標準レベル）</li>
                <li><strong>C</strong>: 55-69%（要改善レベル）</li>
                <li><strong>D</strong>: 55%未満（危機レベル）</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== 6軸バランス分析セクション（HTML Grid 2カラム + st.pyplot()）=====
    st.markdown('<h3 style="margin-top: 2rem; margin-bottom: 0.8rem;">📈 6軸バランス分析</h3>', unsafe_allow_html=True)
    
    # レーダーチャート生成
    labels = list(axis_scores.keys())
    scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles_plot = angles + angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # グラデーション効果
    ax.plot(angles_plot, scores_plot, 'o-', linewidth=3, color=ADAMS_NAVY, markersize=10)
    ax.fill(angles_plot, scores_plot, alpha=0.3, color=ADAMS_ACCENT)
    
    # 英語ラベルを使用（文字化け対策）
    english_labels = [diagnostic_data[label]["english_label"] for label in labels]
    
    ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=12, weight='bold')
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['1', '2', '3', '4'], fontsize=10)
    ax.grid(True, linewidth=1, alpha=0.3, color=ADAMS_NAVY)
    
    # 背景色
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # チャートをバッファに保存してbase64化
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    
    # 各軸スコアのHTML生成
    axis_scores_html = ""
    for idx, (axis_name, score) in enumerate(axis_scores.items(), 1):
        icon = diagnostic_data[axis_name].get('icon', '📌')
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        
        if pct >= 75:
            color = "🟢"
            badge_color = "#d4edda"
            bar_color = "#28a745"
        elif pct >= 50:
            color = "🟡"
            badge_color = "#fff3cd"
            bar_color = "#ffc107"
        else:
            color = "🔴"
            badge_color = "#f8d7da"
            bar_color = "#dc3545"
        
        axis_scores_html += f"""
        <div style='background: {badge_color}; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.8rem;'>
            <div style='margin-bottom: 0.5rem;'>
                <strong>{color} {icon} {axis_name}</strong>
            </div>
            <div style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
                {score} / {max_score} 点 ({pct:.1f}%)
            </div>
            <div style='width: 100%; background: #e0e0e0; border-radius: 10px; height: 10px; overflow: hidden;'>
                <div style='width: {pct}%; background: {bar_color}; height: 100%; border-radius: 10px; transition: width 0.3s ease;'></div>
            </div>
        </div>
        """
    
    # HTML Grid 2カラムレイアウト
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 2fr 3fr; gap: 1rem; margin-top: 0;">
        <!-- 左側: レーダーチャート -->
        <div class="info-card">
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto; border-radius: 8px;">
            <div style="margin-top: 1rem; padding: 0.8rem; background: #f8f9fa; border-radius: 8px; font-size: 0.85rem; line-height: 1.6;">
                <strong>凡例</strong>:<br>
                Vision = 経営ビジョンの明確さ<br>
                Planning = 事業計画の実行管理<br>
                Organization = 組織体制の強さ<br>
                Time Mgmt = 経営者の時間の使い方<br>
                KPI = 数値管理の仕組み<br>
                Profitability = 収益性の健全度
            </div>
        </div>
        
        <!-- 右側: 各軸スコア -->
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: {ADAMS_NAVY};">📊 各軸スコア</h4>
            {axis_scores_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== 優先改善課題 TOP3 =====
    st.write("### 🎯 優先改善課題 TOP3")
    
    sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1] / axis_max_scores[x[0]] if axis_max_scores[x[0]] > 0 else 0)
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (axis_name, score) in enumerate(sorted_axes[:3]):
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        icon = diagnostic_data[axis_name].get('icon', '📌')
        
        # スコアに応じたテーマを選択
        if pct >= 75:
            level = "high"
        elif pct >= 50:
            level = "medium"
        else:
            level = "low"
        
        themes = diagnostic_data[axis_name]["improvement_themes"][level]
        
        st.markdown(f"""
        <div class="info-card">
            <h4 style="margin-top: 0;">{medals[i]} 第{i+1}位: {icon} {axis_name}</h4>
            <p><strong>現在のスコア</strong>: {score}/{max_score} 点 ({pct:.1f}%)</p>
            <p><strong>取り組むと良いテーマ（ヒント）</strong>:</p>
            <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8;">
                {''.join([f"<li>{theme}</li>" for theme in themes])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== 総合診断コメント =====
    st.write("### 💬 総合診断コメント")
    
    if percentage >= 85:
        comment = "🎉 **素晴らしい！** 事業推進力が非常に高い状態です。現状を維持しつつ、さらなる成長に向けた新たな挑戦を検討してください。"
    elif percentage >= 70:
        comment = "👍 **良好！** 事業推進の基盤がしっかりしています。弱点となっている軸を強化することで、さらなる飛躍が期待できます。"
    elif percentage >= 55:
        comment = "⚠️ **要改善！** 改善の余地が大きい状態です。優先改善課題TOP3から着手し、段階的に事業推進力を高めていきましょう。"
    else:
        comment = "🚨 **要注意！** 早急な改善が必要です。まずは優先度の高い課題から集中的に取り組むことをお勧めします。"
    
    st.info(comment)
    
    # ===== アクションボタン =====
    st.markdown('<div class="no-print" style="margin-top: 2rem;">', unsafe_allow_html=True)
    
    # PDFダウンロードボタン用のデータ準備
    pdf_buffer = generate_pdf_report(axis_scores, axis_max_scores, total_score, 
                                     max_total_score, percentage, rank, rank_label)
    
    # ボタンをHTML Gridで配置
    st.markdown('<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0;">', unsafe_allow_html=True)
    
    # 左側: 印刷ボタン
    st.markdown('<div>', unsafe_allow_html=True)
    if st.button("🖨️ 印刷する", use_container_width=True, key="print_btn"):
        st.markdown("""
        <script>
        setTimeout(function() {
            window.print();
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 右側: PDFダウンロードボタン
    st.markdown('<div>', unsafe_allow_html=True)
    st.download_button(
        label="📄 PDFダウンロード",
        data=pdf_buffer,
        file_name=f"ADAMS_診断結果_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # ボタンGrid終了
    st.markdown('</div>', unsafe_allow_html=True)  # no-print終了
    
    # もう一度診断するボタン
    st.markdown('<div class="no-print" style="margin-top: 1rem;">', unsafe_allow_html=True)
    if st.button("🔄 もう一度診断する", use_container_width=True):
        st.session_state.scores = {}
        st.session_state.page = 'intro'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 著作権表示
    st.markdown(f"""
    <div class="copyright">
        © 株式会社ADAMS Management Consulting Office<br>
        本診断結果の無断転用を禁じます
    </div>
    """, unsafe_allow_html=True)

# メイン処理
if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'questions':
    show_questions()
elif st.session_state.page == 'results':
    show_results()
