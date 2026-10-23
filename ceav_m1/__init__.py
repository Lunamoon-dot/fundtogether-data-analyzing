"""Exact analysis of the CEAV-M1 game; Python standard library only."""

V1_MODEL_VERSION = "ceav-m1-v1.0"
V2_MODEL_VERSION = "ceav-m1-v2.0"
V3_MODEL_VERSION = "ceav-m1-v3.0"
SUPPORTED_MODEL_VERSIONS = (V1_MODEL_VERSION, V2_MODEL_VERSION, V3_MODEL_VERSION)
DEFAULT_MODEL_VERSION = V3_MODEL_VERSION

# Compatibility alias for V1 imports. Runtime manifests use config.model_version.
MODEL_VERSION = V1_MODEL_VERSION
ENGINE_VERSION = "ceav-m1-engine-v3.1"
