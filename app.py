import streamlit as st
import plotly.graph_objects as go

# ページ設定

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="centered")

# タイトル

st.title("📊 宅建士試験レーダーチャート")

# 項目と満点

categories = ["権利関係 (14)", "法令上の制限 (8)", "税その他 (3)", "宅建業法 (20)", "免除科目 (5)"]
max_scores = [14, 8, 3, 20, 5]

# 入力フォーム

st.sidebar.header("スコア入力")
scores = []
for i, (cat, max_s) in enumerate(zip(categories, max_scores), start=1):
score = st.sidebar.number_input(f"{cat}", min_value=0, max_value=max_s, value=int(max_s*0.7))
scores.append(score)

# 合計点と合格ライン

total_score = sum(scores)わかりにくいので、
passing_line = 37

st.sidebar.markdown(f"### 合計: {total_score} 点")
if total_score >= passing_line:
st.sidebar.success("✅ 合格ライン突破！")
else:
st.sidebar.error("❌ 合格ライン未達")

# レーダーチャート作成

fig = go.Figure()

# 満点データ

fig.add_trace(go.Scatterpolar(
r=max_scores + [max_scores[0]],
theta=categories + [categories[0]],
fill='toself',
name='満点',
line=dict(color="rgba(0,100,200,0.7)", width=2)
))

# 自分のスコア

fig.add_trace(go.Scatterpolar(
r=scores + [scores[0]],
theta=categories + [categories[0]],
fill='toself',
name='自分のスコア',
line=dict(color="rgba(200,50,50,0.7)", width=2)
))

fig.update_layout(
polar=dict(
radialaxis=dict(visible=True, range=[0, max(max_scores)])
),
showlegend=True
)

# グラフ表示

st.plotly_chart(fig, use_container_width=True)
