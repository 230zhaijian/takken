# --- レーダーチャート部分（改善版） ---
import plotly.graph_objects as go

# レーダーチャート作成
fig = go.Figure()

# 自分の得点
fig.add_trace(go.Scatterpolar(
    r=r_scores,
    theta=subjects,
    fill='toself',
    name='自分の得点',
    line=dict(color='blue', width=3),
    mode='markers+lines+text',
    text=[f"{v}点" for v in r_scores],
    textposition="top center",
    textfont=dict(color="white", size=12, family="Arial Black")
))

# 目標得点
fig.add_trace(go.Scatterpolar(
    r=r_target,
    theta=subjects,
    fill='toself',
    name='目標得点',
    line=dict(color='green', dash='solid', width=3),
    opacity=0.4,
))

# --- 見やすくするためのレイアウト調整 ---
fig.update_layout(
    polar=dict(
        bgcolor='white',  # 背景を明示的に白固定
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickfont=dict(color='black', size=10),
            gridcolor='lightgray',
        ),
        angularaxis=dict(
            tickfont=dict(
                color='dodgerblue',  # 見やすい青
                size=15,
                family='Arial Black'
            ),
            rotation=90,  # ラベルを見やすく回転
            direction="clockwise",
            layer="above traces"  # ラベルをグラフ線より前面に
        ),
    ),
    font=dict(color='black'),
    margin=dict(l=60, r=60, t=80, b=60),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5
    )
)

# --- スクロール・ズーム・回転操作の無効化 ---
st.plotly_chart(fig, use_container_width=True, config={
    "staticPlot": True,  # グラフ操作を完全に無効化
    "displayModeBar": False  # 右上のメニューバーも非表示
})
