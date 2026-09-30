# AI Disclosure

This project uses AI-assisted technologies during development and within the application.

- **AI Model Used:** GPT-OSS-20B, accessed through the Groq API.
- **Purpose in the Application:** The model is used in the P2 Neural Understanding layer to interpret natural-language user complaints, identify the relevant problem domain and canonical problem, estimate confidence, and request clarification when the input is ambiguous.
- **Decision & Safety Logic:** The AI model does not generate or independently execute troubleshooting steps. Troubleshooting plans, risk classification, validation, and action execution are handled by deterministic backend logic and predefined scenario data.
- **Development Assistance:** AI tools were also used to assist with coding, debugging, documentation, and integration during development.
- **Human Oversight:** The project architecture, implementation, testing, integration, and final decisions were reviewed and controlled by the development team.
