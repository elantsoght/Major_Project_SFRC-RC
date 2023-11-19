import math
from PyNite import FEModel3D
from eng_module import utils 
from typing import Optional
from eng_module import load_factors

def calc_shear_modulus(nu: float, E:float)-> float:
    """
    Returns the shear modulus calculated for a material based 
    on the Poisson's ratio 'nu' and the elastic modulus 'E'

    Assumes that the material is a linear elastic isotropic 
    material
    """
    G = E / (2 * (1 + nu))
    return G

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


def beam_reactions_ss_cant(w: float, b:float, a:float)->float:
    """
    Returns the reactions R1 and R2 for a simply support beam with 
    a  cantilever at one end. R2 is the "backspan" reaction and R1
    is the hammer reaction

    |||||||||||||||||||||||||||||||||||||||||w
    _________________________________________beam
    ^R2                            ^R1
      
    """
    R2 = w / (2*b) * (b**2 - a**2)
    R1 = w / (2*b) * (b+a)**2
    return R1, R2


def fe_model_ss_cant(
    w: float, 
    b: float, 
    a: float, 
    E: float=1., 
    I: float=1., 
    A: float=1., 
    J: float=1., 
    nu: float=1., 
    rho: float=1., 
)->FEModel3D:
    """
    Returns a PyNite beam model ready for analysis. The member name of 
    the beam is "M0". The beam is going to be in the following 
    configuration 
    
    |||||||||||||||||||||||||||||||||||||||||w
    _________________________________________beam
    ^R2                            ^R1
    |-------------b----------------|----a----|

    Where 'w' represents the magnitude of the applied UDL
    'b' represents the backspan length and 'a' represents the
    cantilever length
    """

    beam_model = FEModel3D()
    beam_model.add_node("N0", 0, 0, 0)
    beam_model.add_node("N1", b, 0, 0)
    beam_model.add_node("N2",a + b, 0, 0)
    beam_model.def_support("N0",True, True, True, True, True, False)
    beam_model.def_support("N1",False, True, False, False, False, False)

    shear_modulus = calc_shear_modulus(nu, E)

    beam_model.add_material("My material",E, shear_modulus, nu, rho)
    beam_model.add_member("M0", "N0", "N2", "My material", Iy = 1., Iz=I, J=J, A=A)

    beam_model.add_member_dist_load("M0", "Fy", w, w)

    return beam_model   


def read_beam_file(filename: str) -> list[list[str]]:
    """
    Returns a list of list of strings representing the text data in the file at 
    'filename'
    """
    return utils.read_csv_file(filename)


def separate_lines(input: str) ->list:
    """
    returns a list with the file data in individual lines
    """
    list = input.split("\n")
    return list


def extract_data(input_list: list, index: int) -> list[str]:
    """
    Returns the data list item corresponding to the index separated
    """
    line = input_list[index].split(", ")
    return line


def get_spans(beamlength: float, cant_sup: float) -> tuple[float, float]:
    """
    Takes a total beam length and location of the cantilver support 
    and returns the length of the backspan ("b") and the length of the cantilever ("a")
    """
    b = cant_sup
    a = beamlength - cant_sup
    return b , a  


def load_beam_model (filename: str, add_combos: Optional[str] = None) -> FEModel3D:
    """
    converts a text file of beam data into a beam model
    NOTE:
    this function assumes that the data in the beam file 
    describes a simply supported beam with a cantilever on one side 
    and a single UDL loading it in the gravity direction.
    """
    input = read_beam_file(filename)
    beam_input = get_structured_beam_data(input)
    beam_model = build_beam(beam_input)
    if add_combos is not None:
        if add_combos == "ACI_31819":
            load_combos = load_factors.ACI_31819_COMBOS()
        else:
            raise ValueError(f"So far, this only works for ACI_31819 as input")
        for combo_name, combo_factors in load_combos.items():
            beam_model.add_load_combo(combo_name, combo_factors)
    return beam_model


def separate_data(data: list[str]) -> list[list[str]]:
    """
    The functions purpose is to split up each 
    individual line of data in the input so that
    we get a list of list of strings
    """
    listoflists = []
    for line in data:
        newline = line.split(", ")
        listoflists.append(newline)
    return listoflists   


def convert_to_numeric(listinput: list[list[str]]) -> list[list[float]]:
    """
    turns the numeric data into numbers
    """
    newlist = []
    for line in listinput:
        i = 0
        for value in line:
            newvalue = utils.str_to_float(value)
            line[i] = newvalue
            i = i + 1
        newlist.append(line)
    return newlist   


