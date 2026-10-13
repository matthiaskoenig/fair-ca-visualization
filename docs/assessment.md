# Assessing a model

An assessment is the FAIR assessment template, `FAIR_assessment_template.xlsx`, with the column `Assessment` filled in. Download it in the app (**Assess Model**, **Download FAIR Template**) or from [the repository](https://github.com/matthiaskoenig/fair-ca-visualization/raw/develop/src/fairvis/data/FAIR_assessment_template.xlsx).

## Columns

The first sheet has one row per indicator:

| Column | Content |
|---|---|
| `ID` | identifier of the indicator, e.g., `CA-RDA-F1-01M` |
| `Short` | short label used in the polar plots |
| `Type` | Model, Model metadata, Archive or Archive metadata; one polar plot per type |
| `Category` | Findable, Accessible, Interoperable or Reusable |
| `Subcategory` | the FAIR principle, e.g., F1 |
| `Priority` | Essential, Important or Useful |
| `Indicator` | the question the indicator asks |
| `Description` | explanation of the indicator |
| `Assessment details` | how to assess the indicator |
| `Assessment` | your assessment, see below |
| `Comment` | optional free text |

Keep the rows and the columns of the template; only fill in `Assessment` and, if you like, `Comment`.

## Scoring

| `Assessment` | Meaning |
|---|---|
| empty | NA, the indicator does not apply to the model |
| `0` | not fulfilled |
| `0.5` | partially fulfilled |
| `1` | fulfilled |

The bar plot shows per category the sum of the assessments divided by the number of indicators of the category, in percent; NA counts as not fulfilled.
