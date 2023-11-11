import pandas as pd
from typing import Optional
from eng_module import columns
import numpy as np
import json



def aisc_w_sections ()-> pd.DataFrame:
    """
    The function takes no parameters. 
    It takes the CSV file of the sections and 
    returns a dataframe with the unscaled data
    """
    filepath = __file__
    filename = filepath.replace("sections_db.py", "aisc_db_si.csv")
    df = pd.read_csv(filename)
    df["Ix"] = df["Ix"] * 1E6
    df["Zx"] = df["Zx"] * 1E3
    df["Sx"] = df["Sx"] * 1E3
    df["Iy"] = df["Iy"] * 1E6
    df["Zy"] = df["Zy"] * 1E3
    df["Sy"] = df["Sy"] * 1E3
    df["J"] = df["J"] * 1E3
    df["Cw"] = df["Cw"] * 1E9
    return df


def sections_filter(
        df: pd.DataFrame, 
        operator: str, 
        **kwargs) -> pd.DataFrame:
    
    """
    This function takes the dataframe and returns
    a new dataframe that is filtered given the input.
    The operator can be 
    "ge": Greater than or equal to
    "le": Less than or equal to
    """
    sub_df = df.copy()
    for k, v in kwargs.items():
        if operator == "ge":
            mask1 = sub_df[k] >= v
            df_new = sub_df.loc[mask1]
        elif operator == "le":
            mask2 = sub_df[k] <= v
            df_new = sub_df.loc[mask2]
        else:
            print("The operator can only be ge or le")

    if df_new.empty:
        print("The returned dataframe is empty. Check the input")
    else:
        print("New dataframe ok")

    return df_new

def sort_by_weight(df: pd.DataFrame, 
        ascending: Optional[str] = None) -> pd.DataFrame:
    """
    This function takes the sections DataFrame 
    and returns a new DataFrame sorted by the linear 
    weight of the sections in the table. 
    The optional keyword argument 
    allows the resulting DataFrame to be sorted in 
    ascending or descending order. 
    The column of the weights is hard-coded into 
    the function.
    """
    if ascending == True:
        sorted_df = df.sort_values("W", ascending=True)
    elif ascending == False:
        sorted_df = df.sort_values("W", ascending=False)
    else:
        sorted_df = df.sort_values("W", ascending=True)
    return sorted_df


def to_steel_column(row: pd.Series, 
                    h: int, E: float, 
                    fy: int, kx: float = 1,
                    ky: float = 1, **kwargs
                    ) -> columns.SteelColumn:
    """
    Returns a SteelColumn populated with the data in 
    a row of data from the panda dataframe (Series), the 
    column height, and the steel properties E and fy
    """
    area = row["A"]
    moix = row["Ix"]
    moiy = row['Iy']
    tag = row['Section']

    sc = columns.SteelColumn(
        h=h, 
        A=area, 
        E=E, 
        Ix=moix, 
        Iy=moiy, 
        kx=kx, 
        ky=ky, 
        fy=fy,
        tag = tag,
        **kwargs 
    )
    return sc


def steel_analysis(sc: columns.SteelColumn,
                   DL: float,
                   LL: float) -> pd.Series:
    """
    Function takes a SteelColumn and returns a 
    pd.Series with Section Name, Height, Dead, 
    Live, Factored load, Axial Resistance, DCR (demand/capacity ratio)
    Note that everything has to be in N and mm units
    """
    factored_load = 1.2*DL + 1.6*LL  
    AxialResistance = 1000 * sc.factored_compressive_resistance()
    UC = factored_load/AxialResistance
    dict = {"SectionName": sc.tag,
            "Height": sc.h,
            "Dead": DL,
            "Live": LL,
            "FactoredLoad": factored_load,
            "AxialResistance": AxialResistance,
            "DCR": UC
               }
    resrow = pd.Series(dict)
    return resrow


def steel_analysis_db(df: pd.DataFrame,
                      h: int, E: float, 
                      fy: int, DL: float, LL: float,
                      kx: float = 1, ky: float = 1, 
                      **kwargs ) -> pd.DataFrame:
    """
    takes a dataframe of steel sections and returns 
    a dataframe with analyzed columns
    Note that everything has to be in N and mm units
    """
    i = 0
    empties = np.zeros([df.shape[0], 7])
    df_columns = pd.DataFrame(empties, 
                              columns = ["Section Name", "Height", 
                                        "Dead", "Live",
                                        "Factored Load",
                                        "Axial Resistance", "DCR"] )
    for i in range(0,len(df)):
        row_sc = to_steel_column(df.iloc[i], h, E, fy,kx, ky, **kwargs)
        df_columns.iloc[i] = steel_analysis(row_sc, DL, LL)
        i = i+1
    
    return df_columns

def to_steel_column_simple(section: str,
                    h: int, E: float, 
                    fy: int, kx: float = 1,
                    ky: float = 1, **kwargs
                    ) -> columns.SteelColumn:
    """
    Returns a SteelColumn populated with the data in 
    a row of data from the panda dataframe (Series), the 
    column height, and the steel properties E and fy
    """
    df = aisc_w_sections()

    #navigating to the values of the selected section in the W sections
    row = df.loc[df['Section'] == section] 

    area = row["A"].values[0]
    moix = row["Ix"].values[0]
    moiy = row['Iy'].values[0]
    tag = section

    sc = columns.SteelColumn(
        h=h, 
        A=area, 
        E=E, 
        Ix=moix, 
        Iy=moiy, 
        kx=kx, 
        ky=ky, 
        fy=fy,
        tag = tag,
        **kwargs 
    )
    return sc

def convert_to_capacity(column: pd.Series) -> pd.Series:
    """
    takes a column of loads as a pd.Series and returns a column that contains
    for each floor the selected cross section, factored axial load, 
    factored axial resistance, and demand to capacity ratio as a pd.Series
    """
    columnindex = column.index
    #print(columnindex)
    new_labels = ["Section", "Pf", "Pr", "DCR_Axial"]
    new_tuples = [(first, new_labels[i % len(new_labels)]) for i, (first, _) in enumerate(columnindex)]
    #print(new_tuples)

    capacity_column = pd.Series(index=pd.MultiIndex.from_tuples(new_tuples))  
    capacity_column = capacity_column.rename(column.name)
    #print(capacity_column)
    steel_column = np.zeros(len(column))

    with open('floor_elevations_si.json') as file:
        elevations = json.load(file)
   
    for i, floor in enumerate(column.index):
        floor_name = floor[0]
        #print(floor_name)
        capacity_column.loc[(floor_name, "Section")] = "W310X67"  
        #print(capacity_column.loc[(floor_name, "Section")])
        capacity_column.loc[(floor_name, "Pf")] = column.loc[(floor_name, "sum_factored")]
        #print(capacity_column.loc[(floor_name, "Pf")])
        sc = to_steel_column_simple("W310X67", elevations[floor_name], 210000, 400)
        capacity_column.loc[(floor_name, "Pr")] = sc.factored_compressive_resistance() 
        #print(capacity_column.loc[(floor_name, "Pr")])
        capacity_column.loc[(floor_name, "DCR_Axial")] = capacity_column[floor_name, "Pf"] / capacity_column[floor_name, "Pr"]
        #print(capacity_column.loc[(floor_name, "DCR_Axial")])

    
    return capacity_column

