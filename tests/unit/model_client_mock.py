from unittest.mock import Mock

from harness.domain.context import ModelContextLimits


def allow_context(client: Mock) -> Mock:
    client.count_tokens.return_value = 1
    client.get_context_limits.return_value = ModelContextLimits(
        model="test-model",
        context_window=1_000,
        reserved_output_tokens=100
    )

    return client
