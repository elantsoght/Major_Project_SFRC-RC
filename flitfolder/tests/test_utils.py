from SFRC.eng_module import utils


def test_str_to_int():
    string_1 = "43"
    string_2 = "-2000"
    string_3 = "324.625"
    string_4 = "COLUMN300X300"

    assert utils.str_to_int(string_1) == 43
    assert utils.str_to_int(string_2) == -2000
    assert utils.str_to_int(string_4) == "COLUMN300X300"


def test_str_to_float():
    string_1 = "43"
    string_2 = "-2000"
    string_3 = "324.625"
    string_4 = "COLUMN300X300"

    assert utils.str_to_float(string_1) == 43.0
    assert utils.str_to_float(string_2) == -2000.0
    assert utils.str_to_float(string_3) == 324.625
    assert utils.str_to_float(string_4) == "COLUMN300X300"
