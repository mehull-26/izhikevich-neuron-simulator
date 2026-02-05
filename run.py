import argparse
import logging
from models.izhikevich import IzhikevichNeuron


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run Izhikevich neuron simulation from YAML config'
    )
    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Path to YAML configuration file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (spike times and events)'
    )
    parser.add_argument(
        '--logfile',
        type=str,
        help='Write log output to file instead of console'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run without displaying plots (for testing/batch processing)'
    )
    return parser.parse_args()


def configure_logging(args):
    """Configure logging based on arguments."""
    level = logging.INFO if args.verbose else logging.WARNING
    log_config = {
        'level': level,
        'format': '%(message)s'
    }
    if args.logfile:
        log_config['filename'] = args.logfile
        log_config['filemode'] = 'w'
    logging.basicConfig(**log_config)


# MAIN FUNCTION
def main():
    args = parse_arguments()

    # Set non-interactive backend for headless environments (prevents GUI crashes)
    if args.headless:
        import matplotlib
        matplotlib.use('Agg')

    configure_logging(args)

    neuron = IzhikevichNeuron.from_yaml(args.config)
    if args.verbose:
        neuron.verbose = True

    neuron.run(show_plot=not args.headless)


if __name__ == "__main__":
    main()
