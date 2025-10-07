import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験 年度別分析", layout="wide")

st.title("📊 宅建士試験 年度別分析（表＆レーダーチャート）")

# --- 設定 ---
years = ["令和5年", "令和6年"]
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
target_scores = [7, 6, 2, 18, 4]  # 科目ごとの目標得点

# データ格納用
all_data = []

for year in years:
    st.subheader(f"{year} データ入力")
    passing_line = st.number_input(f"{year} 合格ライン点数", min_value=0, max_value=sum(max_scores), value=37, step=1, key=year)
    
    cols = st.columns(len(categories))
    scores = []
    for col, cat, m in zip(cols, categories, max_scores):
        with col:
            scores.append(int(st.number_input(f"{cat}", min_value=0, max_value=m, value=int(m*0.7), step=1, key=f"{year}_{cat}")))

    total_score = sum(scores)
    total_pct = total_score / sum(max_scores) * 100
    scores_pct = [s/m*100 for s,m in zip(scores,max_scores)]

    all_data.append({
        "年度": year,
        "得点": scores,
        "得点率": scores_pct,
        "合計点": total_score,
        "合計点率": total_pct,
        "合格ライン": passing_line
    })

# --- レイアウト左右分割 ---
col1, col2 = st.columns([1,1])

# --- 左側：表 ---
with col1:
    st.subheader("📋 年度別得点表")
    table_rows = []
    highlight_styles = []
    
    for data in all_data:
        row = {"年度": data["年度"]}
        style = {}
        for cat, s, t in zip(categories, data["得点"], target_scores):
            text = f"{s}/{max_scores[categories.index(cat)]}"
            row[cat] = text
            # 目標未達ならハイライト
            if s < t:
                style[cat] = 'background-color: #FFA07A'  # 明るい赤
        # 合計点
        row["合計点"] = f"{data['合計点']}/{sum(max_scores)}"
        if data["合計点"] < data["合格ライン"]:
            style["合計点"] = 'background-color: #FF6347'
        row["合格ライン"] = f"{data['合格ライン']}/{sum(max_scores)}"
        table_rows.append(row)
        highlight_styles.append(style)
    
    df = pd.DataFrame(table_rows)
    
    # ハイライト適用
    def highlight_cells(val, col_name, row_idx):
        style = highlight_styles[row_idx].get(col_name, '')
        return style
    
    def style_df(df):
        styled = df.style
        for i in range(len(df)):
            for c in df.columns:
                styled = styled.apply(lambda val, col=c, row_idx=i: highlight_cells(val, col, row_idx), axis=None)
        return styled
    
    st.dataframe(style_df(df), use_container_width=True)

# --- 右側：レーダーチャート ---
with col2:
    st.subheader("📈 年度別レーダーチャート")
    theta = categories + [categories[0]]
    fig = go.Figure()
    for data in all_data:
        r = data["得点率"] + [data["得点率"][0]]
        # マーカー色（未達赤、達成青）
        colors = ['red' if s<t else 'royalblue' for s,t in zip(data["得点"], target_scores)]
        r_colors = colors + [colors[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            name=data["年度"],
            line=dict(color='royalblue', width=2),
            marker=dict(color=r_colors, size=10),
            text=[f"{s}/{m}" for s,m in zip(data["得点"], max_scores)],
            textposition='top center'
        ))
        
        # 総合点未達なら線を赤点線
        if data["合計点"] < data["合格ライン"]:
            fig.add_trace(go.Scatterpolar(
                r=r,
                theta=theta,
                fill="toself",
                name=f"{data['年度']} 未達",
                line=dict(color='red', width=2, dash='dash'),
                opacity=0.3
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100], ticktext=["20%","40%","60%","80%","100%"])
        ),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
