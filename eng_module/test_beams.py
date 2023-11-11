import beams
import math




def test_calc_shear_modulus():

    E1 = 200000 # MPa
    nu1 = 0.3

    E2 = 3645 # ksi 
    nu2 = 0.2

    assert beams.calc_shear_modulus(nu1, E1) == 76923.07692307692
    assert beams.calc_shear_modulus(nu2, E2) == 1518.75


def test_euler_buckling_load():

    l1 = 5300 # mm
    E1 = 200000 # MPa
    I1 = 632e6 # mm**4
    k1 = 1.0

    l2 = 212 # inch
    E2 = 3645 # ks2i ("ksi" == "kips per square inch")
    I2 = 5125.4 # inch**4
    k2 = 2.0

    assert beams.euler_buckling_load(l1, E1, I1, k1) == 44411463.02234584
    assert beams.euler_buckling_load(l2, E2, I2, k2) == 1025.6361727834453


def test_beam_reactions_ss_cant():

    w1 = 50 # kN/m (which is the same as N/mm)
    a1 = 2350 # mm
    b1 = 4500 # mm

    w2 = 19 # lbs/inch == 228 lbs/ft
    a2 = 96 # inch
    b2 = 96 # inch2

    assert beams.beam_reactions_ss_cant(w1,b1,a1) == (260680.55555555556, 81819.44444444445)
    assert beams.beam_reactions_ss_cant(w2,b2,a2) == (3648.0, 0.0)


def test_fe_model_ss_cant():

    beam_model1 = beams.fe_model_ss_cant(-10, 10, 10)
    beam_model1.analyze_linear()
    n0 = beam_model1.Nodes['N0'].RxnFY['Combo 1']
    n1 = beam_model1.Nodes['N1'].RxnFY['Combo 1']
    assert math.isclose(n0, 0, abs_tol = 1e-6)
    assert math.isclose(n1,200, abs_tol = 1e-6)


def test_read_beam_file():

    beam1_data = beams.read_beam_file('eng_module/test_data/beam_1.txt')
    beam4_data = beams.read_beam_file('eng_module/test_data/beam_4.txt')

    assert beam1_data == [['4800', ' 200000', ' 437000000'], ['0', ' 3000'], ['-10']]
    assert beam4_data == [['8000', ' 28000', ' 756e6'],['0', ' 7000'],['-52']]

def test_separate_lines():
    
    example_1_data = "cat, bat, hat\ntroll, scroll, mole"
    assert beams.separate_lines(example_1_data) == ["cat, bat, hat", "troll, scroll, mole"]


def test_extract_data():

    beam_1_lines = ['4800, 200000, 437000000', '0, 3000', '10, 2000']
    assert beams.extract_data(beam_1_lines, 1) == ['0', '3000']
    assert beams.extract_data(beam_1_lines, 0) == ['4800', '200000', '437000000']


def test_get_spans():

    beam_length1 = 10
    cant_support_loc1 = 7
    assert beams.get_spans(beam_length1, cant_support_loc1) == (7, 3)
    
    beam_length2 = 4000
    cant_support_loc2 = 2500
    assert beams.get_spans(beam_length2, cant_support_loc2) == (2500, 1500)


def test_load_beam_model():

    model5 = beams.load_beam_model('eng_module/test_data/beam_5.txt')
    model5.analyze_linear(check_statics=True)
    res5 = model5.Members['My new beam'].min_deflection(Direction="dy",combo_name="Live")
    assert math.isclose(res5, -68.12405, abs_tol = 1e-2)


def test_separate_data():

    input = ['Roof beam', '4800, 19200, 1000000000', '0, 3000', '100, 500, 4800', '200, 3600, 4800']
    
    output = beams.separate_data(input)

    assert output == [['Roof beam'], ['4800', '19200', '1000000000'], ['0', '3000'], ['100', '500', '4800'], ['200', '3600', '4800']]


def test_convert_to_numeric():
    input = [['4800', '19200', '1000000000'],
 ['0', '3000'],
 ['100', '500', '4800'],
 ['200', '3600', '4800']]
    
    assert beams.convert_to_numeric(input) == [[4800.0, 19200.0, 1000000000.0],
 [0.0, 3000.0],
 [100.0, 500.0, 4800.0],
 [200.0, 3600.0, 4800.0]]
    

def test_get_structured_beam_data():
    input = [['Balcony transfer'],
     ['4800', '24500', '1200000000', '1', '1'],
     ['1000:P', '3800:R'],
     ['POINT:Fy', '-10000', '4800', 'case:Live'],
     ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']]

    assert beams.get_structured_beam_data(input) == {
    'Name': 'Balcony transfer',
    'L': 4800.0,
    'E': 24500.0,
    'Iz': 1200000000.0,
    'Iy': 1.0,
    'A': 1.0,
    'J': 1,
    'nu': 1,
    'rho': 1,
    'Supports': {1000.0: 'P', 3800.0: 'R'},
    'Loads': [
        {'Type': 'Point', 'Direction': 'Fy', 'Magnitude': -10000.0, 'Location': 4800.0, 'Case': 'Live'},
        {
            'Type': 'Dist',
            'Direction': 'Fy',
            'Start Magnitude': 30.0,
            'End Magnitude': 30.0,
            'Start Location': 0.0,
            'End Location': 4800.0,
            'Case': 'Dead'
        }]}
    

def test_get_node_locations():

    beam_length1 = 10000.0
    supports1 = [1000.0, 4000.0, 8000.0]
    beam_length2 = 210.0
    supports2 = [0.0, 210.0]
    assert beams.get_node_locations(supports1, beam_length1) == {'N0': 0.0, 'N1': 1000.0, 'N2': 4000.0, 'N3': 8000.0, 'N4': 10000.0} 
    assert beams.get_node_locations(supports2, beam_length2) == {'N0': 0.0, 'N1': 210.0}

def test_parse_supports():

    supports = ['1000:P', '3800:R', '4800:F', '8000:R']
    assert beams.parse_supports(supports) == {1000.0: 'P', 3800.0: 'R', 4800.0: 'F', 8000.0: 'R'}


def test_parse_loads():

    input = [
    ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
    ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']
    ]
    assert beams.parse_loads(input) == [
        {'Type': 'Point', 'Direction': 'Fy', 'Magnitude': -10000.0, 'Location': 4800.0, 'Case': 'Live'},
        {'Type': 'Dist',
        'Direction': 'Fy',
        'Start Magnitude': 30.0,
        'End Magnitude': 30.0,
        'Start Location': 0.0,
        'End Location': 4800.0,
        'Case': 'Dead'}]
    

def test_parse_beam_attributes():

    input1 = [20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3]
    input2 = [4800, 24500, 1200000000, 10]
    assert beams.parse_beam_attributes(input1) == {"L": 20e3, "E": 200e3, "Iz": 6480e6, "Iy": 390e6, "A": 43900, "J": 11900e3, "nu": 0.3, "rho": 1}
    assert beams.parse_beam_attributes(input2) == {"L": 4800, "E": 24500, "Iz": 1200000000, "Iy": 10, "A": 1, "J": 1, "nu": 1, "rho": 1}
