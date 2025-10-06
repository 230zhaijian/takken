import streamlit as st
import plotly.graph_objects as go

# ページ設定

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="centered")

# Google Fonts をクライアント読み込み（日本語をブラウザでレンダリング）

st.markdown(
'<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">',
unsafe_allow_html=True
)

st.title("📊 宅建士試験 レーダーチャート")

# カテゴリと満点

categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
passing_line = 37

# サイドバーで入力（リスト内包で書くことでインデントミスを回避）

scores = [
int(st.sidebar.number_input(f"{i+1}. {cat} (満点 {m})", min_value=0, max_value=m, value=int(m*0.7), step=1, format="%d"))
for i, (cat, m) in enumerate(zip(categories, max_scores))
]

total_max = sum(max_scores)
total_score = sum(scores)
total_pct = total_score / total_max * 100

st.sidebar.markdown(f"### 合計: {total_score} / {total_max} 点 ({total_pct:.1f}%)")
if total_score >= passing_line:
st.sidebar.success("✅ 合格ライン突破！")
else:
st.sidebar.er
