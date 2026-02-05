import argparse
from models.izhikevich import IzhikevichNeuron


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", required=True,
                        help="Path to YAML configuration file")
    args = parser.parse_args()

    neuron = IzhikevichNeuron.from_yaml(args.config)
    neuron.run()


if __name__ == "__main__":
    main()
