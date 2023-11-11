from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from openpyxl import load_workbook
from rich.progress import track
import xlwings as xw
import excel_engine

def test_update_rebar():
    """
    a test function to check if redoing rebar works
    """
    here = Path.cwd()
    print(here)
    test_file = here / "eng_module" / "test_data" / "Basic Concrete Footing.xlsx"
    changes = excel_engine.update_rebar(test_file, 330)[2]
    assert changes == {'nlong': True, 'nwidth': True, 'typelong': True, 'typewidth': True}