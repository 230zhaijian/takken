import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験分析", layout="wide")
st.title("📊 宅建士試験 レーダーチャート＋得点表")

# 年度入力
year = st.text_input("年度", "令和5年")

# 科目と得点設定
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
target_scores = [7, 6, 2, 18, 4]

st.subheader("科目ごとの得点を入力")
cols = st.columns(len(categories))
scores = []
for i, (col, cat, m) in enumerate(zip(cols, categories, max_scores)):
    with col:
        scores.append(int(st.number_input(f"{cat}", min_value=0, max_value=m, value=int(m*0.7), step=1)))

# 合格ライン
passing_line = st.number_input("合格ライン点数", min_value=0, max_value=sum(max_scores), value=37, step=1)

# --- レーダーチャート ---
st.subheader(f"📈 {year} レーダーチャート")
theta = categories + [categories[0]]
r_score = [s/m*100 for s,m in zip(scores, max_scores)]
r_score += [r_score[0]]
r_target = [t/m*100 for t,m in zip(target_scores, max_scores)]
r_target += [r_target[0]]

fig = go.Figure()
# 目標得点：薄いイエロー
fig.add_trace(go.Scatterpolar(
    r=r_target,
    theta=theta,
    fill='toself',
    name='目標得点',
    line=dict(color='gold', width=1),
    opacity=0.3
))
# 自分の得点
fig.add_trace(go.Scatterpolar(
    r=r_score,
    theta=theta,
    fill='toself',
    name='自分の得点',
    line=dict(color='royalblue', width=3),
    marker=dict(color='royalblue', size=10)
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100], ticktext=["20%","40%","60%","80%","100%"])
    ),
    showlegend=True,
    width=700,
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- 得点表 ---
st.subheader(f"📋 {year} 得点表")
total_score = sum(scores)
table_data = []
for i, cat in enumerate(categories):
    achieved_target_pct = min(scores[i]/target_scores[i]*100, 100) if target_scores[i]>0 else 100
    achieved_full_pct = scores[i]/max_scores[i]*100 if max_scores[i]>0 else 0
    table_data.append({
        "科目": cat,
        "得点": scores[i],
        "満点": max_scores[i],
        "目標": target_scores[i],
        "目標達成率": achieved_target_pct,
        "満点達成率": achieved_full_pct
    })
table_data.append({
    "科目": "合計",
    "得点": total_score,
    "満点": sum(max_scores),
    "目標": passing_line,
    "目標達成率": min(total_score/passing_line*100, 100) if passing_line>0 else 100,
    "満点達成率": total_score/sum(max_scores)*100
})

df = pd.DataFrame(table_data)

# ハイライト：目標未達は赤背景＋白文字
def highlight_target(val, target):
    try:
        if val < target:
            return 'background-color: #FF6347; color: white; font-weight: bold'
    except:
        pass
    return ''

# スタイル設定
def style_row(row):
    styles = []
    for col in df.columns:
        if col == "得点":
            styles.append(highlight_target(row[col], row["目標"]))
        else:
            styles.append("")
    return styles

df_styled = df.style.apply(style_row, axis=1)

# 達成率にバーを追加
df_styled = df_styled.bar(subset=["目標達成率"], color='#FFD700', vmin=0, vmax=100)
df_styled = df_styled.bar(subset=["満点達成率"], color='#87CEFA', vmin=0, vmax=100)

st.dataframe(df_styled, use_container_width=True)
