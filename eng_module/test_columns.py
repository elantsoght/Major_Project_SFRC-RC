import columns
import math

def test_column_critical_buckling_load():
    column1 = columns.Column(
        h=4000,
        E=200e3,
        A=2000,
        Ix=400e3,
        Iy=200e3,
        kx=1.0,
        ky=2.0
    )
    # For option 2: if you use the same inputs/outputs for your function test
    # you can save a bit of effort...
    assert math.isclose(column1.critical_buckling_load('x'), 49348.02201)
    assert math.isclose(column1.critical_buckling_load('y'), 6168.502750)


def test_column_radius_of_gyration():
    column1 = columns.Column(
        h=4000,
        E=200e3,
        A=2000,
        Ix=400e3,
        Iy=200e3,
        kx=1.0,
        ky=2.0
    )
    assert math.isclose(column1.radius_of_gyration('x'),14.1421356, abs_tol = 1e-3)
    assert math.isclose(column1.radius_of_gyration('y'),10)


def test_factored_crushing_load():
    column1 = columns.SteelColumn(
        h=4000,
        E=200e3,
        A=2000,
        Ix=400e3,
        Iy=200e3,
        kx=1.0,
        ky=2.0,
        fy = 200,
        phic = 1
    )
    assert math.isclose(column1.factored_crushing_load(),400)


def test_factored_compressive_resistance():
    SC01 = columns.SteelColumn(h=3750, A=16500, Ix=308e6, Iy=100e6, kx=1, ky=1, E=200e3, tag='W310x129', fy=345, phic=0.9)
    assert math.isclose(SC01.factored_compressive_resistance(), 4323.430827669878, abs_tol = 1e-3)


def test_csv_record_to_steelcolumn():
    record = ["C00","26380.0","3360.0","767000000.0","361000000.0","250","200000.0","0.7","1.0","101430.0","449880.0"]
    SC01 = columns.SteelColumn(h=3360.0, E=200000.0, A=26380.0, Ix=767000000.0, Iy=361000000.0, kx=0.7, ky=1.0, fy=250.0, phic=0.9, tag='C00')
    assert columns.csv_record_to_steelcolumn(record, phic=0.9) == SC01


def test_calculate_factored_csv_load():
    record = ["C00","26380.0","3360.0","767000000.0","361000000.0","250","200000.0","0.7","1.0","101430.0","449880.0"]
    assert columns.calculate_factored_csv_load(record) == 841524


def test_run_all_columns():
    input = columns.run_all_columns('eng_module/test_data/test_column_data.csv')
    assert math.isclose(input[0].demand_capacity_ratio,0.140320420199655, abs_tol = 1e-3)
    assert math.isclose(input[1].demand_capacity_ratio,0.38045493534695746, abs_tol = 1e-3)



