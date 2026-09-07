import numpy as np
from aerostruct15mw.config import TurbineConfig
from aerostruct15mw.control import below_rated_rpm, rotor_rpm_schedule

def test_rpm_schedule_is_clipped():
    cfg = TurbineConfig(); assert np.isclose(below_rated_rpm(3.0, cfg), cfg.rpm_min); assert rotor_rpm_schedule(25.0, cfg) == cfg.rpm_rated

def test_rpm_schedule_hits_rated_condition():
    cfg = TurbineConfig(); assert np.isclose(rotor_rpm_schedule(cfg.rated_wind_mps, cfg), cfg.rpm_rated, atol=0.05)
