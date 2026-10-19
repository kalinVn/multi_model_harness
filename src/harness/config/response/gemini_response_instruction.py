from harness.config.response.groq_response_instruction import (
    GROQ_RESPONSE_INSTRUCTION,
)


# Gemini and Groq use the same native function-calling response protocol.
GEMINI_RESPONSE_INSTRUCTION = GROQ_RESPONSE_INSTRUCTION
