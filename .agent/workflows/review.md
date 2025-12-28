---
description: Perform a comprehensive code and architecture review of the entire project
---

1. **System Archeology**: Scan the entire codebase to map out the current architecture, data flow, and component relationships.
2. **Standard Alignment**: Review the code against the engineering standards and guiding principles defined in `CLAUDE.md` and `docs/TECHNICAL-SPEC.md`.
3. **Security & Robustness**:
    - Audit error handling across all modules.
    - Check data validation and sanitization for user inputs and API responses.
    - Identify any potential security vulnerabilities or rate-limiting issues.
4. **Architectural Assessment**:
    - Evaluate the modularity and separation of concerns (Collectors, Processors, Storage, Dashboard).
    - Identify any "leaky abstractions" or tight coupling between components.
    - Review database schema design for scalability and query efficiency.
5. **Technical Debt Audit**: Identify obsolete files, redundant code, or areas that deviate from the "Boring Technology" and "Simplicity First" principles.
6. **Summary Report**: Provide a detailed report covering:
    - **Strengths**: What is well-implemented.
    - **Critical Issues**: Immediate bugs or architectural flaws.
    - **Optimization Opportunities**: Performance and maintainability improvements.
    - **Action Plan**: Prioritized list of recommended changes.
