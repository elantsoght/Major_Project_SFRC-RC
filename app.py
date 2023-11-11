import streamlit as st
import SFRC as sf

st.header("Moment-curvature diagram of a SFRC-RC rectangular cross-section")

st.sidebar.subheader("Input Parameters")
fc = st.sidebar.number_input("Concrete cylinder compressive strenght (MPa)", value=25)
daggmax = st.sidebar.number_input("Maximum aggregate size (mm)", value=16)
fy = st.sidebar.number_input("Yield strenght of mild steel (MPa)", value=400)
As = st.sidebar.number_input("Area of tensile reinforcement (mm2)", value=200)
rhof = st.sidebar.number_input("Fiber bond factor (-)", value=1)
Vf = st.sidebar.number_input("Fiber volume fraction (-)", value=0.0075)
df = st.sidebar.number_input("Fiber diameter (mm)", value=0.55)
lf = st.sidebar.number_input("Fiber length (mm)", value=35)
b = st.sidebar.number_input("Width (mm)", value=120)
d = st.sidebar.number_input("Effective depth (mm)", value=435)
h = st.sidebar.number_input("Height (mm)", value=500)

Mphi = sf.momentcurvatureSFRC(fc,daggmax, fy, As, rhof, Vf, df, lf, b, h, d)

fig = go.Figure(data=[go.Scatter(x=[0,Mphi[1][0],Mphi[1][1], Mphi[1][2] ], y=[0, Mphi[0][0], Mphi[0][1], Mphi[0][2]])])
fig.data[0].marker.color = 'Red'
fig.layout.title.text = "Moment-curvature diagram of SFRC-RC beam"
fig.layout.width = 900
fig.layout.height = 600
fig.layout.xaxis.title = "Curvature (-)"
fig.layout.yaxis.title = "Bending moment (kNm)"
fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
fig.update_layout(
    plot_bgcolor='white',
    xaxis_showgrid=True, xaxis_gridcolor='rgb(245, 245, 245)',
    yaxis_showgrid=True, yaxis_gridcolor='rgb(245, 245, 245)')


st.plotly_chart(fig)




                       
                   
