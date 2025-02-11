"""Example to test visualization."""

from data_io import load_assessment
from settings import DATA_PATH
from visualization import visualize_barplot

if __name__ == "__main__":
    model_id = "BioModels_curated"
    df = load_assessment(DATA_PATH / "assessments" / f"{model_id}.xlsx")

    # barplot
    fig = visualize_barplot(df)
    fig.show()

    # polar barplots
    # figs, keys = visualize_polar_barplots(df)
    # figs[0].show()
