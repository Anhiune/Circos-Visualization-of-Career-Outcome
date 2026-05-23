from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Career Major Dashboard",
    page_icon="C",
    layout="wide",
)


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "Major_Job_Cluster_Lookup_Filtered.csv"
DIAGRAM_CANDIDATES = [
    ROOT / "circos_working" / "circos.svg",
    ROOT / "circos_working" / "circos.png",
    ROOT / "circos" / "circos.png",
    ROOT / "Major_Job_Circos_Diagram_FIXED.png",
    ROOT / "Major_Job_Circos_Diagram.png",
    ROOT / "circos_diagram_hires.png",
    ROOT / "circos_diagram.png",
]


def find_first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def main() -> None:
    st.title("Career Major Dashboard")
    st.caption("Public-friendly viewer for the major-to-career diagram and source data.")

    if not DATA_FILE.exists():
        st.error(f"Missing data file: {DATA_FILE.name}")
        st.stop()

    df = load_data(DATA_FILE)
    diagram_path = find_first_existing(DIAGRAM_CANDIDATES)

    total_rows = len(df)
    major_count = df["Large Major Cluster"].nunique()
    career_count = df["Large Job Title Cluster"].nunique()

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Records", f"{total_rows:,}")
    metric_2.metric("Major Clusters", major_count)
    metric_3.metric("Career Clusters", career_count)

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Diagram")
        if diagram_path is None:
            st.warning("No SVG or PNG diagram was found in the project.")
        elif diagram_path.suffix.lower() == ".svg":
            st.image(str(diagram_path), use_container_width=True)
        else:
            st.image(str(diagram_path), use_container_width=True)

        if diagram_path is not None:
            with open(diagram_path, "rb") as file_obj:
                st.download_button(
                    label=f"Download {diagram_path.name}",
                    data=file_obj.read(),
                    file_name=diagram_path.name,
                    mime="image/svg+xml" if diagram_path.suffix.lower() == ".svg" else "image/png",
                )

    with right:
        st.subheader("Filters")
        selected_majors = st.multiselect(
            "Major clusters",
            sorted(df["Large Major Cluster"].dropna().unique().tolist()),
        )
        selected_jobs = st.multiselect(
            "Career clusters",
            sorted(df["Large Job Title Cluster"].dropna().unique().tolist()),
        )

        filtered = df.copy()
        if selected_majors:
            filtered = filtered[filtered["Large Major Cluster"].isin(selected_majors)]
        if selected_jobs:
            filtered = filtered[filtered["Large Job Title Cluster"].isin(selected_jobs)]

        summary = (
            filtered.groupby(["Large Major Cluster", "Large Job Title Cluster"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

        st.subheader("Top Flows")
        st.dataframe(summary.head(15), use_container_width=True, hide_index=True)

    st.subheader("Source Data")
    st.dataframe(filtered, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
