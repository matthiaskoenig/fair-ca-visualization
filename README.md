![fair-ca-visualization logo](https://github.com/matthiaskoenig/fair-ca-visualization/raw/main/docs/fair-ca-logo.png)

# fair-ca-visualization
Computational models are essential tools for studying complex systems which,
particularly in clinical settings, need to be quality-approved and transparent.
A community-driven approach to enhance the transparency and communication of
model features is adherence to the principles of Findability, Accessibility,
Interoperability and Reusability (FAIR). We propose here an adaptation of the
FAIR indicators published by the Research Data Alliance to assess the
FAIRness of models encoded in domain-specific standards, such as those
established by [COMBINE](https://co.mbine.org).

The FAIR COMBINE Archive Indicators project is available from [https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io](https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io).

The visualization tool is available from: https://faircombine.streamlit.app/

[![./docs/fair-ca-example.png](./docs/fair-ca-example.png)](https://faircombine.streamlit.app/)

# How to cite
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)

# Local installation
The app has been implemented as streamlit application and can be run locally.

Clone the repository
```bash
git clone https://github.com/matthiaskoenig/fair-ca-visualization.git
cd fair-ca-visualization
```

Setup environment
```bash
uv sync
```

Run the application
```bash
uv run streamlit run src/fairvis/app.py
```
or use the shortcut
```bash
./run_app.sh
```

# Development
## Setup pre-commit
```bash
uv pip install pre-commit
uv run pre-commit install
uv run pre-commit run
```

# License

* Source Code: [MIT](https://opensource.org/license/MIT)
* Documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

# Funding
Matthias König (MK) was supported by the Federal Ministry of Education and Research
(BMBF, Germany) within the research network Systems Medicine of the Liver
(LiSyM, grant number 031L0054). MK is supported by the Federal Ministry of
Education and Research (BMBF, Germany) within ATLAS by grant number 031L0304B and
by the German Research Foundation (DFG) within the Research Unit Program FOR 5151
QuaLiPerF (Quantifying Liver Perfusion-Function Relationship in Complex Resection -
A Systems Medicine Approach) by grant number 436883643 and by grant number
465194077 (Priority Programme SPP 2311, Subproject SimLivA).

© 2024 - 2026 Matthias König