def get_structured_beam_data(listinput: list[list[str]]) -> dict:
    """"
    This function creates a dictionary with all of the beam data 
    nicely parcelled out. In other words, the goal is to take the raw data, 
    which only has meaning because we happen to know the file format, 
    and to put it in a structured form where it has explicit meaning.
    """
    attributes = listinput[1]
    floatattributes = []
    for attribute in attributes:
        value = utils.str_to_float(attribute)
        floatattributes.append(value)
    structured_data = {'Name': "M1"}
    structured_data.update({'Name': str(listinput[0]).strip("[").strip("]").strip("'")})
    structured_data.update(parse_beam_attributes(floatattributes))
    structured_data.update({"Supports":parse_supports(listinput[2])})
    structured_data.update({"Loads":parse_loads(convert_to_numeric(listinput[3:]))}) 
    return structured_data    
        


def get_node_locations(supports: list, beamlength) -> dict[str, float]:
    """
    Takes a list with support positions and
    returns a dictionarry with support nodes 
    and node coordinates
    """
    itendsup = len(supports)
    if supports[0] > 0:
        itendsup = itendsup + 1
    else:
        itendsup = itendsup + 0
    node_info = {"N0":0.0}
    i = 0
    for support in supports:
        i = i+1
        if supports[0] > 0:
            node_info.update({f"N{i}": support})
            
        else:
            node_info.update({f"N{i-1}": support})
    
    if supports[len(supports)-1] < beamlength:
        node_info.update({f"N{itendsup}": beamlength})
    return node_info


# def build_beam(beam_data: dict) -> FEModel3D:
#     """
#     Returns a beam finite element model for the data in 'beam_data' which is represents
#     a continuous beam with first x-coo = 0.
#     The beam can be loaded with both UDL loading and Point loads
#     """
#     beam_model = FEModel3D()
#     G = calc_shear_modulus(nu = beam_data["nu"], E = beam_data["E"])
#     beam_model.add_material('Material', beam_data["E"], G, beam_data["nu"], beam_data["rho"])
#     supp_locs = list(beam_data['Supports'].keys())
#     supp_types = list(beam_data['Supports'].items())
#     Nodes = get_node_locations(supp_locs, beam_data["L"])   
#     for node_name, x_coord in Nodes.items():
#         beam_model.add_node(node_name, x_coord, 0, 0)
    
#     if supp_locs[0] > 0:
#         i = 2
#         if beam_data['Supports'].get(supp_locs[0]) == "P":
#             beam_model.def_support(node_name = "N1", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False)
#         elif beam_data['Supports'].get(supp_locs[0]) == "R":
#              beam_model.def_support("N1", False, True, True, False, False, False)
#         else:
#              print("The correct support type is not provided")
#              beam_model.def_support(node_name = "N1", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False)
#         numsups = len(supp_locs)
#         print(f"numsups is {numsups}")
#         supnum = 1
#         for supnum in range(1,numsups):
            
#             if beam_data['Supports'].get(supp_locs[supnum]) == "P":
#                 beam_model.def_support(node_name = f"N{i}", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False)
      
#             elif beam_data['Supports'].get(supp_locs[supnum]) == "R":
#                 beam_model.def_support(f"N{i}", False, True, True, False, False, False)
#             else:
#                 print("The correct support type is not provided")
#                 beam_model.def_support(node_name = f"N{i}", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False) 
#             supnum = supnum + 1
#             i = i + 1
#     elif supp_locs[0] == 0:   
#         i = 1
#         if beam_data['Supports'].get(supp_locs[0]) == "P":
#            beam_model.def_support(node_name = "N0", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False)
#         elif beam_data['Supports'].get(supp_locs[0]) == "R":
#             beam_model.def_support("N0", False, True, True, False, False, False)
#         else:
#            print("The correct support type is not provided")
#            beam_model.def_support(node_name = "N0", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False)
        
#         numsups = len(supp_locs)
#         supnum = 1
#         for supnum in range(0,numsups-1):   
#             supnum = supnum + 1
#             if beam_data['Supports'].get(supp_locs[supnum]) == "P":
#                 beam_model.def_support(f"N{i}",support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False) 
#             elif beam_data['Supports'].get(supp_locs[supnum]) == "R":
#                 beam_model.def_support(f"N{i}", False, True, True, False, False, False)
#             else:
#                 print("The correct support type is not provided")
#                 beam_model.def_support(f"N{i}", support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=False, support_RZ=False) 
            
