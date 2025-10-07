```python
import streamlit as st
import plotly.graph_objects as go
import math

# ---- ページ設定 ----
st.set_page_config(page_title="宅建士試験レーダーチャート", layout="wide")

# ---- 和暦変換 ----
def to_japanese_era(year):
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

# ---- 年度選択（±ボタン） ----
st.sidebar.header("年度設定")
if "year" not in st.session_state:
    st.session_state.year = 2024  # 初期値（令和6年）

col_minus, col_display, col_plus = st.sidebar.columns([1, 3, 1])
with col_minus:
    if st.button("−"):
        st.session_state.year -= 1
with col_display:
    st.markdown(
        f"<div style='text-align:center;font-size:22px;font-weight:bold;'>{to_japanese_era(st.session_state.year)}</div>",
        unsafe_allow_html=True)
with col_plus:
    if st.button("+"):
        st.session_state.year += 1

# ---- 合格ライン設定 ----
st.sidebar.header("合格ライン設定")
passing_score = st.sidebar.number_input("合格ライン（総合点）", min_value=0, max_value=50, value=37, step=1)

# ---- 科目情報 ----
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
targets = [7, 6, 2, 18, 4]

st.sidebar.header("科目ごとの得点入力")
scores = []
for i, (cat, m) in enumerate(zip(categories, max_scores)):
    cols = st.sidebar.columns([1, 2, 1])
    with cols[0]:
        if st.button("−", key=f"minus_{i}"):
            st.session_state[f"score_{i}"] = max(st.session_state.get(f"score_{i}", int(m*0.7)) - 1, 0)
    with cols[1]:
        val = st.session_state.get(f"score_{i}", int(m*0.7))
        st.markdown(f"<div style='text-align:center;font-size:20px;font-weight:bold;color:#333;'>{val}</div>", unsafe_allow_html=True)
        scores.append(val)
    with cols[2]:
        if st.button("+", key=f"plus_{i}"):
            st.session_state[f"score_{i}"] = min(st.session_state.get(f"score_{i}", int(m*0.7)) + 1, m)

# ---- メモ欄 ----
st.sidebar.header("メモ")
memo = st.sidebar.text_area("自由記入欄", height=180, placeholder="気づいたこと・要復習ポイントなど")

# ---- 計算 ----
total_score = sum(scores)
total_max = sum(max_scores)
total_pct = total_score / total_max * 100
scores_pct = [(s / m * 100) if m else 0 for s, m in zip(scores, max_scores)]
targets_pct = [(t / m * 100) if m else 0 for t, m in zip(targets, max_scores)]

# ---- レーダーチャート ----
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()

# 目標得点（黄色）
fig.add_trace(go.Scatterpolar(
    r=r_targets, theta=theta,
    name="目標得点", fill="toself",
    fillcolor="rgba(255,255,0,0.25)",
    line=dict(color="yellow", width=3),
))

# 自分の得点（青）
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta,
    name="自分の得点", fill="toself",
    fillcolor="rgba(65,105,225,0.5)",
    line=dict(color="royalblue", width=3),
))

# ---- 科目名（青字＋白ボックス）＋ 得点表示 ----
for i, (cat, s, m) in enumerate(zip(categories, scores, max_scores)):
    angle = (i / len(categories)) * 2 * math.pi
    x = 0.5 + 0.48 * math.cos(angle)
    y = 0.5 + 0.48 * math.sin(angle)
    fig.add_annotation(
        x=x, y=y, xref="paper", yref="paper",
        text=f"<div style='background-color:rgba(255,255,255,0.9);padding:4px;border-radius:4px;'>"
             f"<span style='color:#005FFF;font-weight:bold;'>{cat}</span><br>"
             f"<span style='font-size:12px;color:#222;'>{s}/{m}</span></div>",
        showarrow=False,
    )

# ---- レイアウト調整 ----
fig.update_layout(
    polar=dict(
        angularaxis=dict(
            rotation=90,
            direction="clockwise",
            tickfont=dict(color="#333", size=12, family="Arial Black")
        ),
        radialaxis=dict(
            range=[0, 100],
            tickvals=[20, 40, 60, 80, 100],
            tickfont=dict(color="#333", size=11),
            gridcolor="lightgray",
            showline=False
        ),
        bgcolor="white"
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Noto Sans JP, sans-serif", size=14),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
    margin=dict(l=40, r=40, t=60, b=60),
)

# ---- iPad操作制限 ----
fig.update_layout(dragmode=False)
fig.update_traces(hoverinfo="none")  # タップ時ポップアップも無効化

# ---- 表示 ----
st.title("📊 宅建士試験 レーダーチャート")
st.subheader(f"{to_japanese_era(st.session_state.year)} の結果")
st.plotly_chart(fig, use_container_width=True)
st.markdown(f"**合計：{total_score}/{total_max}点（{total_pct:.1f}%）**　合格ライン：{passing_score}点")
```
