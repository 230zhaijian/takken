import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="wide")

# 日本年号変換
def to_japanese_era(year):
    if year <= 1925: return str(year)
    if year <= 1988: return f"昭和{year - 1925}年"
    elif year == 1989: return "平成元年"
    elif 1989 < year <= 2018: return f"平成{year - 1988}年"
    elif year == 2019: return "令和元年"
    else: return f"令和{year - 2018}年"

# -------------------------------
# サイドバー設定
# -------------------------------
st.sidebar.header("年度・設定")
if "year" not in st.session_state: st.session_state.year = 2024
st.sidebar.number_input("年度", min_value=1900, max_value=2100,
                        value=st.session_state.year, step=1, key="year", format="%d")

st.sidebar.markdown("---")
st.sidebar.header("合格ライン設定")
if "passing_score" not in st.session_state: st.session_state.passing_score = 37
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
    if key not in st.session_state: st.session_state[key] = int(m * 0.7)

# -------------------------------
# 科目入力
# -------------------------------
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

# -------------------------------
# 得点計算
# -------------------------------
scores = [st.session_state[f"score_{i}"] for i in range(len(categories))]
passing_score = st.session_state.passing_score
total_score = sum(scores)
total_max = sum(max_scores)
total_pct = total_score / total_max * 100 if total_max else 0.0
scores_pct = [(s / m * 100) if m else 0 for s, m in zip(scores, max_scores)]
targets_pct = [(t / m * 100) if m else 0 for t, m in zip(targets, max_scores)]
total_exceeded = total_score >= passing_score

# -------------------------------
# 合格時背景色と文字色変更
# -------------------------------
if total_exceeded:
    st.markdown("""
    <style>
    .stApp {background-color: #ffe6f0 !important; color: black !important;}
    .sidebar .css-1d391kg {background-color: #ffe6f0 !important;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 得点表作成
# -------------------------------
df_scores = pd.DataFrame({
    "科目": categories + ["合計"],
    "自分の得点": scores + [total_score],
    "目標得点": targets + [passing_score],
    "満点": max_scores + [total_max]
})

def highlight_score(val, col_name, row=None):
    is_total = (row is not None) and (row["科目"]=="合計")
    if col_name == "自分の得点":
        target = row["目標得点"] if row is not None else val
        if val >= target:
            return 'background-color: lightblue; color: black; font-weight: bold; text-align:center; font-size:16px;'
        else:
            return 'background-color: lightcoral; color: black; font-weight: bold; text-align:center; font-size:14px;'
    else:
        return 'text-align:center;'

df_styled = df_scores.style.apply(
    lambda row: [highlight_score(row[col], col, row) for col in df_scores.columns], axis=1
).set_properties(**{'text-align':'center', 'font-weight':'bold', 'font-size':'14px'})

# -------------------------------
# タイトル表示（さらに小さく調整）
# -------------------------------
st.markdown(f"<h4>📊 宅建士試験 得点表（{to_japanese_era(st.session_state.year)}）</h4>", unsafe_allow_html=True)
st.dataframe(df_styled)

# -------------------------------
# 合格表示（小さく調整）
# -------------------------------
if total_exceeded:
    st.markdown("""
    <style>
    @keyframes floatPulse {
        0% {transform: translateY(0px) scale(1);}
        50% {transform: translateY(-5px) scale(1.05);}
        100% {transform: translateY(0px) scale(1);}
    }
    .celebrate {
        font-size:24px;
        font-weight:bold;
        text-align:center;
        background: linear-gradient(90deg, #ff69b4, #ff1493, #ff69b4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: floatPulse 1.5s ease-in-out infinite;
        text-shadow: 1px 1px 5px pink;
    }
    </style>
    <div class="celebrate">🌸 合格！おめでとうございます！🌸</div>
    """, unsafe_allow_html=True)

# -------------------------------
# レーダーチャート作成（幅を抑えて一画面優先）
# -------------------------------
import math
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=r_targets, theta=theta,
    name="目標得点",
    fill="toself", fillcolor="rgba(255,0,0,0.15)",
    line=dict(color="lightcoral", width=3),
    marker=dict(size=8),
    hoverinfo="skip"
))
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta,
    name="自分の得点",
    fill="toself", fillcolor="rgba(65,105,225,0.25)",
    line=dict(color="royalblue", width=3),
    marker=dict(size=10),
    hoverinfo="skip"
))
fig.update_layout(
    polar=dict(
        angularaxis=dict(rotation=90, direction="clockwise",
                         showticklabels=True,
                         tickfont=dict(size=12, color="black", family="Noto Sans JP")),
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100],
                        ticktext=["20%","40%","60%","80%","100%"],
                        tickfont=dict(color="#333", size=12),
                        gridcolor="lightgray"),
        bgcolor="white"
    ),
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Noto Sans JP", size=12),
    showlegend=False,
    margin=dict(l=30,r=30,t=20,b=20),
    width=500, height=400  # 幅と高さを固定して一画面収まり優先
)
fig.update_layout(dragmode=False)
fig.update_traces(hoverinfo="skip")

st.markdown(f"<h4>📊 宅建士試験 レーダーチャート（{to_japanese_era(st.session_state.year)}）</h4>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False, config={"staticPlot": True, "displayModeBar": False})

# -------------------------------
# 合計得点表示
# -------------------------------
st.markdown(f"""
<div style='display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:5px;'>
    <div style='font-size:16px; font-weight:bold; color:royalblue;'>合計：{total_score}/{total_max}点（{total_pct:.1f}%）</div>
</div>
<div style='font-size:14px; font-weight:bold; color:red;'>合格ライン：{passing_score}点</div>
""", unsafe_allow_html=True)
