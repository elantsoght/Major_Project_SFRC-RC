import streamlit as st
import SFRC as sf
import plotly.graph_objects as go
import math
from eng_module import beams


st.header("Design checks of a simply supported SFRC-RC beam")

st.sidebar.subheader("Concrete Materials Parameters")
fc = st.sidebar.number_input("Concrete cylinder compressive strenght (MPa)", value=25)
daggmax = st.sidebar.number_input("Maximum aggregate size (mm)", value=16)
st.sidebar.subheader("Steel Reinforcement Parameters")
fy = st.sidebar.number_input("Yield strenght of mild steel (MPa)", value=400)
As = st.sidebar.number_input("Area of tensile reinforcement (mm2)", value=200)
phibar = st.sidebar.number_input("Reinforcement bar diameter (mm)", value=12)
ns = st.sidebar.number_input("Number of reinforcement bars (-)", value=2)

st.sidebar.subheader("Steel fiber properties")
rhof = st.sidebar.number_input("Fiber bond factor (-)", value=1)
Vf = st.sidebar.number_input("Fiber volume fraction (-)", value=0.0075)
df = st.sidebar.number_input("Fiber diameter (mm)", value=0.55)
lf = st.sidebar.number_input("Fiber length (mm)", value=35)
st.sidebar.subheader("Geometry input")
b = st.sidebar.number_input("Width (mm)", value=120)
d = st.sidebar.number_input("Effective depth (mm)", value=435)
h = st.sidebar.number_input("Height (mm)", value=500)
l = st.sidebar.number_input("Length (mm)", value=2000)
sup1 = st.sidebar.number_input("Support 1 (mm)", value=10)
sup2 = st.sidebar.number_input("Support 2 (mm)", value=1500)
st.sidebar.subheader("Loading input")
load = st.sidebar.number_input("Load (kN)", value=100)
loadloc = st.sidebar.number_input("Position of load (mm)", value=400)
dfactor = st.sidebar.number_input("Dead load factor", value=1.2)
lfactor = st.sidebar.number_input("Live load factor", value=1.6)

tab1, tab2, tab3, tab4 = st.tabs(["Moment-Curvature", "Beam Analysis", "Moment Check", "Shear Check"])

with tab1:
    Mphi = sf.momentcurvatureSFRC(fc,daggmax, fy, As, rhof, Vf, df, lf, b, h, d)

    st.subheader("Results of calculation")
    st.write(f"The cracking moment is {Mphi[0][0]:.2f} kNm and the curvature at cracking is {Mphi[1][0]:.3e}.")
    st.write(f"The yield moment is {Mphi[0][1]:.2f} kNm the curvature at yielding is {Mphi[1][1]:.3e}.")
    st.write(f"The ultimate moment is {Mphi[0][2]:.2f} kNm the curvature at ultimate is {Mphi[1][2]:.3e}.")

    st.subheader("Moment-curvature plot")
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

    st.subheader("References")
    st.write("Mobasher, B., Y. Yao and C. Soranakom (2015). Analytical solutions for flexural design of hybrid steel fiber reinforced concrete beams. Engineering Structures 100: 164-177.")
    st.write("RILEM TC 162-TDF (2003). σ-ε-Design Method.")

with tab2:
    E = 57000/12*math.sqrt(fc)
    Iz = b*h**3/12
    selfweight = 25*b/1000*h/1000
    beam_dict = {'Name': 'SFRC-RC beam',
    'L': l,
    'E': E,
    'Iz': Iz,
    'Iy': 1.0,
    'A': b*h,
    'J': 1,
    'nu': 1,
    'rho': 25,
    'Supports': {sup1: 'P', sup2: 'R'},
    'Loads': [{'Type': 'Point',
    'Direction': 'Fy',
    'Magnitude': -load,
    'Location': loadloc,
    'Case': 'Live'}, {'Type': 'Dist',
    'Direction': 'Fy',
    'Start Magnitude': -selfweight,
    'End Magnitude': -selfweight,
    'Start Location': 0.0,
    'End Location': l,
    'Case': 'Dead'},
    ]}

    beam_model = beams.build_beam(beam_dict)
    beam_model.analyze(check_statics=True)   

    beam_model.Members['SFRC-RC beam'].plot_shear(Direction="Fy", combo_name="Dead", n_points=100)
    beam_model.Members['SFRC-RC beam'].plot_moment(Direction="Mz", combo_name="Dead", n_points=100)
    beam_model.Members['SFRC-RC beam'].plot_shear(Direction="Fy", combo_name="Live", n_points=100)
    beam_model.Members['SFRC-RC beam'].plot_moment(Direction="Mz", combo_name="Live", n_points=100)

    shearres = beams.extract_arrays_all_combos(beam_model, "shear", "Fy", 300)
    shearfactored = 1/1000*dfactor*shearres["Dead"][0][1] + lfactor*shearres["Live"][0][1]
    designshear = max(abs(shearfactored))
    xes = shearres[list(shearres.keys())[0]]
    x_values = xes[0][0]
    momentres = beams.extract_arrays_all_combos(beam_model, "moment", "Mz", 300)
    momentfactored = 1/1000*(1/1000*dfactor*momentres["Dead"][0][1] + lfactor*momentres["Live"][0][1])
    designmoment = max(abs(momentfactored))

    st.subheader("Factored shear diagram")
    fig = go.Figure(data=[go.Scatter(x=x_values, y=shearfactored)])
    fig.data[0].marker.color = 'Red'
    fig.layout.title.text = "Shear diagram of SFRC-RC beam"
    fig.layout.width = 900
    fig.layout.height = 600
    fig.layout.xaxis.title = "x (mm)"
    fig.layout.yaxis.title = "Shear (kN)"
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_showgrid=True, xaxis_gridcolor='rgb(245, 245, 245)',
        yaxis_showgrid=True, yaxis_gridcolor='rgb(245, 245, 245)')

    st.plotly_chart(fig)

    st.subheader("Factored moment diagram")
    fig = go.Figure(data=[go.Scatter(x=x_values, y=momentfactored)])
    fig.data[0].marker.color = 'Red'
    fig.layout.title.text = "Moment diagram of SFRC-RC beam"
    fig.layout.width = 900
    fig.layout.height = 600
    fig.layout.xaxis.title = "x (mm)"
    fig.layout.yaxis.title = "Moment (kNm)"
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightGray', range=[0, None])
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_showgrid=True, xaxis_gridcolor='rgb(245, 245, 245)',
        yaxis_showgrid=True, yaxis_gridcolor='rgb(245, 245, 245)')

    st.plotly_chart(fig)

    st.write("These graphs are built with PyNite.")

                       
    with tab3:   
        st.subheader("Results of Bending Moment Check")
        if designmoment <= Mphi[0][2]:
            st.write(f"The ultimate moment is {Mphi[0][2]:.2f} kNm and the factored moment demand is {designmoment:.2f} kNm.")
            st.write("The demand is less than or equal to the capacity. The beam fulfills the requirements for flexure.")
        elif designmoment > Mphi[0][2]:
            st.write(f"The ultimate moment is {Mphi[0][2]:.2f} kNm and the factored moment demand is {designmoment:.2f} kNm.")
            st.write("The demand is larger than the capacity. The beam does not fulfill the requirements for flexure.")
        else:
            st.write("Sorry, something has gone wrong here!")


        #st.write(f"The design shear is {designshear} kN")








