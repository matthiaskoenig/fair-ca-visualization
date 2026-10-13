![fair-ca-visualization logo](https://github.com/matthiaskoenig/fair-ca-visualization/raw/develop/docs/images/fair-ca-logo.png)

# fair-ca-visualization

[![GitHub Actions CI/CD Status](https://github.com/matthiaskoenig/fair-ca-visualization/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/matthiaskoenig/fair-ca-visualization/actions/workflows/ci-cd.yml) [![Documentation](https://img.shields.io/badge/docs-fair--ca--visualization-008080.svg)](https://matthiaskoenig.github.io/fair-ca-visualization) [![Version](https://img.shields.io/pypi/v/fair-ca-visualization.svg)](https://pypi.org/project/fair-ca-visualization/) [![Python Versions](https://img.shields.io/pypi/pyversions/fair-ca-visualization.svg)](https://pypi.org/project/fair-ca-visualization/) [![MIT License](https://img.shields.io/pypi/l/fair-ca-visualization.svg)](https://opensource.org/licenses/MIT) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)

Computational models are essential tools for studying complex systems which, particularly in clinical settings, need to be quality-approved and transparent. A community-driven approach to enhance the transparency and communication of model features is adherence to the principles of Findability, Accessibility, Interoperability and Reusability (FAIR). The FAIR COMBINE Archive Indicators (FAIR-CA) adapt the FAIR indicators published by the Research Data Alliance to assess the FAIRness of models encoded in domain-specific standards, such as those established by [COMBINE](https://co.mbine.org).

The FAIR COMBINE Archive Indicators project is available from [https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io](https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io) and described in

> Balaur I., Nickerson D.P., Welter D., Wodke J.A.H., Ancien F., Gebhardt T., Grouès V., Hermjakob H., König M., Radde N., Rougny A., Schneider R., Malik-Sheriff R.S., Shiferaw K.B., Stefan M., Satagopam V., Waltemath D. (2026). A system for FAIR assessment of computational biology models and simulations based on RDA indicators. npj Systems Biology and Applications. [doi:10.1038/s41540-026-00828-7](https://doi.org/10.1038/s41540-026-00828-7)

`fair-ca-visualization` visualizes FAIR-CA assessments interactively. The app is available from https://faircombine.streamlit.app, the documentation from https://matthiaskoenig.github.io/fair-ca-visualization.

[![The fair-ca-visualization app](https://github.com/matthiaskoenig/fair-ca-visualization/raw/develop/docs/images/fair-ca-example.png)](https://faircombine.streamlit.app)

# Installation

To run the app locally, install the package from [PyPI](https://pypi.org/project/fair-ca-visualization/) (python 3.14) and start it with `fairvis`:

```bash
uv tool install fair-ca-visualization
fairvis
```

See the [installation guide](https://matthiaskoenig.github.io/fair-ca-visualization/installation/) for pip and for running from a checkout, and [contributing](https://matthiaskoenig.github.io/fair-ca-visualization/development/) for the development setup.

# How to cite

If you use the FAIR COMBINE Archive Indicators, please cite the publication above. If you use `fair-ca-visualization`, please also cite the software:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)

> König M. fair-ca-visualization: interactive visualization of the FAIR COMBINE Archive Indicators. Zenodo. [doi:10.5281/zenodo.13755820](https://doi.org/10.5281/zenodo.13755820)

```bibtex
@article{balaur2026,
  author  = {Balaur, Irina and Nickerson, David P. and Welter, Danielle and Wodke, Judith A. H. and Ancien, Francois and Gebhardt, Tom and Grou{\`e}s, Valentin and Hermjakob, Henning and K{\"o}nig, Matthias and Radde, Nicole and Rougny, Adrien and Schneider, Reinhard and Malik-Sheriff, Rahuman S. and Shiferaw, Kirubel Biruk and Stefan, Melanie and Satagopam, Venkata and Waltemath, Dagmar},
  title   = {A system for {FAIR} assessment of computational biology models and simulations based on {RDA} indicators},
  journal = {npj Systems Biology and Applications},
  year    = {2026},
  doi     = {10.1038/s41540-026-00828-7}
}

@software{fair_ca_visualization,
  author    = {König, Matthias},
  title     = {fair-ca-visualization: interactive visualization of the FAIR COMBINE Archive Indicators},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.13755820},
  url       = {https://doi.org/10.5281/zenodo.13755820}
}
```

# License

- Source Code: [MIT](https://opensource.org/license/MIT)
- Documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

# Funding

Matthias König (MK) was supported by the Federal Ministry of Education and Research (BMBF, Germany) within the research network Systems Medicine of the Liver (LiSyM, grant number 031L0054). MK is supported by the Federal Ministry of Education and Research (BMBF, Germany) within ATLAS by grant number 031L0304B and by the German Research Foundation (DFG) within the Research Unit Program FOR 5151 QuaLiPerF (Quantifying Liver Perfusion-Function Relationship in Complex Resection - A Systems Medicine Approach) by grant number 436883643 and by grant number 465194077 (Priority Programme SPP 2311, Subproject SimLivA).

© 2024 - 2026 Matthias König
