import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験分析", layout="wide")
st.title("📊 宅建士試験 レーダーチャート＋得点表")

# --- サイドバーにメモ欄 ---
st.sidebar.subheader("📝 メモ")
memo = st.sidebar.text_area("ここにメモを入力できます", height=300)
if memo:
    st.sidebar.info("入力中のメモを保存できます")

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
r_over = [max(0, s-t)/m*100 for s,t,m in zip(scores, target_scores, max_scores)]
r_over += [r_over[0]]
r_under = [min(s, t)/m*100 for s,t,m in zip(scores, target_scores, max_scores)]
r_under += [r_under[0]]

fig = go.Figure()

# 目標得点 緑
fig.add_trace(go.Scatterpolar(
    r=r_target,
    theta=theta,
    fill='toself',
    name='目標得点',
    line=dict(color='green', width=2),
    opacity=0.5
))

# 目標未達分 青
fig.add_trace(go.Scatterpolar(
    r=r_under,
    theta=theta,
    fill='toself',
    name='目標未達分',
    line=dict(color='blue', width=0),
    fillcolor='rgba(0,0,255,0.3)'
))

# 目標超過分 赤
fig.add_trace(go.Scatterpolar(
    r=r_over,
    theta=theta,
    fill='toself',
    name='目標超過分',
    line=dict(color='red', width=0),
    fillcolor='rgba(255,0,0,0.3)'
))

# 自分の得点線
fig.add_trace(go.Scatterpolar(
    r=r_score,
    theta=theta,
    name='自分の得点',
    line=dict(color='royalblue', width=2),
    marker=dict(color='royalblue', size=8)
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100],
                        ticktext=["20%","40%","60%","80%","100%"])
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
    achieved_target_pct = scores[i]/target_scores[i]*100 if target_scores[i]>0 else 100
    achieved_full_pct = scores[i]/max_scores[i]*100 if max_scores[i]>0 else 0
    table_data.append({
        "科目": cat,
        "得点": scores[i],
        "満点": max_scores[i],
        "目標": target_scores[i],
        "目標達成率(%)": achieved_target_pct,
        "満点達成率(%)": achieved_full_pct
    })
table_data.append({
    "科目": "合計",
    "得点": total_score,
    "満点": sum(max_scores),
    "目標": passing_line,
    "目標達成率(%)": total_score/passing_line*100 if passing_line>0 else 100,
    "満点達成率(%)": total_score/sum(max_scores)*100
})

df = pd.DataFrame(table_data)

# ハイライト：目標達成なら緑、未達なら赤
def highlight_target(val, target):
    if isinstance(val, (int, float)):
        if val >= target:
            return 'background-color: #32CD32; color: black; font-weight: bold'
        else:
            return 'background-color: #FF6347; color: white; font-weight: bold'
    return ''

def style_row(row):
    return [highlight_target(row['得点'], row['目標']) if col=='得点' else "" for col in row.index]

df_styled = df.style.apply(style_row, axis=1)
df_styled = df_styled.bar(subset=["目標達成率(%)"], color='#32CD32', vmin=0, vmax=100)
df_styled = df_styled.bar(subset=["満点達成率(%)"], color='#1E90FF', vmin=0, vmax=100)
df_styled.format({"目標達成率(%)": "{:.0f}%", "満点達成率(%)": "{:.0f}%"})

st.dataframe(df_styled, use_container_width=True)
