# Adding an example assessment

The example assessments of the app are xlsx files in `src/fairvis/data/assessments/`, one per model, bundled with the package. To add one:

1. Fill in the template, see [Assessing a model](assessment.md), and check it by uploading it in the app.
2. Name it `<Author><Year>_<substance>.xlsx` for a published model, e.g., `Elias2025_glimepiride.xlsx`, or `<Repository>_<selection>.xlsx` for a collection, e.g., `BioModels_curated.xlsx`. The name without `.xlsx` is the model id shown in the app; the models are listed in alphabetical order.
3. Copy it to `src/fairvis/data/assessments/`.
4. Run the tests, which load every assessment, compare its indicators with the template and render it in the app:

```bash
uv run pytest -n auto
```

5. Open a pull request against `develop`, see [Contributing](development.md).
