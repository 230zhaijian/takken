import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="centered")

categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
passing_line = 37

st.title("📊 宅建士試験 レーダーチャート (Plotly)")

cols = st.columns(len(categories))
scores = []
for i, (col, cat, m) in enumerate(zip(cols, categories, max_scores), start=1):
    with col:
        scores.append(int(st.number_input(
            f"{i}. {cat}",
            min_value=0, max_value=m,
            value=int(m * 0.7), step=1, format="%d"
        )))

total_max = sum(max_scores)
total_score = sum(scores)
total_pct = total_score / total_max * 100 if total_max > 0 else 0

scores_pct = [(s / m * 100) if m > 0 else 0 for s, m in zip(scores, max_scores)]
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_max = [100] * len(categories) + [100]

fig = go.Figure()

# 満点
fig.add_trace(go.Scatterpolar(
    r=r_max, theta=theta,
    name="満点", fill="toself",
    line=dict(color="rgba(120,120,120,0.8)"),
    opacity=0.2, hoverinfo="none"
))

# 自分のスコア
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta,
    name="自分のスコア", fill="toself",
    line=dict(color="royalblue", width=2),
    marker=dict(size=6)
))

# 頂点ラベル
texts = [f"{s}/{m}<br>{p:.0f}%" for s, m, p in zip(scores, max_scores, scores_pct)]
texts = texts + [texts[0]]
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta,
    mode="markers+text", text=texts,
    textposition="top center",
    marker=dict(color="royalblue", size=8),
    showlegend=False
))

# レイアウト調整（角度補正・文字位置改善）
fig.update_layout(
    polar=dict(
        angularaxis=dict(rotation=90, direction="clockwise"),
        radialaxis=dict(range=[0, 100], tickvals=[20, 40, 60, 80, 100],
                        ticktext=["20%", "40%", "60%", "80%", "100%"])
    ),
    font=dict(family="Noto Sans JP, sans-serif", size=12),
    margin=dict(l=40, r=40, t=80, b=60),
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
)

# 中央注記（スコア表示）
fig.add_annotation(
    text=f"{total_score}/{total_max}<br>{total_pct:.1f}%",
    x=0.5, y=0.45, xref="paper", yref="paper", showarrow=False,
    font=dict(size=16, color="royalblue", family="Noto Sans JP")
)
fig.add_annotation(
    text=f"合格ライン: {passing_line}点 ({passing_line/total_max*100:.1f}%)",
    x=0.5, y=0.05, xref="paper", yref="paper", showarrow=False,
    font=dict(size=13, color="red", family="Noto Sans JP")
)

st.plotly_chart(fig, use_container_width=True)
