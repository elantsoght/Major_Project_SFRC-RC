import sections_db
import math
import pandas as pd



def test_aisc_w_sections():
    df = sections_db.aisc_w_sections()
    assert df["Ix"][0] == 12900000000.0


def test_sections_filter():
    df_test_csv = pd.read_csv("eng_module/test_data/test_csv.csv")
    df_test_d_filter = sections_db.sections_filter(df_test_csv, "le", d=500)
    value = df_test_d_filter["Section"][0]
    assert value == 'A'


def test_sort_by_weight():
    test_df = pd.DataFrame(
    data=[
        [10, 30, 20],
        [20, 10, 30],
        [30, 20, 10],
    ],
    columns=["A", "W", "B"],)
    sorted_df = sections_db.sort_by_weight(test_df)
    sorted_df = sorted_df.reset_index()
    sorted_b_col = sorted_df['B'] 
    print(sorted_b_col)
    # The result of this will be a pd.Series
    assert sorted_b_col.equals(pd.Series([30, 10, 20])) 
    # Did a search online to find that there is a .equals method