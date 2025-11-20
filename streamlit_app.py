import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from datetime import datetime
import json
import base64
from io import BytesIO
from pdf_report_generator import generate_pdf_report

st.set_page_config(page_title="ADAMS 事業推進力診断ツール", layout="wide", initial_sidebar_state="collapsed")

# ADAMSブランドカラー(ネイビー)
ADAMS_NAVY = "#243666"
ADAMS_LIGHT_NAVY = "#3d5a8f"
ADAMS_ACCENT = "#4a90e2"
ADAMS_GOLD = "#d4af37"

# カスタムCSS
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
    }}
    
    /* メインコンテンツエリア */
    .main .block-container {{
        padding-top: 1rem;
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
        margin-top: 1rem;
    }}
    
    .sub-header {{
        font-size: 1.1rem;
        text-align: center;
        color: #5a6c7d;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    
    /* カードスタイル */
    .info-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        border: 1px solid rgba(36, 54, 102, 0.08);
    }}
    
    .info-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }}
    
    /* ボタンスタイル */
    .stButton>button {{
        background: linear-gradient(135deg, {ADAMS_NAVY} 0%, {ADAMS_LIGHT_NAVY} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
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
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    
    .question-card:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateX(4px);
    }}
    
    /* ロゴコンテナ */
    .logo-container {{
        text-align: left;
        margin-bottom: 1rem;
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
    
    /* ランクカード */
    .rank-card {{
        text-align: center;
        padding: 2rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 1rem;
    }}
    
    /* Streamlitのデフォルトマージン削減 */
    .element-container {{
        margin-bottom: 0.5rem !important;
    }}
    
    h1, h2, h3, h4 {{
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
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
                "✓ 改善アクションの迅速化",
                "✓ 社員への情報共有強化"
            ],
            "low": [
                "✓ 年間事業計画の策定",
                "✓ 行動計画の具体化",
                "✓ 進捗確認の仕組み構築",
                "✓ 差異分析の習慣化",
                "✓ 計画の見える化"
            ]
        }
    },
    "組織体制の強さ": {
        "english_label": "Organization",
        "icon": "👥",
        "questions": [
            "各メンバーの役割と責任が明確になっていますか？",
            "組織図や業務分担表が整備されていますか？",
            "社員の能力やスキルを把握し、適材適所の配置ができていますか？",
            "定期的な1on1ミーティングや評価面談を実施していますか？",
            "社員の育成計画があり、スキルアップの機会を提供していますか？",
            "社内のコミュニケーションは円滑で、風通しの良い職場環境ですか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 次世代リーダーの育成",
                "✓ 組織文化のさらなる強化",
                "✓ エンゲージメント向上施策"
            ],
            "medium": [
                "✓ 役割分担の最適化",
                "✓ 評価制度の見直し",
                "✓ 育成プログラムの体系化",
                "✓ コミュニケーション活性化"
            ],
            "low": [
                "✓ 組織図の作成",
                "✓ 役割と責任の明確化",
                "✓ 1on1ミーティングの導入",
                "✓ 評価制度の構築",
                "✓ 育成計画の策定"
            ]
        }
    },
    "経営者の時間の使い方": {
        "english_label": "Time Mgmt",
        "icon": "⏰",
        "questions": [
            "経営者として、「やるべきこと」と「やりたいこと」を明確に区別できていますか？",
            "日々の業務の中で、重要な経営課題に取り組む時間を確保できていますか？",
            "現場の細かい業務に追われず、経営者としての本来の役割に集中できていますか？",
            "社員に仕事を任せ、権限委譲ができていますか？",
            "中長期的な戦略を考える時間を定期的に確保していますか？",
            "自己研鑽や学びの時間を意識的に取っていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 戦略的思考時間のさらなる拡大",
                "✓ 外部ネットワーク構築",
                "✓ 経営者としての学びの深化"
            ],
            "medium": [
                "✓ 時間管理手法の高度化",
                "✓ 権限委譲の拡大",
                "✓ 重要課題への集中力向上",
                "✓ 学習時間の確保"
            ],
            "low": [
                "✓ 時間の使い方の可視化",
                "✓ 優先順位の明確化",
                "✓ 権限委譲の開始",
                "✓ 戦略思考時間の確保",
                "✓ 学びの習慣化"
            ]
        }
    },
    "数値管理の仕組み": {
        "english_label": "KPI",
        "icon": "📊",
        "questions": [
            "月次の売上・利益を正確に把握していますか？",
            "経営判断に必要な数値（KPI）を定期的にチェックしていますか？",
            "数値データをもとに、問題点や改善点を見つけられていますか？",
            "キャッシュフロー（資金繰り）を常に意識していますか？",
            "財務諸表（損益計算書・貸借対照表）を理解し、活用していますか？",
            "数値目標を社員と共有し、達成に向けて動いていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 予測分析の高度化",
                "✓ データドリブン経営の深化",
                "✓ リアルタイムダッシュボード構築"
            ],
            "medium": [
                "✓ KPIの精緻化",
                "✓ 数値分析力の向上",
                "✓ キャッシュフロー管理の強化",
                "✓ 社員への数値共有強化"
            ],
            "low": [
                "✓ 月次決算の仕組み構築",
                "✓ 重要KPIの設定",
                "✓ 数値の見える化",
                "✓ キャッシュフロー管理の開始",
                "✓ 財務諸表の基礎理解"
            ]
        }
    },
    "収益性の健全度": {
        "english_label": "Profitability",
        "icon": "💰",
        "questions": [
            "売上に対する利益率（売上高営業利益率）を把握していますか？",
            "商品やサービスごとの利益率を把握し、採算管理ができていますか？",
            "無駄なコストを定期的に見直し、削減する取り組みをしていますか？",
            "価格設定が適正で、利益を確保できる価格になっていますか？",
            "売上が増えれば、それに見合った利益も増える仕組みがありますか？",
            "将来の投資や成長のための資金を確保できていますか？"
        ],
        "improvement_themes": {
            "high": [
                "✓ 収益構造の最適化",
                "✓ 新規事業への投資",
                "✓ 利益率のさらなる改善"
            ],
            "medium": [
                "✓ 商品別採算分析の精緻化",
                "✓ コスト削減施策の推進",
                "✓ 価格戦略の見直し",
                "✓ 投資計画の策定"
            ],
            "low": [
                "✓ 利益率の把握",
                "✓ 商品別採算管理の開始",
                "✓ コスト構造の可視化",
                "✓ 価格設定の見直し",
                "✓ 資金計画の策定"
            ]
        }
    }
}

