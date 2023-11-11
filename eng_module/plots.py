from matplotlib.figure import Figure
from typing import Optional
from PyNite import FEModel3D
from eng_module import beams
from eng_module import load_factors

def plot_results(beam_model: FEModel3D, result_type: str, 
                 direction: Optional[str] = None, units: Optional[str] = None, 
                 load_combo: Optional[str] = None, figsize=(8,3), dpi=200, 
                 n_points=1000) -> Figure:
    
    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.gca()
    result_arrays = beams.extract_arrays_all_combos(beam_model, 
                                                   result_type, 
                                                   direction, 
                                                   n_points)
    enveloperesults = load_factors.envelope_max(result_arrays)
    x_array = enveloperesults[0]

    # Plot beam line
    ax.plot(x_array, [0] * len(x_array), color='k')

    # Plot envelope
    max_result_env = load_factors.envelope_max(result_arrays)
    min_result_env = load_factors.envelope_min(result_arrays)
    ax.fill_between(x_array, y1=max_result_env[1], y2=min_result_env[1], fc='teal', alpha=0.35)

    if load_combo is not None:
        ax.plot(x_array, result_arrays[load_combo][0][1], color='b')
        if units is not None:
            ax.set_title(f'Max/min {result_type} envelope w/ load combo {load_combo} ({units})')
        else:
            ax.set_title(f'Max/min {result_type} envelope w/ load combo {load_combo}')
    else:
        ax.set_title(f'Max/min {result_type} envelope')

    # Add some "padding" around the top and bottom of the plot
    ax.margins(x=0.1, y=0.1)

    # Setup the variables required for labelling
    if result_type == "shear":
        action_symbol = "Vf"
    elif result_type == "moment": 
        action_symbol = "Mf"
    elif result_type == "axial":
        action_symbol = "Nf"
    elif result_type == "torque":
        action_symbol = "Tf"
    elif result_type == "deflection":
        action_symbol = "$\Delta$"

    if max(x_array) < 1000:
        loc_precision = 1
    else:
        loc_precision = -1
    
    max_value = max(max_result_env[1])
    min_value = min(min_result_env[1])
    print(max_value)
    print(min_value)
    delta = max(abs(max_value), abs(min_value))
    results_precision = 0
    if delta < 100:
        results_precision = 2
    
    max_idx = max_result_env[1].index(max_value)
    max_value_loc = max_result_env[0][max_idx]
    ax.annotate(xy=[max_value_loc, max_value], text=f"{action_symbol}, max @ {round(max_value_loc, loc_precision)} mm = {round(max_value, results_precision)} {units}")
    

    min_idx = min_result_env[1].index(min_value)
    min_value_loc = min_result_env[0][min_idx]
    ax.annotate(xy=[min_value_loc, min_value], text=f"{action_symbol}, min @ {round(min_value_loc, loc_precision)} mm = {round(min_value, results_precision)} {units}")
    
    ax.set_xlabel('Position in mm') 
    ax.set_ylabel(f"{result_type} in {units}") 

    return fig


