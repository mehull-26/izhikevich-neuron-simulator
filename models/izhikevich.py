import matplotlib.pyplot as plt
from brian2 import *
import yaml
from brian2 import ms


class IzhikevichNeuron:
    def __init__(self, a, b, c, d, stimulus, dt, t_end, integrator):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

        self.stimulus = stimulus

        self.dt = dt
        self.t_end = t_end
        self.integrator = integrator

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)

        # neuron parameters
        a = _require(cfg, ["neuron", "parameters", "a"])
        b = _require(cfg, ["neuron", "parameters", "b"])
        c = _require(cfg, ["neuron", "parameters", "c"])
        d = _require(cfg, ["neuron", "parameters", "d"])

        # stimulus
        stim = _require(cfg, ["stimulus"])
        stim_base = _require(cfg, ["stimulus", "base"])
        stim_components = _require(cfg, ["stimulus", "components"])
        stim_comp = []

        for component in stim_components:
            stim_kind = _require(component, ["kind"])

            amplitude = _require(component, ["amplitude"])
            start = _require(component, ["start_ms"])
            duration = _require(component, ["duration_ms"])
            stim_comp.append({
                "kind": stim_kind,
                "amplitude": amplitude,
                "start": start * ms,
                "duration": duration * ms
            })
        stimulus = {"base": stim_base,
                    "components": stim_comp}

        # --- simulation ---
        dt_ms = _require(cfg, ["simulation", "dt_ms"])
        t_end_ms = _require(cfg, ["simulation", "t_end_ms"])
        integrator = _require(cfg, ["simulation", "integrator"])

        _require_positive("dt_ms", dt_ms)
        _require_positive("t_end_ms", t_end_ms)

        return cls(
            a=a,
            b=b,
            c=c,
            d=d,
            stimulus=stimulus,
            dt=dt_ms * ms,
            t_end=t_end_ms * ms,
            integrator=integrator
        )

    def run(self):
        start_scope()
        defaultclock.dt = self.dt

        stim = self.stimulus

        # Intialize the steps and I array
        n_steps = int(self.t_end / self.dt)
        I_values = zeros(n_steps)
        I_values += stim["base"]

        # build step current
        for c in stim["components"]:
            if c["kind"] == "step":
                s = int(c["start"] / self.dt)
                e = int((c["start"] + c["duration"]) / self.dt)
                # Boundary check
                if s < 0 or e > n_steps:
                    raise ValueError("Stimulus is outside simulation window.")

                I_values[s:e] += c["amplitude"]
            else:
                # unsupported stimulus kind check
                raise ValueError("This kind of stimulus is yet unsupported.")

        I_t = TimedArray(I_values, dt=self.dt)

        # Izhikevich equations
        eqs = '''
        dv/dt = (0.04*v**2 + 5*v + 140 - u + I_t(t)) / ms : 1
        du/dt = a*(b*v - u) / ms : 1
        a : 1
        b : 1
        '''

        method = validate_integrator(self.integrator)

        G = NeuronGroup(
            1,
            eqs,
            threshold='v >= 30',
            reset='''
                v = c
                u += d
                ''',
            method=method
        )

        # parameters
        G.v = -65
        G.u = float(self.b) * G.v
        G.a = self.a
        G.b = self.b

        c = self.c
        d = self.d

        M = StateMonitor(G, 'v', record=True)

        run(self.t_end)

        # plot
        fig, ax = plt.subplots(2, 1, sharex=True, figsize=(
            8, 5), gridspec_kw={'height_ratios': [5, 1]})

        ax[0].set_ylabel("Membrane potential (V)")
        ax[0].plot(M.t/ms, M.v[0])

        ax[1].plot(M.t/ms, I_t(M.t), lw=1.2, c='k')
        ax[1].set_ylabel("Current (I)")
        ax[1].set_xlabel("Time (ms)")

        plt.title("Izhikevich neuron")
        plt.tight_layout()
        plt.show()


# Helper functions
def _require(cfg, path):
    cur = cfg
    for key in path:
        if key not in cur:
            raise KeyError(f"Missing key in config: {'/'.join(path)}")
        cur = cur[key]
    if cur is None:
        raise ValueError(f"Empty value for key: {'/'.join(path)}")
    return cur


def _require_positive(name, value):
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")


def validate_integrator(method: str):
    method = method.lower()
    try:
        # tiny dummy model just to test the method
        start_scope()
        test_eqs = "dv/dt = -v/(10*ms) : 1"
        _ = NeuronGroup(1, test_eqs, method=method)
        run(1*ms)

    except Exception:
        raise ValueError(
            f"Unsupported integrator '{method}'. "
            "Try one of: euler, rk2, rk4, heun, exponential euler, \nor visit Brian2 documentation for supported types."
        )

    return method
