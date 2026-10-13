# Initial milestone verification

Observed in the authoring environment: Python 3.12, Django 5.2.18, PyJWT 2.15.1; helper built into a wheel and installed with pip. Three Django HTTP processes started with fresh seeded databases.

Eight integration tests passed in the initial run:
1. Create/save/read; cross-user denial; administrator read.
2. Own-only listing.
3. Ordinary deletion denial; administrator deletion; disappearance after deletion.
4. B's create authority cannot delete; result remains.
5. Expired administrator/wrong-audience token rejection; result remains.
6. Invalid signature text and unexpected owner field rejection.
7. Oversized direct B input rejection.
8. Forged token rejection.

These checks validate the stub-backed milestone only. They are not evidence of real Ollama integration, a complete security assessment, planted vulnerability experiments, Jenkins operation, or Docker execution. Those are still pending.
