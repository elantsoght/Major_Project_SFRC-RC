import math

import SFRC


def test_momentcurvatureSFRC():
    outcome = SFRC.momentcurvatureSFRC(
        fc=28,
        daggmax=16,
        fy=400,
        As=226,
        rhof=1,
        Vf=0.005,
        df=0.55,
        lf=35,
        b=120,
        d=435,
        h=500,
    )
    Myield = outcome[0][1]
    assert math.isclose(Myield, 45.86742947733356)


def test_shearcap():
    shearcap = SFRC.shearcap(
        fc=28,
        daggmax=16,
        fy=400,
        As=226,
        phibar=12,
        ns=2,
        rhof=1,
        Vf=0.005,
        df=0.55,
        lf=35,
        b=120,
        d=435,
        h=500,
        M=48.16,
        V=81.08,
    )
    VCSDT = shearcap[0]

    assert math.isclose(VCSDT, 32.08540659227059)
