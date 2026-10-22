"""Versioned binary-signal likelihoods, isolated from game behavior."""

from . import V1_MODEL_VERSION, V2_MODEL_VERSION


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return specificity if value else 1 - specificity
    return specificity if not value else 1 - specificity


def signal_parameters(config):
    if config.model_version == V1_MODEL_VERSION:
        return (config.a, config.a), ((config.b, config.b),) * 3
    if config.model_version == V2_MODEL_VERSION:
        public = (config.public_sensitivity, config.public_specificity)
        private = tuple(zip(config.private_sensitivities, config.private_specificities))
        return public, private
    raise ValueError("Unsupported validated model version")


def state_probability(config, y, z, signals):
    public, private = signal_parameters(config)
    mass = config.pi if y else 1 - config.pi
    mass *= likelihood(z, y, *public)
    for value, pair in zip(signals, private):
        mass *= likelihood(value, y, *pair)
    return mass


def diagnostics(config):
    public, private = signal_parameters(config)

    def one(pair):
        sensitivity, specificity = pair
        return {
            "sensitivity": sensitivity,
            "specificity": specificity,
            "false_negative_rate": 1 - sensitivity,
            "false_positive_rate": 1 - specificity,
            "prior_weighted_accuracy": config.pi * sensitivity + (1 - config.pi) * specificity,
        }

    return {
        "public_signal": one(public),
        "judges": {judge: {"private_signal": one(pair)} for judge, pair in zip(("A", "B", "C"), private)},
    }
