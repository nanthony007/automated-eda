import pandas as pd
import streamlit as st
from ydata_profiling import ProfileReport

st.set_page_config(page_title="Automated EDA", layout="wide")


def parse_dtype(
    x: str,
) -> str:
    """Convert pandas types (as strings) to pandas-profiling
    respected types (as strings) that are then passed to
    `visions` api"""
    match x:
        case "int64" | "float64":
            return "Numeric"
        case "string":
            return "Text"
        case "category":
            return "Categorical"
        case "datetime[ns]":
            return "Datetime"
        case _:
            raise ValueError(f"Unsupported datatype found: {x}")


PANDAS_DTYPE_OPTIONS: list[str] = [
    "bool",
    "int64",
    "float64",
    "datetime[ns]",
    "string",
    "category",
]
with st.sidebar:
    st.header("Automated EDA")
    st.markdown("""
This app uses [ydata-profiling](https://github.com/ydataai/ydata-profiling) (formerly pandas-profiling)
to generate automated EDA reports from uploaded datasets.

The Report _used to be_ previewed, but bugs in `st.to_html` led me to remove that.

It allows for the configuration of column data types which 
greatly improves the usability of the report.
""")
    st.caption("Supported dtype conversions")
    st.json(PANDAS_DTYPE_OPTIONS)


st.header("Automated EDA", divider=True)

st.caption("Upload a datafile to get started.")


st.markdown("""
Uploaded files should be <200MB, and either in CSV (.csv) or Excel (.xlsx) format. 
If you would like to see other file types supported, please [submit an issue](TODO: LINK). Similarly
if you would like to see more dtypes supported, submit an issue. The full list of dtype translations we 
currently perform is in the sidebar (left), with a full list of `pandas` dtypes available
[here](https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#dtypes)
Uploading multiple files will remove the Report Preview section and just make the files available
for download. 
""")


uploaded_files = st.file_uploader(
    label="Datafiles",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
)
if uploaded_files is not None:
    for file in uploaded_files:
        # load data and preview section
        if file.name.endswith(".csv"):
            df = pd.read_csv(
                file,
                low_memory=False,
            )
        elif file.name.endswith(".xlsx"):
            st.warning(f"WARNING: Only reading first sheet of excel file: {file.name}")
            df = pd.read_excel(
                file,
                engine="openpyxl",
            )
        else:
            raise ValueError(f"Unexpected file type {file.type} from {file.name}")
        st.header(f"File: {file.name}", divider=True)
        st.caption("File preview:")
        st.dataframe(df, use_container_width=True, hide_index=True)
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype("string")
        schema = df.dtypes.reset_index()
        schema.columns = ["Column Name", "Old Type"]
        schema["New Type"] = schema["Old Type"].astype(str)

        _, center, _ = st.columns([0.1, 0.8, 0.1])
        col1, col2 = center.columns(2, gap="small", vertical_alignment="center")
        col1.caption("Minimal report with minimal compute, good for fast reporting")
        minimal = col1.toggle(label="Minimal", value=False, key=f"{file.name}-minimal")
        col2.caption("More detailed reporting, takes longer but can be beneficial")
        explorative = col2.toggle(
            label="Explorative",
            value=True,
            key=f"{file.name}-explorative",
        )
        center.caption("Click on the New Type column/cell to edit the type!")
        new_schema_table = center.data_editor(
            schema,
            column_config={
                "Column Name": st.column_config.Column(
                    label="Column Name",
                    disabled=True,
                ),
                "Old Type": st.column_config.TextColumn(
                    "Old DataType",
                    disabled=True,
                ),
                "New Type": st.column_config.SelectboxColumn(
                    "New DataType",
                    help="New column type",
                    options=PANDAS_DTYPE_OPTIONS,
                    required=True,
                    disabled=False,
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
        new_schema = new_schema_table.set_index("Column Name").to_dict()["New Type"]
        for column, new_type in new_schema.items():
            if new_type != "datetime[ns]":
                df[column] = df[column].astype(new_type)
            else:
                df[column] = pd.to_datetime(
                    df[column],
                    format="mixed",
                    errors="raise",
                )
        report = ProfileReport(
            df,
            title=f"{file.name.split('.')[0].title()} Report",
            type_schema={k: parse_dtype(v) for k, v in new_schema.items()},
            minimal=minimal,
            explorative=explorative,
        )
        report_html = report.to_html()
        center.download_button(
            label="Download report",
            file_name=f"{file.name.split('.')[0].title()}-report.html",
            data=report_html,
            mime="text/plain",
            type="primary",
            use_container_width=True,
        )
