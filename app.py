import streamlit as st
import plotly.graph_objects as go
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
st.sidebar.number_input("年度", min_value=1900, max_value=2100,
                        value=st.session_state.year, step=1, key="year", format="%d")

st.sidebar.markdown("---")
st.sidebar.header("合格ライン設定")
if "passing_score" not in st.session_state:
    st.session_state.passing_score = 37
st.session_state.passing_score = st.sidebar.number_input(
    "合格ライン（総合点）", min_value=0, max_value=100,
    value=st.session_state.passing_score, step=1, format="%d"
)

st.sidebar.markdown("---")
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
targets = [7, 6, 2, 18, 4]

for i, m in enumerate(max_scores):
    key = f"score_{i}"
    if key not in st.session_state:
        st.session_state[key] = int(m * 0.7)

# --- 科目入力（スピナー式） ---
st.sidebar.header("科目ごとの得点入力")
for i, (cat, m) in enumerate(zip(categories, max_scores)):
    val = st.sidebar.number_input(
        cat, min_value=0, max_value=m,
        value=st.session_state[f"score_{i}"],
        step=1, format="%d", key=f"input_{i}"
    )
    st.session_state[f"score_{i}"] = val

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

def highlight_cell(val, target):
    color = "lightblue" if val >= target else "lightcoral"
    return f'background-color: {color}; font-weight:bold; text-align:center;'

df_styled = df_scores.style.format({
    "自分の得点":"{:.0f}",
    "目標得点":"{:.0f}",
    "満点":"{:.0f}"
}).apply(lambda row: [highlight_cell(row['自分の得点'], row['目標得点']) if col=="自分の得点" else 'text-align:center;' for col in row.index], axis=1)\
  .set_properties(**{'text-align':'center'})

st.dataframe(df_styled, height=250)

# --- レーダーチャート ---
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()
# 目標得点線（薄赤）
fig.add_trace(go.Scatterpolar(
    r=r_targets, theta=theta, name="目標得点",
    fill="toself", fillcolor="rgba(255,0,0,0.15)",
    line=dict(color="lightcoral", width=3),
    marker=dict(size=8),
    hoverinfo="skip"
))
# 自分の得点線（青）
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta, name="自分の得点",
    fill="toself", fillcolor="rgba(65,105,225,0.25)",
    line=dict(color="royalblue", width=3),
    marker=dict(size=10),
    hoverinfo="skip"
))

fig.update_layout(
    polar=dict(
        angularaxis=dict(rotation=90, direction="clockwise",
                         showticklabels=True,
                         tickfont=dict(size=14, color="black", family="Noto Sans JP"),
                         tickcolor="black"),
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100],
                        ticktext=["20%","40%","60%","80%","100%"],
                        tickfont=dict(color="#333", size=12),
                        gridcolor="lightgray"),
        bgcolor="white"
    ),
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Noto Sans JP", size=13),
    showlegend=True,
    legend=dict(
        orientation="v", yanchor="top", y=1, xanchor="right", x=1.05,
        title="凡例", font=dict(size=12)
    ),
    margin=dict(l=40,r=80,t=80,b=40)
)
fig.update_layout(dragmode=False)
fig.update_traces(hoverinfo="skip")

st.title("📊 宅建士試験 レーダーチャート")
st.subheader(f"{to_japanese_era(st.session_state.year)} の結果")
st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True, "displayModeBar": False})

st.markdown(f"**合計：{total_score}/{total_max}点（{total_pct:.1f}%）**　合格ライン：{passing_score}点")
