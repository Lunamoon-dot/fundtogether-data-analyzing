"""Versioned binary-signal likelihoods, isolated from game behavior."""

from . import V1_MODEL_VERSION, V2_MODEL_VERSION, V3_MODEL_VERSION, V32_MODEL_VERSION, V33_MODEL_VERSION


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def signal_parameters(config):
    if config.model_version == V1_MODEL_VERSION:
        return (config.a, config.a), ((config.b, config.b),) * 3
    if config.model_version in (V2_MODEL_VERSION, V3_MODEL_VERSION, V32_MODEL_VERSION, V33_MODEL_VERSION):
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


def verification_probability(config, y, audit, verification):
    audit_mass = config.audit_probability if audit else 1 - config.audit_probability
    return audit_mass * likelihood(verification, y, config.verification_sensitivity, config.verification_specificity)


def verification_likelihood(config, y, verification):
    return likelihood(verification, y, config.verification_sensitivity, config.verification_specificity)


def audit_probability_for_report(config, report):
    if config.model_version in (V32_MODEL_VERSION, V33_MODEL_VERSION):
        return config.audit_probability_by_report[report]
    return config.audit_probability


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

    result = {
        "public_signal": one(public),
        "judges": {judge: {"private_signal": one(pair)} for judge, pair in zip(("A", "B", "C"), private)},
    }
    if config.model_version == V3_MODEL_VERSION:
        result["verification_anchor"] = one((config.verification_sensitivity, config.verification_specificity))
        result["verification_anchor"]["audit_probability"] = config.audit_probability
    elif config.model_version in (V32_MODEL_VERSION, V33_MODEL_VERSION):
        result["verification_anchor"] = one((config.verification_sensitivity, config.verification_specificity))
        result["verification_anchor"]["audit_probability_by_report"] = {
            "0": config.audit_probability_by_report[0], "1": config.audit_probability_by_report[1]
        }
        if config.model_version == V33_MODEL_VERSION:
            result["verification_anchor"]["audit_reward_mode"] = config.audit_reward_mode
    return result