# 回答オプション
options = {
    4: "非常に当てはまる",
    3: "やや当てはまる",
    2: "あまり当てはまらない",
    1: "全く当てはまらない"
}

# Google Sheets保存機能（ダミー）
def save_to_google_sheets(data):
    """Google Sheetsへのデータ保存（実装は省略）"""
    pass

# ランク判定関数
def get_rank(percentage):
    if percentage >= 85:
        return "A", "優良レベル", "🏆", ADAMS_GOLD
    elif percentage >= 70:
        return "B", "標準レベル", "🥈", ADAMS_ACCENT
    elif percentage >= 55:
        return "C", "要改善レベル", "🥉", "#ff9800"
    else:
        return "D", "危機レベル", "⚠️", "#f44336"

def show_intro():
    """イントロページ"""
    # ロゴ
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=140)
    except:
        st.markdown(f'<div style="color: {ADAMS_NAVY}; font-weight: bold; font-size: 1.1rem;">㈱ADAMS Management Consulting Office</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">事業推進力診断ツール</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">✨ 所要時間: 約15分 | 全36問 | その場で結果がわかります ✨</div>', unsafe_allow_html=True)
    
    st.markdown("## 🎯 この診断について")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>📋 診断内容</h3>
            <p>事業推進力を<strong>6つの軸</strong>で診断します</p>
            <p><strong>所要時間</strong>: 約15分 | <strong>設問数</strong>: 全36問</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>📊 わかること</h3>
            <ul>
                <li>総合スコアとランク評価</li>
                <li>6軸のバランス（レーダーチャート）</li>
                <li>具体的な改善ポイント</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🔍 6つの診断軸</h3>
            <p style="font-size: 0.9rem;">
            🎯 経営ビジョンの明確さ (6問)<br>
            📋 事業計画の実行管理 (7問)<br>
            👥 組織体制の強さ (6問)<br>
            ⏰ 経営者の時間の使い方 (6問)<br>
            📊 数値管理の仕組み (6問)<br>
            💰 収益性の健全度 (6問)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>✅ 回答方法</h3>
            <p>各設問に対して、現状を最も表している選択肢を選んでください</p>
            <ul style="font-size: 0.9rem;">
                <li>非常に当てはまる</li>
                <li>やや当てはまる</li>
                <li>あまり当てはまらない</li>
                <li>全く当てはまらない</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 診断を始める", type="primary", use_container_width=True):
        st.session_state.page = 'questions'
        st.rerun()
    
    st.markdown(f"""
    <div class="copyright">
        © 株式会社ADAMS Management Consulting Office<br>
        本診断ツールの無断転用を禁じます
    </div>
    """, unsafe_allow_html=True)

