import math
import plotly.express as px
import plotly.graph_objects as go

def momentcurvatureSFRC (fc: float, daggmax: float, 
                         fy: int, As: int, 
                         rhof: float, Vf: float, df: float, lf: float,
                         b: int, d: int, h: int) -> list:
    """
    This function calculates the values of the moment and curvature at cracking,
    yielding, and the ultimate of a SFRC-RC hybrid cross-section.
    The expressions are taken from the following references:
    Mobasher, B., Y. Yao and C. Soranakom (2015). 
    "Analytical solutions for flexural design of hybrid steel fiber reinforced concrete beams." 
    Engineering Structures 100: 164-177.
    and
    RILEM TC 162-TDF (2003). 
    "σ-ε-Design Method." 
    Materials and Structures 36(8): 560-567.
    """

    #General properties
    Ec = 57000/12 * fc**(1/2) #MPa, Young's modulus of the concrete
    ecy= fc / Ec
    ecu=0.0035
    Es=200000 #MPa
    rho=As/(b*d)
    rhog=As/(b*h)
    #angle=min(max(math.atan(d/a),0.436),0.7854)
    esy=fy/Es

    # Properties of the steel fibers
    F = Vf*lf/df*rhof
    sigmat=0.772*(lf/df)*Vf*rhof
    Eten=9500*(fc)**(1/3)

    # Determination of tensile strenght of SFRC
    if fc < 20.5:
        ffctmfl=3.7
    elif fc <25.5:
        ffctmfl=4.3
    elif fc < 30.5:
        ffctmfl = 4.8
    elif fc < 35.5:
        ffctmfl = 5.3
    elif fc < 40.5:
        ffctmfl = 5.8
    elif fc < 45.5:
        ffctmfl = 6.3
    else:
        ffctmfl = 6.8
    sigma1=0.7*ffctmfl*(1.6-d/1000)

    #Determination of size effect factor
    if h/10 > 12.5:
        if h/10 < 60:
            kh=1-0.6*(h/10-12.5)/47.5
        elif h/10 >= 60:
            kh=0.4
    else:
        kh = 1

    #Input for M-phi calculations
    fcuf = fc/0.82
    fr4=0.63*math.sqrt(fcuf)+0.288*F*math.sqrt(fcuf)+0.052*F
    sigma2=0.45*kh*ffctmfl
    sigma3=0.37*fr4*kh
    sigmap=1/2*(sigma2+sigma3)

    ecr=sigma1/Eten

    lambdacu=ecu/ecr
    mu = sigmap/sigma1
    om=ecy/ecr
    alpha=d/h
    kappa=esy/ecr

    #cracking moment and curvature
    Mcr=1/6*b*d**2*Eten*ecr/1000000 #kNm
    k1=(18*rhog*alpha+1)/(18*rhog+2)
    n=Es/Eten
    elr1=k1*h/(h-k1*h)*ecr
    lambdar1=elr1/ecr
    gamma=(1/(2*k1)*(k1-1)**2+rho*n/k1*(alpha-k1))/(1/2*k1)
    phicr = 2*ecr/h

    #yielding moment and curvature
    B1y=om**2+2*mu*(om+1)-1
    B2y=mu-9*rhog*om
    B3y=9*rhog*(rhog*9*om**2-2*mu*om)+mu**2
    B4y=2*om*(9*rhog*kappa+mu)
    k21y=om/B1y*(B2y+math.sqrt(B3y+2*alpha*rhog*n*B1y))
    C5y=2*om**3+3*mu*(om**2-1)+2
    C6y=6*om**2*(9*om*rhog-mu)
    C7y=3*om**2*(mu-36*rhog*alpha*om)
    C8y=54*rhog*alpha**2*om**3
    C9y=-6*om**2*(9*rhog*kappa+mu)
    C10y=3*om**2*(18*rhog*alpha*kappa+mu)
    M21=1/(om**2*k21y)*(C5y*k21y**3+C6y*k21y**2+C7y*k21y+C8y)*Mcr
    phi21 = om/(2*k21y)
    k22y=B4y/B1y
    M22=1/om**2*(C5y*k22y**2+C9y*k22y+C10y)*Mcr
    phi22 = om/(2*k22y)
    es2=(alpha-k22y)/k22y*om*ecr
    if es2 > esy:
        My=M22
        k2y=k22y
        phiy = phi22*phicr
    else: 
        My=M21
        k2y=k21y
        phiy = phi21*phicr

    #ultimate moment and curvature
    B2u=mu-9*rhog*lambdacu
    B3u=9*rhog*(rhog*9*lambdacu**2-2*mu*lambdacu)
    B4u=2*lambdacu*(9*rhog*kappa+mu)
    B5u=20*lambdacu-101+2*mu*(lambdacu+1)
    C6u=6*lambdacu**2*(9*lambdacu*rhog-mu)
    C7u=3*lambdacu**2*(mu-36*rhog*alpha*lambdacu)
    C8u=54*rhog*alpha**2*lambdacu**3
    C9u=-6*lambdacu**2*(9*rhog*kappa+mu)
    C10u=3*lambdacu**2*(18*rhog*alpha*kappa+mu)
    C11u=30*lambdacu**2+3*mu*(lambdacu**2-1)-998
    k31=lambdacu/B5u*(B2u+math.sqrt(B3u+2*alpha*rhog*n*B5u))
    k32=B4u/B5u
    M31=1/(lambdacu**2*k31)*(C11u*k31**3+C6u*k31**2+C7u*k31+C8u)*Mcr
    phi31 = lambdacu/(2*k31)
    M32=1/lambdacu**2*(C11u*k32**2+C9u*k32+C10u)*Mcr
    phi32=lambdacu/(2*k32)
    es3=(alpha-k32)/k32*lambdacu*ecr

    if es3 > esy:
        Mult=M32
        k3u=k32
        phiult = phi32*phicr
    else: 
        Mult=M31
        k3u=k31
        phiult = phi31*phicr

    return [[Mcr, My, Mult],[phicr, phiy, phiult]]