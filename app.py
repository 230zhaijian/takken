import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="wide")

# 日本年号変換
def to_japanese_era(year):
    if year <= 1925: return str(year)
    if year <= 1988: return f"昭和{year - 1925}年"
    elif year == 1989: return "平成元年"
    elif 1989 < year <= 2018: return f"平成{year - 1988}年"
    elif year == 2019: return "令和元年"
    else: return f"令和{year - 2018}年"

# サイドバー設定
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

# 科目入力（スピナー式）
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

# 得点計算
scores = [st.session_state[f"score_{i}"] for i in range(len(categories))]
passing_score = st.session_state.passing_score
total_score = sum(scores)
total_max = sum(max_scores)
total_pct = total_score / total_max * 100 if total_max else 0.0
scores_pct = [(s / m * 100) if m else 0 for s, m in zip(scores, max_scores)]
targets_pct = [(t / m * 100) if m else 0 for t, m in zip(targets, max_scores)]
total_exceeded = total_score >= passing_score

# 背景色切替・文字色
if total_exceeded:
    st.markdown("""
    <style>
    .stApp {background-color: #ffe6f0 !important; color: black !important;}
    .css-1v3fvcr, .css-1d391kg {color: black !important;}
    </style>
    """, unsafe_allow_html=True)

# 得点表
st.subheader("得点表")
df_scores = pd.DataFrame({
    "科目": categories,
    "自分の得点": scores,
    "目標得点": targets,
    "満点": max_scores
})

def highlight_cell(val, target):
    color = "lightblue" if val >= target else "lightcoral"
    return f'background-color: {color}; font-weight:bold; text-align:center;'

df_styled = df_scores.style.format({
    "自分の得点":"{:.0f}",
    "目標得点":"{:.0f}",
    "満点":"{:.0f}"
}).apply(lambda row: [highlight_cell(row['自分の得点'], row['目標得点']) if col=="自分の得点" else 'text-align:center;' for col in row.index], axis=1)\
  .set_properties(**{'text-align':'center', 'font-weight':'bold', 'font-size':'14px'})

st.dataframe(df_styled, height=250)

# レーダーチャート
theta = categories + [categories[0]]
r_scores = scores_pct + [scores_pct[0]]
r_targets = targets_pct + [targets_pct[0]]

fig = go.Figure()
# 目標得点線（薄赤）
fig.add_trace(go.Scatterpolar(
    r=r_targets, theta=theta, name="目標得点",
    fill="toself", fillcolor="rgba(255,0,0,0.15)",
    line=dict(color="lightcoral", width=3),
    marker=dict(size=8),
    hoverinfo="skip"
))
# 自分の得点線（青）
fig.add_trace(go.Scatterpolar(
    r=r_scores, theta=theta, name="自分の得点",
    fill="toself", fillcolor="rgba(65,105,225,0.25)",
    line=dict(color="royalblue", width=3),
    marker=dict(size=10),
    hoverinfo="skip"
))

fig.update_layout(
    polar=dict(
        angularaxis=dict(rotation=90, direction="clockwise",
                         showticklabels=True,
                         tickfont=dict(size=14, color="black", family="Noto Sans JP"),
                         tickcolor="black"),
        radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100],
                        ticktext=["20%","40%","60%","80%","100%"],
                        tickfont=dict(color="#333", size=12),
                        gridcolor="lightgray"),
        bgcolor="white"
    ),
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Noto Sans JP", size=13),
    showlegend=False,
    margin=dict(l=40,r=40,t=100,b=40)
)
fig.update_layout(dragmode=False)
fig.update_traces(hoverinfo="skip")

