import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験分析", layout="wide")
st.title("📊 宅建士試験 レーダーチャート＋得点表")

# サイドバーにメモ
st.sidebar.subheader("📝 メモ")
memo = st.sidebar.text_area("ここにメモを入力できます", height=200)

# 年度入力
year = st.text_input("年度", "令和5年")

# 科目設定
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
target_scores = [7, 6, 2, 18, 4]

# セッションステートで得点管理
if 'scores' not in st.session_state:
    st.session_state.scores = [int(m*0.7) for m in max_scores]

# 科目ごとの得点入力
st.subheader("科目ごとの得点を入力（＋/−で調整）")
for i, cat in enumerate(categories):
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button(f"{cat} −", key=f"minus_{i}"):
            st.session_state.scores[i] = max(0, st.session_state.scores[i]-1)
    with col2:
        st.markdown(f"<div style='text-align:center; font-weight:bold'>{st.session_state.scores[i]} / {max_scores[i]}</div>", unsafe_allow_html=True)
    with col3:
        if st.button(f"{cat} ＋", key=f"plus_{i}"):
            st.session_state.scores[i] = min(max_scores[i], st.session_state.scores[i]+1)

scores = st.session_state.scores
passing_line = st.number_input("合格ライン点数", min_value=0, max_value=sum(max_scores), value=37, step=1)

# --- レーダーチャート ---
theta = categories + [categories[0]]
r_score = [s/m*100 for s,m in zip(scores, max_scores)] + [scores[0]/max_scores[0]*100]
r_target = [t/m*100 for t,m in zip(target_scores, max_scores)] + [target_scores[0]/max_scores[0]*100]

# 科目ラベル色・サイズ
label_colors = []
label_sizes = []
for s, t in zip(scores, target_scores):
    if s < t:
        label_colors.append('red')
        label_sizes.append(12)
    elif s == t:
        label_colors.append('blue')
        label_sizes.append(12)
    else:
        label_colors.append('blue')
        label_sizes.append(14)

# レーダーチャート作成
fig = go.Figure()

# 自分の得点
fig.add_trace(go.Scatterpolar(
    r=r_score,
    theta=theta,
    name='自分の得点',
    line=dict(color='royalblue', width=3),
    marker=dict(color='royalblue', size=8),
    text=[f"{s}/{m}" for s,m in zip(scores, max_scores)],
    textposition='top center',
    mode='lines+markers+text'
))

# 目標得点
fig.add_trace(go.Scatterpolar(
    r=r_target,
    theta=theta,
    name='目標得点',
    line=dict(color='green', width=2),
    fill='toself',
    opacity=0.3,
    text=[f"{t}/{m}" for t,m in zip(target_scores, max_scores)],
    textposition='bottom center',
    mode='lines+markers+text'
))

# レーダーチャートレイアウト
fig.update_layout(
    polar=dict(
        bgcolor="#FFFFFF",  # 白背景で視認性確保
        angularaxis=dict(
            tickmode='array',
            tickvals=list(range(len(categories))),
            ticktext=categories,
            tickfont=dict(color='black', size=12),
            rotation=90,
            direction='clockwise'
        ),
        radialaxis=dict(
            range=[0,100],
            tickvals=[20,40,60,80,100],
            ticktext=["20%","40%","60%","80%","100%"],
            tickfont=dict(color='black')
        )
    ),
    width=650,
    height=400,
    showlegend=True
)

# 科目名を外側に注釈
for i, cat in enumerate(categories):
    fig.add_annotation(
        x=i,
        y=110,
        text=f"<b>{cat}</b>",
        showarrow=False,
        font=dict(color=label_colors[i], size=label_sizes[i])
    )

# 横並びで表示するため列に分割
col_chart, col_table = st.columns([1,1])
with col_chart:
    st.plotly_chart(fig, use_container_width=True)
    
# --- 得点表 ---
with col_table:
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
