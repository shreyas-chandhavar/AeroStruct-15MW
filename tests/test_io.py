from pathlib import Path
from aerostruct15mw.io import read_aerodyn_polar

def test_polar_reader(tmp_path: Path):
    p = tmp_path / "polar.dat"; p.write_text("2 NumAlf\n! comment\n-1.0 0.1 0.01 0.0\n1.0 0.2 0.02 0.0\n"); df = read_aerodyn_polar(p); assert list(df.columns) == ["alpha_deg", "Cl", "Cd", "Cm"]; assert len(df) == 2
