import streamlit as st
import numpy as np
import plotly.graph_objs as go

# Load Google font (client-side) so Japanese labels render in the browser without uploading a font file
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# Configuration
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
pass_line = 37

st.title("📊 宅建士試験 レーダーチャート (Plotly版)")

# Input scores
st.info("各科目の得点を入力してください（右端の矢印で数値を変えられます）")
scores = []
cols = st.columns(len(categories))
for i, (col, cat, m) in enumerate(zip(cols, categories, max_scores)):
    with col:
        scores.append(int(st.number_input(f"{i+1}. {cat}", min_value=0, max_value=m, value=0, step=1, format="%d")))

# Prepare data (percentages)
total_max = sum(max_scores)
total_score = sum(scores)
total_pct = total_score / total_max * 100

scores_pct = [s / m * 100 if m > 0 else 0 for s, m in zip(scores, max_scores)]
# Close the polygon
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_max = [100] * len(categories) + [100]

# Build Plotly figure
fig = go.Figure()

fig.add_trace(go.Scatterpolar(r=r_max, theta=theta, name='満点', fill='toself',
                              line=dict(color='gray'), hoverinfo='none', opacity=0.15))
fig.add_trace(go.Scatterpolar(r=r_scores, theta=theta, name='自分のスコア', fill='toself',
                              line=dict(color='royalblue', width=2), marker=dict(size=6)))

# Add markers + labels for each vertex (show score and percent)
texts = [f"{s}/{m}<br>{p:.0f}%" for s, m, p in zip(scores, max_scores, scores_pct)]
texts = texts + [texts[0]]
fig.add_trace(go.Scatterpolar(r=r_scores, theta=theta, mode='markers+text', text=texts,
                              textposition='top center', showlegend=False,
                              marker=dict(color='royalblue', size=8)))

# Layout: use the Google font, radial ticks shown as percentages
fig.update_layout(
    polar=dict(
        radialaxis=dict(range=[0, 100], tickvals=[20, 40, 60, 80, 100],
                        ticktext=['20%', '40%', '60%', '80%', '100%'])
    ),
    font=dict(family='Noto Sans JP, sans-serif', size=12),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
    margin=dict(l=40, r=40, t=80, b=40)
)

# Center annotation for totals and passline note
fig.add_annotation(text=f"{total_score}/{total_max}<br>{total_pct:.1f}%",
                   x=0.5, y=0.52, xref='paper', yref='paper', showarrow=False,
                   font=dict(size=14, color='royalblue', family='Noto Sans JP'))
fig.add_annotation(text=f"合格ライン: {pass_line}点 ({pass_line/total_max*100:.1f}%)",
                   x=0.5, y=0.02, xref='paper', yref='paper', showarrow=False,
                   font=dict(size=12, color='red', family='Noto Sans JP'))

# Show figure
st.plotly_chart(fig, use_container_width=True)

# Note about font: If your environment blocks Google Fonts, the labels may fallback to another font.
st.caption('フォントは Google Fonts の「Noto Sans JP」を使用します。ネットワーク条件により読み込みできない場合、日本語フォントが代替されることがあります。')
