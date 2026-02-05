"""
Smoke tests for SimpleNeuron Izhikevich simulator.

These tests ensure basic functionality works across different environments.
Run with: pytest tests/test_smoke.py
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path


def test_rs_neuron_runs():
    """Test that RS neuron simulation runs without errors."""
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "rs.yaml"

    result = subprocess.run(
        [sys.executable, "run.py", "-c", str(config_path), "--headless", "-v"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Combine stdout and stderr since logging might go to either
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Simulation failed with code {result.returncode}:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    assert "simulation complete" in output.lower(
    ), f"No completion message found in output:\n{output}"
    assert "spikes detected" in output.lower(
    ), f"No spike detection message found in output:\n{output}"


def test_rs_neuron_produces_spikes():
    """Test that RS neuron with I=10 produces spikes."""
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "rs.yaml"

    result = subprocess.run(
        [sys.executable, "run.py", "-c", str(config_path), "--headless", "-v"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Combine stdout and stderr
    output = result.stdout + result.stderr

    # Extract spike count from output
    for line in output.split('\n'):
        if 'simulation complete' in line.lower() and 'spikes detected' in line.lower():
            # Parse number from "simulation complete: N spikes detected"
            try:
                spike_count = int(line.split(
                    ':')[1].split('spikes')[0].strip())
                assert spike_count > 0, "RS neuron with I=10 should produce spikes"
                assert spike_count > 5, f"Expected multiple spikes, got {spike_count}"
                return
            except (ValueError, IndexError):
                pass  # Try next line

    assert False, f"Could not find spike count in output:\n{output}"


def test_logfile_creation():
    """Test that --logfile creates output file."""
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "rs.yaml"

    with tempfile.TemporaryDirectory() as tmpdir:
        logfile = Path(tmpdir) / "test_output.log"

        result = subprocess.run(
            [sys.executable, "run.py", "-c", str(config_path),
             "--headless", "-v", "--logfile", str(logfile)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Simulation failed: {result.stderr}"
        assert logfile.exists(), "Log file was not created"

        # Check log file contains expected content
        log_content = logfile.read_text()
        assert "simulation complete" in log_content.lower()
        assert "spikes detected" in log_content.lower()


def test_all_neuron_types_run():
    """Test that all pre-configured neuron types can run."""
    repo_root = Path(__file__).parent.parent
    config_dir = repo_root / "config"

    neuron_types = ['rs.yaml', 'fs.yaml', 'ib.yaml', 'ch.yaml',
                    'lts.yaml', 'rz.yaml', 'tc.yaml']

    for config_file in neuron_types:
        config_path = config_dir / config_file
        if not config_path.exists():
            continue

        result = subprocess.run(
            [sys.executable, "run.py", "-c", str(config_path), "--headless"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, \
            f"{config_file} failed to run: {result.stderr}"


def test_invalid_config_fails_gracefully():
    """Test that invalid config produces helpful error."""
    repo_root = Path(__file__).parent.parent

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content:")
        invalid_config = f.name

    try:
        result = subprocess.run(
            [sys.executable, "run.py", "-c", invalid_config, "--headless"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode != 0, "Should fail with invalid config"
        # Just check it doesn't crash spectacularly
        assert len(result.stderr) > 0 or len(result.stdout) > 0
    finally:
        os.unlink(invalid_config)


if __name__ == "__main__":
    # Allow running tests directly
    print("Running smoke tests...")
    test_rs_neuron_runs()
    print("✓ RS neuron runs")

    test_rs_neuron_produces_spikes()
    print("✓ RS neuron produces spikes")

    test_logfile_creation()
    print("✓ Logfile creation works")

    test_all_neuron_types_run()
    print("✓ All neuron types run")

    test_invalid_config_fails_gracefully()
    print("✓ Invalid config fails gracefully")

    print("\nAll smoke tests passed!")