# タイトル・凡例
st.markdown(f"<h1 style='display:inline-block'>📊 宅建士試験 レーダーチャート</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='display:inline-block; margin-left:10px'>{to_japanese_era(st.session_state.year)} の結果</h3>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; gap:20px; margin-top:10px; margin-bottom:10px;">
<div style="color:royalblue; font-weight:bold;">🔹 自分の得点</div>
<div style="color:lightcoral; font-weight:bold;">🔴 目標得点</div>
</div>
""", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True, "displayModeBar": False})

# はなまるアニメーション
st.markdown("""
<style>
@keyframes poprotate {0% {transform: scale(1) rotate(0deg); color:#FFD700;} 25% {transform: scale(1.3) rotate(20deg); color:#FFB347;} 50% {transform: scale(1) rotate(0deg); color:#FFD700;} 75% {transform: scale(1.2) rotate(-20deg); color:#FFB347;} 100% {transform: scale(1) rotate(0deg); color:#FFD700;}}
.pop-emoji {display:inline-block; animation: poprotate 1.5s infinite;}
</style>
""", unsafe_allow_html=True)

# 合計・合格ライン表示
st.markdown(f"""
<div style='display:flex; align-items:center; gap:15px;'>
    <div style='font-size:22px; font-weight:bold; color:royalblue;'>合計：{total_score}/{total_max}点（{total_pct:.1f}%）</div>
    {"<div class='pop-emoji' style='font-size:40px;'>🌸</div>" if total_exceeded else ""}
</div>
<div style='font-size:18px; font-weight:bold; color:red;'>合格ライン：{passing_score}点</div>
""", unsafe_allow_html=True)

# 花びらアニメーション（全画面）
if total_exceeded:
    petals_html = """
    <canvas id="petals" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999;"></canvas>
    <script>
    const canvas=document.getElementById('petals');
    function resizeCanvas(){canvas.width=window.innerWidth; canvas.height=window.innerHeight;}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    const ctx=canvas.getContext('2d');
    const petals=[];
    const colors=['#FFC0CB','#FFB6C1','#FF69B4','#FF1493','#FFD700'];
    const shapes=['circle','heart','star'];
    function drawShape(p){
        ctx.fillStyle=p.color;
        ctx.save();
        ctx.translate(p.x,p.y);
        ctx.rotate(p.rotation);
        switch(p.shape){
            case 'circle': ctx.beginPath(); ctx.arc(0,0,p.r,0,Math.PI*2); ctx.fill(); break;
            case 'heart':
                ctx.beginPath();
                const x=0,y=0;
                ctx.moveTo(x,y);
                ctx.bezierCurveTo(x,y-p.r,x-p.r,y-p.r,x-p.r,y);
                ctx.bezierCurveTo(x-p.r,y+p.r,x,y+p.r,x,y+p.r/2);
                ctx.bezierCurveTo(x,y+p.r,x+p.r,y+p.r,x+p.r,y);
                ctx.bezierCurveTo(x+p.r,y-p.r,x,y-p.r,x,y);
                ctx.fill();
                break;
            case 'star':
                ctx.beginPath();
                for(let i=0;i<5;i++){
                    ctx.lineTo(Math.cos((18+i*72)/180*Math.PI)*p.r,-Math.sin((18+i*72)/180*Math.PI)*p.r);
                    ctx.lineTo(Math.cos((54+i*72)/180*Math.PI)*(p.r/2),-Math.sin((54+i*72)/180*Math.PI)*(p.r/2));
                }
                ctx.closePath();
                ctx.fill();
                break;
        }
        ctx.restore();
    }
    for(let i=0;i<50;i++){
        petals.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*8+3,d:Math.random()*1+0.5,color:colors[Math.floor(Math.random()*colors.length)],tilt:Math.random()*0.5-0.25,rotation:Math.random()*2*Math.PI,rotationSpeed:Math.random()*0.02-0.01,shape:shapes[Math.floor(Math.random()*shapes.length)]});
    }
    function draw(){
        ctx.clearRect(0,0,canvas.width,canvas.height);
        for(let i=0;i<petals.length;i++){
            let p=petals[i];
            drawShape(p);
            p.y+=p.d;
            p.x+=Math.sin(p.tilt);
            p.rotation+=p.rotationSpeed;
            if(p.y>canvas.height){p.y=0;p.x=Math.random()*canvas.width;}
            if(p.x>canvas.width){p.x=0;}
            if(p.x<0){p.x=canvas.width;}
        }
        requestAnimationFrame(draw);
    }
    draw();
    </script>
    """
    html(petals_html, height=0)