def show_questions():
    """質問ページ"""
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f'<div style="color: {ADAMS_NAVY}; font-weight: bold;">㈱ADAMS 事業推進力診断ツール</div>', unsafe_allow_html=True)
    
    st.write("## 📝 診断設問")
    
    total_questions = sum(len(data["questions"]) for data in diagnostic_data.values())
    answered = len(st.session_state.scores)
    progress = answered / total_questions if total_questions > 0 else 0
    st.progress(progress)
    st.write(f"**進捗: {answered}/{total_questions} 問回答済み** ({int(progress*100)}%)")

    for axis_idx, (axis_name, axis_data) in enumerate(diagnostic_data.items(), 1):
        icon = axis_data.get('icon', '📌')
        st.markdown(f"### {icon} 軸{axis_idx}: {axis_name}")
        
        for q_idx, question in enumerate(axis_data['questions'], 1):
            key = f"{axis_name}_{q_idx}"
            
            st.markdown(f'<div class="question-card"><p style="font-weight: 600; color: {ADAMS_NAVY};">問{q_idx}. {question}</p>', unsafe_allow_html=True)
            
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
    """結果ページ - シンプルで確実に表示される版"""
    try:
        st.image("https://raw.githubusercontent.com/KOKOS130/business-diagnostic-tool/main/adams_logo.png", width=100)
    except:
        st.markdown(f'<div style="color: {ADAMS_NAVY}; font-weight: bold;">㈱ADAMS 事業推進力診断ツール</div>', unsafe_allow_html=True)
    
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
    
    save_to_google_sheets(result_data)
    
    # ===== 総合評価セクション =====
    st.write("### 🎯 総合評価")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="rank-card" style="background: linear-gradient(135deg, {rank_color} 0%, {rank_color}dd 100%);">
            <div style='font-size: 4rem; margin-bottom: 0.5rem;'>{rank_icon}</div>
            <div style='font-size: 2.5rem; font-weight: 800;'>ランク {rank}</div>
            <div style='font-size: 1.2rem;'>{rank_label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4 style="text-align: center; color: {ADAMS_NAVY};">総合スコア</h4>
            <p style="text-align: center; font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY}; margin: 1rem 0;">
                {total_score} / {max_total_score} 点
            </p>
            <h4 style="text-align: center; color: {ADAMS_NAVY};">達成率</h4>
            <p style="text-align: center; font-size: 2rem; font-weight: 700; color: {ADAMS_NAVY}; margin: 1rem 0;">
                {percentage:.1f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card">
            <h4 style="color: {ADAMS_NAVY};">📋 ランク基準</h4>
            <ul>
                <li><strong>A</strong>: 85%以上（優良レベル）</li>
                <li><strong>B</strong>: 70-84%（標準レベル）</li>
                <li><strong>C</strong>: 55-69%（要改善レベル）</li>
                <li><strong>D</strong>: 55%未満（危機レベル）</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== 6軸バランス分析 =====
    st.write("### 📈 6軸バランス分析")
    
    # レーダーチャート生成
    labels = list(axis_scores.keys())
    scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles_plot = angles + angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    ax.plot(angles_plot, scores_plot, 'o-', linewidth=3, color=ADAMS_NAVY, markersize=10)
    ax.fill(angles_plot, scores_plot, alpha=0.3, color=ADAMS_ACCENT)
    
    english_labels = [diagnostic_data[label]["english_label"] for label in labels]
    ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=14, weight='bold')
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['1', '2', '3', '4'], fontsize=12)
    ax.grid(True, linewidth=1, alpha=0.3, color=ADAMS_NAVY)
    
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.pyplot(fig)
        plt.close()
        
        st.info("""
        **凡例**:  
        Vision = 経営ビジョンの明確さ  
        Planning = 事業計画の実行管理  
        Organization = 組織体制の強さ  
        Time Mgmt = 経営者の時間の使い方  
        KPI = 数値管理の仕組み  
        Profitability = 収益性の健全度
        """)
    
    with col2:
        st.markdown(f"#### 📊 各軸スコア")
        
        for axis_name, score in axis_scores.items():
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
            <div style='background: {badge_color}; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                <div><strong>{color} {icon} {axis_name}</strong></div>
                <div style='font-size: 1.1rem; margin: 0.5rem 0;'>{score} / {max_score} 点 ({pct:.1f}%)</div>
                <div style='width: 100%; background: #e0e0e0; border-radius: 10px; height: 10px;'>
                    <div style='width: {pct}%; background: {ADAMS_ACCENT}; height: 100%; border-radius: 10px;'></div>
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
        
        if pct >= 75:
            level = "high"
        elif pct >= 50:
            level = "medium"
        else:
            level = "low"
        
        themes = diagnostic_data[axis_name]["improvement_themes"][level]
        
        with st.expander(f"{medals[i]} 第{i+1}位: {icon} {axis_name}（{score}/{max_score} 点 - {pct:.1f}%）"):
            st.write("**取り組むと良いテーマ（ヒント）**:")
            for theme in themes:
                st.write(theme)
    
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
    st.write("---")
    
    # PDFレポートダウンロードボタン
    col1, col2 = st.columns(2)
    
    with col1:
        # 企業名入力（オプション）
        company_name = st.text_input("🏢 企業名（レポートに表示）", placeholder="例: 株式会社ABC", key="company_name")
    
    with col2:
        st.write("")
        st.write("")
        # PDF生成ボタン
        try:
            pdf_buffer = generate_pdf_report(
                axis_scores=axis_scores,
                axis_max_scores=axis_max_scores,
                total_score=total_score,
                max_total_score=max_total_score,
                percentage=percentage,
                rank=rank,
                rank_label=rank_label,
                diagnostic_data=diagnostic_data,
                company_name=company_name if company_name else ""
            )
            
            st.download_button(
                label="📄 診断レポートをダウンロード（PDF）",
                data=pdf_buffer,
                file_name=f"ADAMS_事業推進力診断レポート_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF生成エラー: {str(e)}")
    
    st.write("")
    
    if st.button("🔄 もう一度診断する", use_container_width=True):
        st.session_state.scores = {}
        st.session_state.page = 'intro'
        st.rerun()
    
    st.markdown(f"""
    <div class="copyright">
        © 株式会社ADAMS Management Consulting Office<br>
        本診断ツールの無断転用を禁じます
    </div>
    """, unsafe_allow_html=True)

# メイン処理
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'scores' not in st.session_state:
    st.session_state.scores = {}

if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'questions':
    show_questions()
elif st.session_state.page == 'results':
    show_results()
