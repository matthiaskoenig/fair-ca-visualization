# Using the app

The app has four tabs. Only the selected tab is computed, and every tab has its own link: the tab is part of the address, e.g., [faircombine.streamlit.app/?tab=Indicators](https://faircombine.streamlit.app/?tab=Indicators), and on **Example Assessments** also the model, e.g., [?tab=Example+Assessments&model=PMR_curated](https://faircombine.streamlit.app/?tab=Example+Assessments&model=PMR_curated).

## About

The motivation of the FAIR COMBINE Archive Indicators, how to cite the publication and the app, and an example of the **Model** and **Model metadata** indicators of the `BioModels_C19_curated` assessment.

## Assess Model

Assess your own model:

1. Download the template with **Download FAIR template**.
2. Fill in the column `Assessment` for every indicator, see [Assessing a model](assessment.md).
3. Upload the filled template with **Upload FAIR model assessment**, at most 1 MB.

The app shows the FAIR percentage per category as a bar plot, one polar bar plot per type of indicator (Model, Model metadata, Archive, Archive metadata), and the table of the assessment. In the polar bar plots an indicator which does not apply to the model (NA) is a full gray bar, an indicator assessed with 0 has no bar; see [Scoring](assessment.md#scoring) for the percentages. A file which is not a filled template, misses or adds indicators, or has an assessment value other than empty, 0, 0.5 or 1 is reported as an error naming the columns or the indicators. Only the column `Assessment` is taken from the file, the description of the indicators always comes from the template. The uploaded file stays selected when you switch tabs.

The uploaded file is only processed in the running app: it is never written to disk, never shared with other users of the app and is discarded when you close the page.

## Example Assessments

The assessments bundled with the app, e.g., curated and non curated models of BioModels and the Physiome Model Repository and published pharmacokinetic models. Select a model to show the same plots as for an uploaded assessment.

## Indicators

All indicators of the template with their identifier, short label, type, category, priority and the question the indicator asks. The columns **NA**, **0**, **0.5** and **1** count the example assessments which rate the indicator with that value.
