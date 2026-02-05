# Developer Guide

This guide helps you understand and modify the backend code.

## Project Structure

```
SimpleNeuron_Izhekevich/
├── models/
│   └── izhikevich.py      # Core neuron model implementation
├── config/                 # YAML configuration files
├── run.py                  # CLI entry point with parse_arguments(), configure_logging(), main()
├── tests/                  # Smoke tests for CI/CD
├── requirements.txt        # Dependencies
└── .github/workflows/      # GitHub Actions CI
```

## Core Components

### `run.py`

CLI entry point with clean separation of concerns:

**`parse_arguments()`** - Handles argparse setup
- `--config/-c`: Path to YAML file (required)
- `--verbose/-v`: Enable spike/event logging
- `--logfile`: Write logs to file
- `--headless`: Run without plot display (for CI/testing)

**`configure_logging(args)`** - Sets up Python logging
- INFO level for verbose, WARNING otherwise
- File or console output based on `--logfile`

**`main()`** - Orchestrates the simulation
- Parses arguments
- Sets matplotlib backend to 'Agg' for headless mode (prevents GUI crashes)
- Configures logging
- Loads neuron from YAML
- Runs simulation with `show_plot=not args.headless`

**Why both matplotlib backend AND show_plot?**
- `matplotlib.use('Agg')` = Prevents crashes in environments without display server (CI/Docker)
- `show_plot=False` = Skips calling `plt.show()` to avoid blocking execution

### `models/izhikevich.py`

The main neuron model class with key methods:

**`from_yaml(path)`** - Loads configuration from YAML file
- Parses neuron parameters (a, b, c, d)
- Builds stimulus from components
- Sets up simulation parameters
- Supports optional `verbose` flag in config

**`run(show_plot=True)`** - Executes the simulation
- Creates TimedArray for dimensionless input current
- Defines Izhikevich differential equations:
  ```
  dv/dt = (0.04*v² + 5*v + 140 - u + I(t)) / ms
  du/dt = a*(b*v - u) / ms
  ```
- Uses Brian2's NeuronGroup for numerical integration
- SpikeMonitor for spike detection and verbose logging
- Conditional plot display based on `show_plot` parameter
- Plots results using matplotlib (with Agg backend for headless)

### Current Units

Input currents are **dimensionless** (arbitrary units) in the config files. This matches the original Izhikevich (2003) formulation where `I=10` is the standard example. Values should be interpreted phenomenologically rather than as direct electrophysiological measurements.

### Integration Methods

Supported integrators (set in `simulation.integrator`):
- all supported by Brian2, as the Backend is supported by Brian2.

## Adding New Features

### New Stimulus Types

Currently only `step` stimuli are supported. To add new types (e.g., ramps, sine waves):

1. Add stimulus building logic in `models/izhikevich.py` `run()` method where TimedArray is constructed
2. Parse new parameters in `from_yaml()` method
3. Update YAML schema documentation in README.md
4. Add example config in `config/` directory
5. Update tests to verify new stimulus types work

### Network Support

To add multi-neuron networks:

1. Modify `NeuronGroup(1, ...)` to accept N neurons
2. Add synaptic connections using Brian2's `Synapses`
3. Update config schema to define network topology

### Custom Neuron Models

To implement other neuron models (e.g., Hodgkin-Huxley):

1. Create new class in `models/` directory
2. Follow same interface: `from_yaml()` and `run()`
3. Update `run.py` to support model selection

## Tips

- **Brian2 Units**: Always attach units to time/voltage (`ms`, `mV`); currents are dimensionless
- **Debugging**: Run with `--verbose` to see spike times, or use `print(G.v[:], G.u[:])` to inspect state
- **Performance**: Use `euler` integrator for quick tests, `rk4` for accuracy
- **Plotting**: Modify plot styling in `models/izhikevich.py` `run()` method
- **Testing**: Run `pytest tests/test_smoke.py` locally before pushing to verify CI will pass
- **Headless Mode**: Always use `--headless` in CI/batch scripts to avoid GUI dependencies

## Resources

- [Brian2 Documentation](https://brian2.readthedocs.io/)
- [Izhikevich Model Details](https://www.izhikevich.org/publications/spikes.htm)
- [Bifurcation Theory Background](https://en.wikipedia.org/wiki/Bifurcation_theory)

## Questions?

Open an issue on GitHub if you need help modifying the backend!