#             i = i + 1
#     else:
#         print("something is wrong, as the position of the first support nodes is not properly defined")
#     load_cases = []
#     for load in beam_data['Loads']:
#         if load['Type'] == "Point":
#             beam_model.add_member_pt_load(
#                 beam_data['Name'],
#                 load['Direction'],
#                 load['Magnitude'],
#                 load['Location'],
#                 case=load["Case"],
#             )
#             if load['Case'] not in load_cases:
#                 load_cases.append(load['Case'])
#         elif load['Type'] == "Dist":
#             beam_model.add_member_dist_load(
#                 beam_data['Name'],
#                 load['Direction'],
#                 load['Start Magnitude'],
#                 load['End Magnitude'],
#                 load['Start Location'],
#                 load['End Location'],
#                 case=load['Case']
#             )
#             if load['Case'] not in load_cases:
#                 load_cases.append(load['Case'])

#     for load_case in load_cases:
#         beam_model.add_load_combo(load_case, {load_case: 1.0})      
#     # num = len(Nodes) - 1
#     # beam_model.add_member(name=beam_data["Name"], i_node = "N0", j_node = f"N{num}", material = "Material", Iy = beam_data["Iy"], 
#     #                       Iz = beam_data["Iz"], J = beam_data["J"], A = beam_data["A"])
#     # beam_model.add_load_combo(name="Dead", factors={"Dead": 1.0})
#     # beam_model.add_load_combo(name="Live", factors={"Live": 1.0})  
#     # t = 0
        
#     # for t in range(0,len(beam_data["Loads"])):
#     #     if beam_data["Loads"][t].get("Case") == "L":
#     #         beam_data["Loads"][t]["Case"] = "Live"
#     #     else:
#     #         print("the key of the live loads is ok")
#     #     if beam_data["Loads"][t].get("Case") == "D":
#     #         beam_data["Loads"][t]["Case"] = "Dead"
#     #     else:
#     #         print("the key of the dead loads is ok")

#     #     if beam_data["Loads"][t].get("Type") == "Dist":
#     #         beam_model.add_member_dist_load(Member=beam_data["Name"], 
#     #                                         Direction=beam_data["Loads"][t].get("Direction"), 
#     #                                         w1 = beam_data["Loads"][t].get("Start Magnitude"), 
#     #                                         w2 = beam_data["Loads"][t].get("End Magnitude"), 
#     #                                         x1 = beam_data["Loads"][t].get("Start Location"), 
#     #                                         x2 = beam_data["Loads"][t].get("End Location"), 
#     #                                         case = beam_data["Loads"][t].get("Case"))
#     #     elif beam_data["Loads"][t].get("Type") == "Point":
#     #         beam_model.add_member_pt_load(Member=beam_data["Name"], 
#     #                                       Direction = beam_data["Loads"][t].get("Direction"), 
#     #                                       P = beam_data["Loads"][t].get("Magnitude"), 
#     #                                       x = beam_data["Loads"][t].get("Location"),
#     #                                       case = beam_data["Loads"][t].get("Case")) 
#     #     else:
#     #         print("No proper input is given for the type of loading")
#     #     t = t + 1
 
#     return beam_model 

def build_beam(beam_data: dict) -> FEModel3D:
    """
    Returns a FEModel3D of a beam that has the attributes described in 'beam_data' and 'A', 'J', 'nu', and 'rho'.
    """
    beam_data['Nodes'] = get_node_locations(list(beam_data['Supports'].keys()), beam_data['L'])
    beam_model = FEModel3D()
    for node_name, x_coord in beam_data['Nodes'].items():
        beam_model.add_node(node_name, x_coord, 0, 0)
        support_type = beam_data['Supports'].get(x_coord, None)
        if support_type == "P":
            beam_model.def_support(node_name, True, True, True, True, True, False)
        elif support_type == "R":
            beam_model.def_support(node_name, False, True, False, False, False, False)
        elif support_type == "F":
            beam_model.def_support(node_name, True, True, True, True, True, True)

    shear_modulus = calc_shear_modulus(beam_data['E'], beam_data['nu'])
    beam_model.add_material("Beam Material", beam_data['E'], shear_modulus, beam_data['nu'], beam_data['rho'])
    
    # The variable 'node_name' retains the last value from the for loop
    # Which gives us the j-node
    beam_model.add_member(
        beam_data['Name'], 
        "N0", 
        node_name, 
        material="Beam Material", 
        Iy=beam_data['Iy'], 
        Iz=beam_data['Iz'],
        J=beam_data['J'],
        A=beam_data['A'],
    )
    load_cases = []
    for load in beam_data['Loads']:
        if load['Type'] == "Point":
            beam_model.add_member_pt_load(
                beam_data['Name'],
                load['Direction'],
                load['Magnitude'],
                load['Location'],
                case=load["Case"],
            )
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])
        elif load['Type'] == "Dist":
            beam_model.add_member_dist_load(
                beam_data['Name'],
                load['Direction'],
                load['Start Magnitude'],
                load['End Magnitude'],
                load['Start Location'],
                load['End Location'],
                case=load['Case']
            )
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])

    for load_case in load_cases:
        beam_model.add_load_combo(load_case, {load_case: 1.0})
    return beam_model


