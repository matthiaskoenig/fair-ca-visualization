# API reference

The package `fairvis` contains the app and the functions it is built from. They can be used to load and plot assessments in a script or notebook:

```python
from fairvis.data_io import load_assessment
from fairvis.visualization import visualize_barplot

df = load_assessment("my_assessment.xlsx")
visualize_barplot(df).show()
```

| Module | Content |
|---|---|
| [`fairvis.cli`](cli.md) | the `fairvis` command which starts the app |
| [`fairvis.data_io`](data_io.md) | loading and validating assessments, counting the assessments of the indicators |
| [`fairvis.visualization`](visualization.md) | the plotly figures |
| [`fairvis.settings`](settings.md) | paths of the app and the bundled data |
| [`fairvis.console`](console.md) | the rich console for logging |
