import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="wide")

def to_japanese_era(year):
    if year <= 1925:
        return str(year)
    if year <= 1988:
        return f"昭和{year - 1925}年"
    elif year == 1989:
        return "平成元年"
    elif 1989 < year <= 2018:
        return f"平成{year - 1988}年"
    elif year == 2019:
        return "令和元年"
    else:
        return f"令和{year - 2018}年"

# --- サイドバー ---
st.sidebar.header("年度・設定")
if "year" not in st.session_state:
    st.session_state.year = 2024

if st.sidebar.button("−", key="year_minus"):
    st.session_state.year -= 1
st.sidebar.markdown(f"<div style='text-align:center;font-size:18px;font-weight:bold'>{to_japanese_era(st.session_state.year)}</div>", unsafe_allow_html=True)
if st.sidebar.button("+", key="year_plus"):
    st.session_state.year += 1

st.sidebar.markdown("---")
st.sidebar.header("合格ライン設定")
if "passing_score" not in st.session_state:
    st.session_state.passing_score = 37
st.session_state.passing_score = st.sidebar.number_input(
    "合格ライン（総合点）", min_value=0, max_value=100,
    value=st.session_state.passing_score, step=1
)

st.sidebar.markdown("---")
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
targets = [7, 6, 2, 18, 4]

for i, m in enumerate(max_scores):
    key = f"score_{i}"
    if key not in st.session_state:
        st.session_state[key] = int(m * 0.7)

# --- 科目入力（縦並び） ---
st.sidebar.header("科目ごとの得点入力（±で調整）")
for i, (cat, m) in enumerate(zip(categories, max_scores)):
    st.sidebar.markdown(f"**{cat} ({st.session_state[f'score_{i}']}/{m})**")
    if st.sidebar.button(f"＋ {cat}", key=f"plus_{i}"):
        st.session_state[f"score_{i}"] = min(st.session_state[f"score_{i}"] + 1, m)
    if st.sidebar.button(f"− {cat}", key=f"minus_{i}"):
        st.session_state[f"score_{i}"] = max(st.session_state[f"score_{i}"] - 1, 0)

st.sidebar.markdown("---")
st.sidebar.header("メモ")
memo = st.sidebar.text_area("自由記入欄（学習メモ）", height=200, placeholder="気づいた点、復習ポイントなど")

# --- 計算 ---
scores = [st.session_state[f"score_{i}"] for i in range(len(categories))]
passing_score = st.session_state.passing_score
total_score = sum(scores)
total_max = sum(max_scores)
total_pct = total_score / total_max * 100 if total_max else 0.0
scores_pct = [(s / m * 100) if m else 0 for s, m in zip(scores, max_scores)]
targets_pct = [(t / m * 100) if m else 0 for t, m in zip(targets, max_scores)]

# --- 得点表 ---
st.subheader("得点表")
df_scores = pd.DataFrame({
    "科目": categories,
    "自分の得点": scores,
    "目標得点": targets,
    "満点": max_scores
})

def color_score(val, target):
    return 'color: royalblue; font-weight:bold;' if val >= target else 'color: red; font-weight:bold;'

df_styled = df_scores.style.format({
    "自分の得点":"{:.0f}",
    "目標得点":"{:.0f}",
    "満点":"{:.0f}"
}).apply(lambda x: [color_score(v, t) if col=="自分の得点" else "" 
                    for v,t,col in zip(x, targets, x.index)], axis=1)

st.dataframe(df_styled, height=250)

# --- レーダーチャート ---
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=r_targets, theta=theta, name="目標得点", fill="toself",
    fillcolor="rgba(255,255,0,0.25)", line=dict(color="gold", width=3),
    marker=dict(size=8), hoverinfo="skip"
))
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta, name="自分の得点", fill="toself",
    fillcolor="rgba(65,105,225,0.35)", line=dict(color="royalblue", width=3),
    marker=dict(size=10), hoverinfo="skip"
))

# --- ラベル（外側にずらして表示） ---
n = len(categories)
for i, (cat, s, m) in enumerate(zip(categories, scores, max_scores)):
    angle_deg = 90 - (i*360/n)
    angle_rad = math.radians(angle_deg)
    radius = 0.65  # 外側にずらす
    x = 0.5 + radius * math.cos(angle_rad)
    y = 0.5 + radius * math.sin(angle_rad)
    label_color = "royalblue" if s >= targets[i] else "red"
    label_text = f"{cat}<br><span style='font-size:14px;color:{label_color};'>{s}/{m}</span>"
    fig.add_annotation(
        x=x, y=y, xref="paper", yref="paper", text=label_text,
        showarrow=False, align="center",
        font=dict(color=label_color, size=14, family="Noto Sans JP"),
        bgcolor="rgba(255,255,255,0.95)", bordercolor="rgba(0,0,0,0.06)", borderpad=4
    )

fig.update_layout(
    polar=dict(
        angularaxis=dict(rotation=90, direction="clockwise", showticklabels=False),
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100],
                        ticktext=["20%","40%","60%","80%","100%"],
                        tickfont=dict(color="#333", size=12),
                        gridcolor="lightgray"),
        bgcolor="white"
    ),
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Noto Sans JP", size=13),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=40,r=40,t=80,b=40)
)
fig.update_layout(dragmode=False)
fig.update_traces(hoverinfo="skip")

st.title("📊 宅建士試験 レーダーチャート")
st.subheader(f"{to_japanese_era(st.session_state.year)} の結果")
st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True, "displayModeBar": False})
st.markdown(f"**合計：{total_score}/{total_max}点（{total_pct:.1f}%）**　合格ライン：{passing_score}点")
