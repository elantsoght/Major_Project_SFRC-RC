def ACI_31819_COMBOS():
    ACI_31819_COMBOS = {
    "LC1": {"D": 1.4},
    "LC2a": {"D": 1.2, "L": 1.6, "Lr":0.5},
    "LC2b": {"D": 1.2, "L": 1.6, "S":0.5},
    "LC2c": {"D": 1.2, "L": 1.6, "R":0.5},
    "LC3a": {"D":1.2, "Lr": 1.6, "L":1.0},
    "LC3b": {"D":1.2, "S": 1.6, "L":1.0},
    "LC3c": {"D":1.2, "R": 1.6, "L":1.0},
    "LC3d": {"D":1.2, "Lr": 1.6, "W":1.0},
    "LC3e": {"D":1.2, "S": 1.6, "W":1.0},
    "LC3f": {"D":1.2, "R": 1.6, "W":1.0},
    "LC4": {"D": 1.2, "E": 1.0, "L": 1.0, "S":0.2},
    "LC5": {"D": 0.9, "W": 1.0},
    "LC6": {"D": 0.9, "E": 1.0}
            }
    return ACI_31819_COMBOS

def factor_load(
        D_load: float = 0., D: float = 0.,
        L_load: float = 0., L: float = 0.,
        Lr_load: float = 0., Lr: float=0.,
        S_load: float = 0., S: float=0.,
        W_load: float = 0., W: float=0.,
        R_load: float = 0., R: float=0.,
        E_load: float = 0., E: float=0.,):
    factored_load = D_load*D + L_load*L + Lr_load*Lr + S_load*S+ W_load*W 
    + R_load*R + E_load*E 
    return factored_load


def max_factored_load(loads: dict, load_combos: dict) -> float:
    """
    Returns the maximum factored load from "loads" based 
    on the combination in 'load_combos'
    """
    factored_loads = []
    for load_combo in load_combos.values():
        factored_load = factor_load(**loads, **load_combo)
        factored_loads.append(factored_load)
    return max(factored_loads)  


def min_factored_load(loads: dict, load_combos: dict) -> float:
    """
    Returns the minimum factored load from "loads" based 
    on the combination in 'load_combos'
    """
    factored_loads = []
    for load_combo in load_combos.values():
        factored_load = factor_load(**loads, **load_combo)
        factored_loads.append(factored_load)
    return min(factored_loads)  



def envelope_max(results_arrays: dict) -> list[list[float], list[float]]:
    """
    The first sublist will be the untouched x-coordinate array from the input 
    but the second sublist will be represent an array of the maximum value across 
    all load combinations for each coordinate step.
    """
    x_values = results_arrays[list(results_arrays.keys())[0]][0][0]
    max_values = [float('-inf')] * len(x_values)

    for idx, result_array in enumerate(results_arrays.values()):
        for i in range(0,len(max_values)):
            valuearray = results_arrays[list(results_arrays.keys())[idx]][0][1]
            if valuearray[i] > max_values[i]:
                max_values[i] = valuearray[i]

    return [x_values, max_values]  


def envelope_min(results_arrays: dict) -> list[list[float], list[float]]:
    """
    The first sublist will be the untouched x-coordinate array from the input 
    but the second sublist will be represent an array of the maximum value across 
    all load combinations for each coordinate step.
    """
    x_values = results_arrays[list(results_arrays.keys())[0]][0][0]
    min_values = [float('inf')] * len(x_values)

    for idx, result_array in enumerate(results_arrays.values()):
        for i in range(0,len(min_values)):
            valuearray = results_arrays[list(results_arrays.keys())[idx]][0][1]
            if valuearray[i] < min_values[i]:
                min_values[i] = valuearray[i]

    return [x_values, min_values]  
