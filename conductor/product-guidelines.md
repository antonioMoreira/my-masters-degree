# Product Guidelines

## Documentation & Prose Style
- **Tone:** Academic and Formal.
- **Style:** Documentation and code comments should provide detailed explanations, making explicit connections to linguistic theories and the DailyTalk reference paper.

## Privacy & Security
- **Inherited Anonymity:** The project relies on the privacy protections already implemented in the original MuPe dataset. No further redaction logic is required, but care must be taken to preserve these existing protections.

## Quality Standards
- **Audio Fidelity:** High-fidelity processing is mandatory. Original sampling rates and bit depths from the MuPe source must be maintained throughout all concatenation and adaptation steps.
- **Validation:** Automated validation against DailyTalk metadata specifications is required for every dataset version.

## Architecture & Reproducibility
- **Modular Pipeline:** The codebase must be organized into distinct, modular components (e.g., filtering, audio processing, validation).
- **Configuration:** Use external configuration files to manage parameters, ensuring experiments can be reproduced without modifying core logic.

## Research Validation (TTS)
- **Primary Metric:** Conversational Prosody.
- **Focus:** The synthesized output must be evaluated primarily on its ability to capture dialogue-specific features such as turn-taking, pauses, and natural conversational flow in Portuguese.
