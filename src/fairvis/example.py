"""Example showing the figures of a bundled assessment in the browser."""

from fairvis.data_io import load_assessment
from fairvis.settings import ASSESSMENTS_PATH
from fairvis.visualization import visualize_barplot, visualize_polar_barplots

if __name__ == "__main__":
    df = load_assessment(ASSESSMENTS_PATH / "BioModels_curated.xlsx")
    visualize_barplot(df).show()
    visualize_polar_barplots(df)[0].show()
