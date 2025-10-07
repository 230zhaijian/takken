import streamlit as st
import plotly.graph_objects as go
import math

# ---- ページ設定 ----

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="wide")

# ---- 和暦変換 ----

def to_japanese_era(year):
# 簡易和暦表示（必要ならここを拡張して切替日を変更できるようにする）
if year <= 1925:
return f"{year}"
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

# ---- サイドバー：年度（±）・合格ライン・科目得点・メモ ----

st.sidebar.header("年度・設定")

# 年度の初期化

if "year" not in st.session_state:
st.session_state.year = 2024  # 初期値（変更可）

col_minus, col_display, col_plus = st.sidebar.columns([1, 3, 1])
with col_minus:
if st.button("−", key="year_minus"):
st.session_state.year -= 1
with col_display:
st.markdown(
f"<div style='text-align:center;font-size:18px;font-weight:bold'>{to_japanese_era(st.session_state.year)}</div>",
unsafe_allow_html=True
)
with col_plus:
if st.button("+", key="year_plus"):
st.session_state.year += 1

# 合格ライン（サイドバー上部）

st.sidebar.markdown("---")
st.sidebar.header("合格ライン設定")
if "passing_score" not in st.session_state:
st.session_state.passing_score = 37
st.session_state.passing_score = st.sidebar.number_input(
"合格ライン（総合点）", min_value=0, max_value=100, value=st.session_state.passing_score, step=1
)

st.sidebar.markdown("---")

# 科目情報（固定）

categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]

# 例の目標値（変更可）

targets = [7, 6, 2, 18, 4]

# セッションステートに科目スコアの初期値を入れておく

for i, m in enumerate(max_scores):
key = f"score_{i}"
if key not in st.session_state:
st.session_state[key] = int(m * 0.7)

st.sidebar.header("科目ごとの得点入力（±で調整）")

# コンパクトに＋/−と中央表示（iPadで押しやすい）

for i, (cat, m) in enumerate(zip(categories, max_scores)):
cols = st.sidebar.columns([1, 2, 1])
with cols[0]:
if st.button("−", key=f"minus_{i}"):
st.session_state[f"score_{i}"] = max(0, st.session_state[f"score_{i}"] - 1)
with cols[1]:
val = st.session_state[f"score_{i}"]
st.markdown(
f"<div style='text-align:center; font-weight:bold; font-size:18px; background-color:white; padding:4px; border-radius:6px'>{cat}: {val} / {m}</div>",
unsafe_allow_html=True
)
with cols[2]:
if st.button("+", key=f"plus_{i}"):
st.session_state[f"score_{i}"] = min(st.session_state[f"score_{i}"] + 1, m)

st.sidebar.markdown("---")
st.sidebar.header("メモ")
memo = st.sidebar.text_area("自由記入欄（学習メモ）", height=200, placeholder="気づいた点、復習ポイントなどを記入")

# ---- 本体側計算 ----

scores = [st.session_state[f"score_{i}"] for i in range(len(categories))]
passing_score = st.session_state.passing_score

total_score = sum(scores)
total_max = sum(max_scores)
total_pct = total_score / total_max * 100 if total_max else 0

scores_pct = [(s / m * 100) if m else 0 for s, m in zip(scores, max_scores)]
targets_pct = [(t / m * 100) if m else 0 for t, m in zip(targets, max_scores)]

# ---- レーダーチャート作成 ----

theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()

# 目標得点（黄色の薄い塗り）

fig.add_trace(go.Scatterpolar(
r=r_targets, theta=theta,
name="目標得点",
fill="toself",
fillcolor="rgba(255,255,0,0.25)",
line=dict(color="gold", width=2),
marker=dict(size=6)
))

# 自分の得点（青）

fig.add_trace(go.Scatterpolar(
r=r_scores, theta=theta,
name="自分の得点",
fill="toself",
fillcolor="rgba(65,105,225,0.35)",
line=dict(color="royalblue", width=3),
marker=dict(size=8)
))

# 注釈（科目名＋自分の得点）を外周に白背景ボックスで配置（青字）

n = len(categories)
for i, (cat, s, m) in enumerate(zip(categories, scores, max_scores)):
# angle: top = 90deg, clockwise increment
angle_deg = 90 - (i * 360 / n)
angle_rad = math.radians(angle_deg)
radius = 0.53  # 少し外側。0.5が中心基準
x = 0.5 + radius * math.cos(angle_rad)
y = 0.5 + radius * math.sin(angle_rad)
label_text = f"{cat}<br><span style='font-size:12px;color:#222;'>{s}/{m}</span>"
# 背景白ボックスを使って常に読みやすく
fig.add_annotation(
x=x, y=y, xref="paper", yref="paper",
text=label_text,
showarrow=False,
align="center",
bgcolor="rgba(255,255,255,0.95)",
bordercolor="rgba(0,0,0,0.06)",
borderpad=4,
font=dict(color="#005FFF", size=13, family="Noto Sans JP")
)

# レイアウト調整（白背景固定・軸の色など）

fig.update_layout(
polar=dict(
angularaxis=dict(
rotation=90,
direction="clockwise",
# デフォルト軸ラベルは使わない（外側注釈で表示）
showticklabels=False,
),
radialaxis=dict(
range=[0, 100],
tickvals=[20, 40, 60, 80, 100],
ticktext=["20%", "40%", "60%", "80%", "100%"],
tickfont=dict(color="#333", size=11),
gridcolor="lightgray",
),
bgcolor="white"
),
paper_bgcolor="white",
plot_bgcolor="white",
font=dict(family="Noto Sans JP", size=13),
showlegend=True,
legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
margin=dict(l=40, r=40, t=80, b=40),
)

# 明示的に操作無効化（Streamlit側でも最終的に設定）

# note: st.plotly_chart config below ensures staticPlot and disables modebar

fig.update_layout(dragmode=False)

# ---- 表示 ----

st.title("📊 宅建士試験 レーダーチャート")
st.subheader(f"{to_japanese_era(st.session_state.year)} の結果")

# staticPlot=True でズームやスワイプ等を完全に無効化（iPadの誤タッチ対策）

st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True, "displayModeBar": False})

st.markdown(f"**合計：{total_score}/{total_max}点（{total_pct:.1f}%）**　合格ライン：{passing_score}点") </writing>

説明（短く）

* `SyntaxError: invalid syntax` の原因はファイルに Markdown の ``` が含まれていたためです。
* 上のコードは **バッククォート等の余分な記号を除去**し、動作する Python スクリプトとして整えたものです。
* さらに：科目ラベルを外側に **白いボックス** で描画し、文字色を青に固定、グラフ操作は `staticPlot=True` で無効化しています（iPadで誤タッチして傾く問題を防止）。

---

もしよければ次に行います（選べます）：

A. このまま「科目別の得点表（%表示・色付きバー・ソート機能）」を下に追加するコードを出す
B. 「和暦の切替日時（昭和→平成、平成→令和等）を UI で変更できる設定」を追加する
C. 上のままデプロイ手順（GitHub→Streamlit Cloud）について簡潔手順を出す

どれを先に進めますか？必要であれば一緒にコードをさらに微調整します。