def parse_supports(supports: list[str]) -> dict[float, str]:
    dict_sup = {}
    for support in supports:
        support = utils.str_to_float(support)
        if isinstance(support, float):
            coo = support
            print(coo)
            type = "P"
            print(type)
            dict_sup.update({coo: type})
        elif isinstance(support, str):
            split = support.split(":")
            coo = utils.str_to_float(split[0])
            type = split[1]
            dict_sup.update({coo: type})  
        else:
            print("input type is not suitable")
    return dict_sup


def parse_loads(loads: list[list[str|float]]) -> list[dict]:
    """
    This function takes a list of list of strings or floats with information about
    load positions, direction, locations, and loading types, and returns it into a dictionarry
    format with the appropriate keys
    """
    parsed_loads = []
    for load in loads:
        dict_loads = {"Type": "Dist", "Direction": "Fy"} 
        type = "dist"
        direction = "Fy"
        if isinstance(load[0], (int, float)):
            start_mag = load[0]
            start_load = load[1]
            end_load = load[2]
            dict_loads = {
                "Type": "Dist",
                "Direction": "Fy",
                "Start Magnitude": start_mag,
                "End Magnitude": start_mag,
                "Start Location": start_load,
                "End Location": end_load,
                "Case": "Live"
            }
                
        elif isinstance(load[0], str):
            type = load[0].split(":")[0]
            direction = load[0].split(":")[1]
            dict_loads.update({"Type" : type, "Direction": direction})
            if type == "POINT":
               type = 'Point' 
               magnitude = load[1]
               location = load[2]
               casetype = load[3].split(":")[1]
               dict_loads.update({"Type": type, "Magnitude": magnitude, "Location": location, "Case": casetype})
            elif type == "DIST":
                type = 'Dist'
                start_mag = load[1]
                end_mag = load[2]
                start_load = load[3]
                end_load = load[4]
                casetype = load[5].split(":")[1]
                dict_loads.update({"Type": type, "Start Magnitude": start_mag, "End Magnitude": end_mag, "Start Location": start_load,
                                        "End Location": end_load, "Case": casetype})
        else:
            print("Type of loading is not defined")
            start_mag = load[0]
            print(start_mag)
            start_load = load[1]
            end_load = load[2]
            dict_loads.update({"Type": type, "Start Magnitude": start_mag, "End Magnitude": start_mag, "Start Location": start_load,
                                "End Location": end_load, "Case": "L"})
            
        parsed_loads.append(dict_loads)
    return parsed_loads  

def parse_beam_attributes(values: list[float]) -> dict[str, float]:
   """
   This function parses the second line of the input data file
   into material that can be read into PyNite
   all default values are 1, and only if we have data it goes
   into the dictionary with info
   """ 
   beam_dict = {"L": 1, "E": 1, "Iz": 1, "Iy": 1, "A": 1, "J": 1, "nu": 1, "rho": 1}
   keys = list(beam_dict.keys())
   for i, value in enumerate(values):
        beam_dict[keys[i]] = value
   return beam_dict  


def extract_arrays_all_combos(solved_beam_model = FEModel3D, result_type = str, direction = str, n_points = int):
    """
    Extracts factored analysis results for all load combinations.

    Input:
        solved_beam_model (FEModel3D): Solved FEModel3D model.
        result_type (str): Type of result - "shear", "moment", "axial", "deflection", or "torque".
        direction (str): Direction for the result (if applicable).
        n_points (int): Number of points to return.

    Returns:
        dict: A dictionary where keys are load combo names and values are result arrays.
    """
    result_arrays = {}

    for combo_name, load_combo in solved_beam_model.LoadCombos.items():
        result_array = []

        for member in solved_beam_model.Members.values():
            if result_type == "shear":
                result_array.append(member.shear_array(direction, n_points, combo_name))
            elif result_type == "moment":
                result_array.append(member.moment_array(direction, n_points, combo_name))
            elif result_type == "axial":
                result_array.append(member.axial_array(n_points, combo_name))
            elif result_type == "torque":
                result_array.append(member.torque_array(n_points, combo_name))
            elif result_type == "deflection":
                result_array.append(member.deflection_array(direction, n_points, combo_name))

        result_arrays[combo_name] = result_array

    return result_arrays



