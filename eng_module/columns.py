from dataclasses import dataclass
import math 
from typing import Optional
import csv
from eng_module import utils 
from eng_module import load_factors

@dataclass
class Column:
    """
    A data type to describe the data required to compute the capacity of a column
    
    Assumptions: 
        - All values are either consistently SI units or US customary units
    """  
    h: int
    E: float
    A: float
    Ix: float
    Iy: float
    kx: float
    ky: float
    
    def critical_buckling_load(self, axis: str) -> float:
       try:
           if axis == "x":
                BL = euler_buckling_load(self.h, self.E, self.Ix, self.kx)

           elif axis == "y":
                BL = euler_buckling_load(self.h, self.E, self.Iy, self.ky)
       except ValueError:
            print("The axis should be x or y")
       return BL
    
    def radius_of_gyration(self, axis:str) -> float:
        try:
            if axis == "x":
                gr = radius_of_gyration(self.A, self.Ix)
            elif axis =="y":
               gr = radius_of_gyration(self.A, self.Iy)
        except ValueError:
            print("The axis should be x or y")
        return gr         
    

def euler_buckling_load(l: float, E: float, I: float, k:float)->float:
    """
    Returns the Euler critical buckling load for an axially loaded
    member based on it's length 'l', elastic modulus 'E', moment of inertia
    'I', and effective length factor 'k'.

    Assumptions: a linear elastic material and that the member is a
    prismatic section
    """
    P_cr = math.pi**2 * E * I / (k*l)**2
    return P_cr  


def radius_of_gyration(A: float, I: float) -> float:
    """
    returns the radius of gyration
    """
    return math.sqrt(I/A)


@dataclass
class SteelColumn(Column):
    """
    a dataclass to represent a steel column
    """
    fy: int
    phic: float = 0.95
    tag: Optional[str] = None
    factored_load: Optional[float] = None  # Added factored_load attribute
    demand_capacity_ratio: Optional[float] = None  # Added demand_capacity_ratio attribute
    
    def factored_crushing_load(self) -> float:
        """
        returns the crushing load in kN
        """
        Po = (self.fy * self.A)/1000
        return self.phic * Po
    
    def factored_compressive_resistance(self)->float:
        """
        per AASHTO chapter 6
        """
        Pex = 0.001 * self.critical_buckling_load("x")
        Pey = 0.001 * self.critical_buckling_load("y")
        Po = (self.fy * self.A)/1000
        if Po/Pex <= 2.25:
            Pnx = Po * (0.658**(Po/Pex))
        elif Po/Pex > 2.25:
            Pnx = 0.877 * Pex
        else: 
            print("calculation not correct for x-axis")
        if Po/Pey <= 2.25:
            Pny = Po * (0.658**(Po/Pey))
        elif Po/Pey > 2.25:
            Pny = 0.877 * Pey
        else: 
            print("calculation not correct for y-axis") 
        return self.phic * min(Pnx, Pny)




def csv_record_to_steelcolumn(record: list[str], **kwargs) -> SteelColumn:
    """
    Returns a SteelColumn populated with the data in 'record' and **kwargs
    """
    tag = record[0]
    area = utils.str_to_float(record[1])
    height = utils.str_to_float(record[2])
    moix = utils.str_to_float(record[3])
    moiy = utils.str_to_float(record[4])
    yield_stress = utils.str_to_float(record[5])
    e_mod = utils.str_to_float(record[6])
    kx = utils.str_to_float(record[7])
    ky = utils.str_to_float(record[8])
    dead_load = utils.str_to_float(record[9])
    live_load= utils.str_to_float(record[10])

    sc = SteelColumn(
        h=height, 
        A=area, 
        E=e_mod, 
        Ix=moix, 
        Iy=moiy, 
        kx=kx, 
        ky=ky, 
        fy=yield_stress,
        tag = tag,
        **kwargs # remember dictionary unpacking?
    )
    return sc


def convert_csv_data_to_steelcolumns(csv_data: list[list[str]], **kwargs)-> list[SteelColumn]:
     """
     Converts all of the data in the csv file into a list 
     of SteelColumn that are ready to do further work
     """
     sc_list = []
     for row in csv_data:
         sc = csv_record_to_steelcolumn(row, **kwargs)
         sc_list.append(sc)
     return sc_list   


def calculate_factored_csv_load(record: list[str])->float:
    """
    To calculate a maximum factored load, 
    according to your load combinations and assumptions, 
    based on the dead load and live load data present in one row of the csv file
    """
    dead_load = utils.str_to_float(record[9])
    live_load= utils.str_to_float(record[10])
    loads = {"D_load": dead_load, "L_load": live_load}
    return load_factors.max_factored_load(loads, load_factors.ACI_31819_COMBOS())


def run_all_columns(filename: str, **kwargs) -> list[SteelColumn]:
    """
    This function will read the data in the CSV file and will return a list 
    of SteelColumn based on the data in the CSV file but also with two additional 
    attributes added that are populated with a factored load and demand/capacity 
    ratio of each column under the applied loading
    """
    csv_data = utils.read_csv_file(filename)
    csv_data.pop(0)
    sc_list = convert_csv_data_to_steelcolumns(csv_data)

    for idx, row in enumerate(csv_data):
        fl =  calculate_factored_csv_load(row)/1000
        sc_list[idx].factored_load = fl
        cap = sc_list[idx].factored_compressive_resistance()
        UC = fl/cap
        sc_list[idx].demand_capacity_ratio = UC
  
    return sc_list


def export_steelcolumn_results(SteelColumns: list[SteelColumn], export_filename: str) -> None:
    """
    Export the results of SteelColumn analysis to a new CSV file.
    """
    with open(export_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        header = ["Tag", "Factored Load (kN)", "Demand Capacity Ratio (-)"]
        writer.writerow(header)
        
        for column in SteelColumns:
            tag = column.tag
            factored_load = column.factored_load
            demand_capacity_ratio = column.demand_capacity_ratio
            
            writer.writerow([tag, factored_load, demand_capacity_ratio])




    
