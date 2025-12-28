---
description: Implement a new feature following the project's engineering standards
---

1. **Analyze Requirements**: Review `docs/FEATURE-PLAN.md`, `docs/TECHINICAL-SPEC.md`, and the existing codebase to understand the new feature's context and requirements.
2. **Implementation Plan**: Present a detailed implementation plan to the user, including:
    - Technical approach and key components.
    - Step-by-step implementation order.
    - Testing strategy (unit, integration, and E2E).
    - Important tradeoffs (explained in plain language).
3. **Wait for Approval**: Stop and wait for the user to explicitly approve the plan (e.g., "ok", "approved").
4. **Execute & Deliver**: Once approved, implement the feature completely:
    - **Production-Ready**: Build only production-ready code. Do NOT use placeholders or "TODO" comments unless explicitly requested.
    - **No Placeholders**: If assets (images, data) are needed, generate or find real examples.
    - **Complexity Alert**: If an implementation detail becomes significantly more complex than initially planned, pause and ask for user confirmation before proceeding.
    - Follow PEP 8 for Python and maintain high code quality.
    - Ensure robust error handling with user-friendly messages.
    - Verify with automated tests before presenting.
5. **Document**: 
    - Create a directory `docs/<feature-name>/`.
    - Add `README.md` (high-level overview and setup).
    - Add `<FEATURE_NAME>.md` (technical specs, architecture, and API details).
    - Update all relevant document `FEATURE-PLAN.md`, `TECHINICAL-SPEC.md`, `README.md`, and `CLAUDE.MD` to make sure feature status is updated and new document reference is added. 
6. **Show Results**: Demonstrate the working feature to the user, explaining both technical and user-facing perspectives.