"""
ADAMS 事業推進力診断ツール - PDF診断レポート生成モジュール
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# ハイブリッドフォント設定: 英数字=Arial、日本語=Noto Sans CJK
try:
    # 日本語フォントの登録
    pdfmetrics.registerFont(TTFont('NotoSans', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('NotoSans-Bold', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', subfontIndex=0))
    FONT_NAME = 'NotoSans'
    FONT_BOLD = 'NotoSans-Bold'
except Exception as e:
    # フォールバック: 標準フォントを使用
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    FONT_NAME = 'HeiseiMin-W3'
    FONT_BOLD = 'HeiseiKakuGo-W5'

# ADAMSブランドカラー
ADAMS_NAVY = colors.HexColor('#243666')
ADAMS_ACCENT = colors.HexColor('#4a90e2')
ADAMS_GOLD = colors.HexColor('#d4af37')

def generate_pdf_report(axis_scores, axis_max_scores, total_score, max_total_score, 
                       percentage, rank, rank_label, diagnostic_data, company_name=""):
    """
    診断結果からPDFレポートを生成
    
    Args:
        axis_scores: 各軸のスコア辞書
        axis_max_scores: 各軸の最大スコア辞書
        total_score: 総合スコア
        max_total_score: 総合最大スコア
        percentage: 達成率
        rank: ランク（A/B/C/D）
        rank_label: ランクラベル
        diagnostic_data: 診断データ辞書
        company_name: 企業名（オプション）
    
    Returns:
        BytesIO: PDF バッファ
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # ストーリー（コンテンツ）を格納するリスト
    story = []
    
    # スタイルシート
    styles = getSampleStyleSheet()
    
    # カスタムスタイルの定義
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=ADAMS_NAVY,
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=30
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        fontName=FONT_BOLD,
        fontSize=18,
        textColor=ADAMS_NAVY,
        spaceAfter=12,
        spaceBefore=12,
        leading=24
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        fontName=FONT_BOLD,
        fontSize=14,
        textColor=ADAMS_NAVY,
        spaceAfter=10,
        spaceBefore=10,
        leading=18
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        fontName=FONT_NAME,
        fontSize=10,
        leading=16,
        spaceAfter=6
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        fontName=FONT_NAME,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_RIGHT,
        leading=12
    )
    
    # ===== 表紙 =====
    story.append(Spacer(1, 30*mm))
    
    story.append(Paragraph("事業推進力診断レポート", title_style))
    story.append(Spacer(1, 10*mm))
    
    if company_name:
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        story.append(Paragraph(f"{company_name} 様", company_style))
        story.append(Spacer(1, 5*mm))
    
    # 診断日時
    diag_date = datetime.now().strftime('%Y年%m月%d日')
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=12,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"診断日時: {diag_date}", date_style))
    
    story.append(Spacer(1, 40*mm))
    
    # 著作権表示
    copyright_text = "© 株式会社ADAMS Management Consulting Office<br/>本診断レポートの無断転用を禁じます"
    story.append(Paragraph(copyright_text, small_style))
    
    story.append(PageBreak())
    
    # ===== 総合評価ページ =====
    story.append(Paragraph("1. 総合評価", heading1_style))
    story.append(Spacer(1, 5*mm))
    
    # 総合評価テーブル
    rank_color = ADAMS_GOLD if rank == "A" else ADAMS_ACCENT if rank == "B" else colors.orange if rank == "C" else colors.red
    
    # 総合評価テーブル（セル結合レイアウト）
    eval_data = [
        ['総合ランク', f'{rank}', rank_label],
        ['総合スコア', f'{total_score} / {max_total_score} 点', ''],
        ['達成率', f'{percentage:.1f}%', '']
    ]
    
    eval_table = Table(eval_data, colWidths=[40*mm, 40*mm, 70*mm])
    eval_table.setStyle(TableStyle([
        # フォント設定（Arial）
        ('FONT', (0, 0), (-1, -1), FONT_NAME, 11),
        ('FONT', (0, 0), (0, -1), FONT_BOLD, 11),
        ('FONT', (1, 0), (2, 0), FONT_BOLD, 20),  # 1行目のランク部分を大きく
        
        # セル結合
        ('SPAN', (1, 1), (2, 1)),  # 2行目: スコア部分を結合
        ('SPAN', (1, 2), (2, 2)),  # 3行目: 達成率部分を結合
        
        # 背景色
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff9e6')),  # 薄い黄色
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff9e6')),
        
        # テキスト色
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        
        # 罫線
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # 配置
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),      # 左列は左揃え
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),     # 1行目のランク（A）は中央揃え
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),       # 1行目の「優良レベル」は左揃え
        ('ALIGN', (1, 1), (2, 2), 'CENTER'),     # 2-3行目の結合セルは中央揃え
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # パディング
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(eval_table)
    story.append(Spacer(1, 10*mm))
    
    # ランク基準
    story.append(Paragraph("【ランク基準】", heading2_style))
    rank_criteria = """
    • <b>Aランク（85%以上）</b>: 優良レベル - 事業推進力が非常に高い状態<br/>
    • <b>Bランク（70-84%）</b>: 標準レベル - 事業推進の基盤がしっかりしている<br/>
    • <b>Cランク（55-69%）</b>: 要改善レベル - 改善の余地が大きい状態<br/>
    • <b>Dランク（55%未満）</b>: 危機レベル - 早急な改善が必要な状態
    """
    story.append(Paragraph(rank_criteria, body_style))
    story.append(Spacer(1, 10*mm))
    
    # 総合診断コメント
    story.append(Paragraph("【総合診断コメント】", heading2_style))
    
    if percentage >= 85:
        comment = "素晴らしい結果です。事業推進力が非常に高い状態を維持されています。現状を維持しつつ、さらなる成長に向けた新たな挑戦を検討される段階です。"
    elif percentage >= 70:
        comment = "良好な状態です。事業推進の基盤がしっかりしています。弱点となっている軸を強化することで、さらなる飛躍が期待できます。"
    elif percentage >= 55:
        comment = "改善の余地が大きい状態です。優先改善課題から着手し、段階的に事業推進力を高めていくことをお勧めします。"
    else:
        comment = "早急な改善が必要な状態です。まずは優先度の高い課題から集中的に取り組むことが重要です。"
    
    story.append(Paragraph(comment, body_style))
    
    story.append(PageBreak())
    
    # ===== 6軸バランス分析と各軸詳細スコア（1ページに統合） =====
    story.append(Paragraph("2. 6軸バランス分析と詳細スコア", heading1_style))
    story.append(Spacer(1, 3*mm))
    
    # レーダーチャートを生成
    labels = list(axis_scores.keys())
    scores = [axis_scores[label] / axis_max_scores[label] * 4 for label in labels]
    
    # Matplotlibでレーダーチャートを生成
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles_plot = angles + angles[:1]
    
    ax.plot(angles_plot, scores_plot, 'o-', linewidth=2, color='#243666', markersize=8)
    ax.fill(angles_plot, scores_plot, alpha=0.25, color='#4a90e2')
    
    # 英語ラベルを使用
    english_labels = [diagnostic_data[label]["english_label"] for label in labels]
    ax.set_thetagrids(np.degrees(angles), english_labels, fontsize=9, weight='bold')
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['1', '2', '3', '4'], fontsize=8)
    ax.grid(True, linewidth=0.8, alpha=0.3)
    
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # 画像をバッファに保存
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    plt.close()
    
    # PDFに画像を追加（小さめ）
    radar_img = Image(img_buffer, width=80*mm, height=80*mm)
    story.append(radar_img)
    story.append(Spacer(1, 3*mm))
    
    # 凡例（簡潔化）
    legend_text = """
    <b>【凡例】</b> Vision=ビジョン / Planning=計画管理 / Organization=組織 / Time Mgmt=時間管理 / KPI=数値管理 / Profitability=収益性
    """
    story.append(Paragraph(legend_text, body_style))
    story.append(Spacer(1, 5*mm))
    
    # 各軸のスコアテーブル（コンパクト化）
    story.append(Paragraph("【各軸詳細スコア】", heading2_style))
    score_data = [['診断軸', 'スコア', '達成率', '評価']]
    
    for axis_name, score in axis_scores.items():
        icon = diagnostic_data[axis_name].get('icon', '📌')
        max_score = axis_max_scores[axis_name]
        pct = (score / max_score) * 100 if max_score > 0 else 0
        
        if pct >= 75:
            evaluation = "良好"
        elif pct >= 50:
            evaluation = "普通"
        else:
            evaluation = "要改善"
        
        score_data.append([
            f"{icon} {axis_name}",
            f"{score} / {max_score}",
            f"{pct:.1f}%",
            evaluation
        ])
    
    score_table = Table(score_data, colWidths=[60*mm, 35*mm, 30*mm, 25*mm])
    score_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), FONT_BOLD, 10),
        ('FONT', (0, 1), (-1, -1), FONT_NAME, 9),
        ('BACKGROUND', (0, 0), (-1, 0), ADAMS_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(score_table)
    
    story.append(PageBreak())
    
    # ===== 優先改善課題 TOP3ページ =====
    story.append(Paragraph("3. 優先改善課題 TOP3", heading1_style))
    story.append(Spacer(1, 5*mm))
    
    sorted_axes = sorted(axis_scores.items(), 
                        key=lambda x: x[1] / axis_max_scores[x[0]] if axis_max_scores[x[0]] > 0 else 0)
    
    medals = ["🥇", "🥈", "🥉"]
    positions = ["第1位", "第2位", "第3位"]
    
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
        
        story.append(Paragraph(f"{medals[i]} {positions[i]}: {icon} {axis_name}", heading2_style))
        story.append(Paragraph(f"現在のスコア: {score}/{max_score} 点 ({pct:.1f}%)", body_style))
        story.append(Spacer(1, 3*mm))
        
        story.append(Paragraph("【取り組むと良いテーマ（ヒント）】", body_style))
        for theme in themes:
            story.append(Paragraph(f"  {theme}", body_style))
        
        story.append(Spacer(1, 5*mm))
    
    story.append(PageBreak())
    
    # ===== まとめページ =====
    story.append(Paragraph("4. まとめと次のステップ", heading1_style))
    story.append(Spacer(1, 5*mm))
    
    summary_text = """
    本診断レポートでは、貴社の事業推進力を6つの軸から総合的に評価いたしました。<br/>
    <br/>
    診断結果を踏まえ、以下のステップで改善を進めることをお勧めします:<br/>
    <br/>
    <b>Step 1:</b> 優先改善課題TOP3から、最も取り組みやすい課題を1つ選定<br/>
    <b>Step 2:</b> 選定した課題について、具体的な改善アクションプランを策定<br/>
    <b>Step 3:</b> 3ヶ月を目安に改善活動を実施<br/>
    <b>Step 4:</b> 改善状況を確認するため、再診断を実施<br/>
    <br/>
    事業推進力の向上は、一朝一夕には実現できませんが、着実に取り組むことで<br/>
    必ず成果につながります。本診断レポートが、貴社のさらなる発展の一助となれば幸いです。
    """
    story.append(Paragraph(summary_text, body_style))
    
    story.append(Spacer(1, 20*mm))
    
    # フッター
    footer_text = """
    <br/><br/>
    本診断レポートに関するご質問、改善支援のご相談は、<br/>
    株式会社ADAMS Management Consulting Officeまでお気軽にお問い合わせください。<br/>
    <br/>
    © 株式会社ADAMS Management Consulting Office<br/>
    本診断レポートの無断転用を禁じます
    """
    story.append(Paragraph(footer_text, small_style))
    
    # PDFを生成
    doc.build(story)
    
    buffer.seek(0)
    return buffer
