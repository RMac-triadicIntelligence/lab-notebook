import numpy as np
from scipy.integrate import odeint

def hill(x: np.ndarray | float, gamma: float = 10.0, threshold: float = 0.5, steepness: int = 6):
    """Steep sigmoidal activation — sharp response once threshold crossed."""
    x = np.asarray(x)
    return gamma * (x ** steepness) / (threshold ** steepness + x ** steepness + 1e-12)

def model_parable(
    y, t,
    gamma: float = 10.0, threshold: float = 0.5, steepness: int = 6,
    base_decay: float = 0.22,
    dwelling_rise: float = 0.35,
    dwelling_fade: float = 0.45,
    coupling_boost: float = 0.8,
    decay_relief: float = 0.6,
    story_depth: float = 0.8,
    nudge_time: float | None = None,
    nudge_duration: float = 2.0,
    nudge_strength: float = 0.5,
):
    """
    y = [x1, x2, x3, dwelling]
    x1,x2,x3 ∈ [0,1] : activation of three facets
    dwelling ∈ [0,1] : holding field that modulates coupling/decay
    """
    x1, x2, x3, dwelling = np.clip(y, 0.0, 1.0)

    coherence = (x1 + x2 + x3) / 3.0

    # Dwelling field dynamics
    d_dwelling_dt = (
        dwelling_rise * story_depth * (1 - coherence) * (1 - dwelling)
        - dwelling_fade * coherence * dwelling
    )

    # Dwelling shapes coupling and decay
    coupling = 1.0 + coupling_boost * dwelling
    decay = base_decay * (1.0 - decay_relief * dwelling)

    # Facet activations
    act1 = hill(x1, gamma, threshold, steepness)
    act2 = hill(x2, gamma, threshold, steepness)
    act3 = hill(x3, gamma, threshold, steepness)

    dx1_dt = coupling * (act2 + act3) / 2.0 * (1 - x1) - decay * x1
    dx2_dt = coupling * (act1 + act3) / 2.0 * (1 - x2) - decay * x2
    dx3_dt = coupling * (act1 + act2) / 2.0 * (1 - x3) - decay * x3

    # Optional pulse nudge
    if nudge_time is not None and (nudge_time <= t < nudge_time + nudge_duration):
        dx1_dt += nudge_strength * (1 - x1)

    return [dx1_dt, dx2_dt, dx3_dt, d_dwelling_dt]

def simulate(
    t: np.ndarray,
    y0=(0.2, 0.1, 0.15, 0.6),
    intervention_time: float = 25.0,
    nudge_mode: str = "jump",   # "jump" or "pulse"
    jump_amount: float = 0.5,
    pulse_duration: float = 2.0,
    pulse_strength: float = 0.5,
    **model_kwargs,
):
    """Run with/without nudge and return both solutions."""
    t = np.asarray(t)
    idx = int(np.searchsorted(t, intervention_time))

    sol_without = odeint(lambda y, tt: model_parable(y, tt, **model_kwargs), y0, t)

    if nudge_mode == "jump":
        sol_pre = odeint(lambda y, tt: model_parable(y, tt, **model_kwargs), y0, t[:idx])
        y_nudge = sol_pre[-1].copy()
        y_nudge[0] = min(y_nudge[0] + jump_amount, 1.0)
        sol_post = odeint(lambda y, tt: model_parable(y, tt, **model_kwargs), y_nudge, t[idx:])
        sol_with = np.vstack((sol_pre, sol_post))
    elif nudge_mode == "pulse":
        sol_with = odeint(
            lambda y, tt: model_parable(
                y, tt,
                nudge_time=intervention_time,
                nudge_duration=pulse_duration,
                nudge_strength=pulse_strength,
                **model_kwargs,
            ),
            y0, t
        )
        y_nudge = None
    else:
        raise ValueError("nudge_mode must be 'jump' or 'pulse'")

    return sol_without, sol_with, idx, y0, y_nudge
