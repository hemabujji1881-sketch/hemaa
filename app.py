
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(
    page_title="Student Details Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Details Analytics Dashboard")
st.markdown("Explore student information with interactive charts and filters.")

# ---------------- SAMPLE DATA ----------------
@st.cache_data
def sample_data():
    return pd.DataFrame({
        "Student Name": [
            "Arun", "Priya", "Rahul", "Sneha", "Kiran",
            "Divya", "Ravi", "Anjali", "Vijay", "Meena",
            "Suresh", "Pooja", "Naveen", "Kavya", "Manoj",
            "Harika", "Sai", "Lakshmi", "Ramesh", "Teja"
        ],
        "Father Name": [
            "Ramesh", "Kumar", "Srinivas", "Mohan", "Raju",
            "Suresh", "Krishna", "Ravi", "Mohan", "Raju",
            "Prasad", "Ravi", "Kumar", "Ramesh", "Siva",
            "Mohan", "Raju", "Kiran", "Suresh", "Prasad"
        ],
        "Gender": [
            "Male", "Female", "Male", "Female", "Male",
            "Female", "Male", "Female", "Male", "Female",
            "Male", "Female", "Male", "Female", "Male",
            "Female", "Male", "Female", "Male", "Male"
        ],
        "Age": [
            18, 19, 20, 18, 21, 19, 20, 18, 22, 19,
            21, 20, 18, 22, 19, 20, 21, 18, 22, 20
        ],
        "Address": [
            "Anantapur", "Hyderabad", "Penukonda", "Bengaluru",
            "Dharmavaram", "Hyderabad", "Hindupur", "Chennai",
            "Anantapur", "Bengaluru", "Penukonda", "Chennai",
            "Hyderabad", "Dharmavaram", "Hindupur", "Anantapur",
            "Bengaluru", "Hyderabad", "Chennai", "Penukonda"
        ],
        "Marks": [
            85, 92, 74, 88, 67, 95, 72, 90, 81, 86,
            69, 93, 78, 89, 76, 96, 83, 87, 71, 91
        ]
    })

# ---------------- DATA UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader(
    "Upload student CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully!")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()
else:
    df = sample_data()
    st.sidebar.info("Showing sample student data.")

# ---------------- DATA PREPARATION ----------------
required_columns = [
    "Student Name", "Father Name", "Gender",
    "Age", "Address", "Marks"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(
        "Your CSV is missing these required columns: "
        + ", ".join(missing)
    )
    st.info(
        "Required columns: " + ", ".join(required_columns)
    )
    st.stop()

df = df[required_columns].copy()
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Marks"] = pd.to_numeric(df["Marks"], errors="coerce")
df = df.dropna(subset=["Age", "Marks", "Gender", "Address"])
df["Gender"] = df["Gender"].astype(str)
df["Address"] = df["Address"].astype(str)
df["Student Name"] = df["Student Name"].fillna("Unknown")
df["Father Name"] = df["Father Name"].fillna("Unknown")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Dashboard Filters")

genders = sorted(df["Gender"].unique().tolist())
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    genders,
    default=genders
)

addresses = sorted(df["Address"].unique().tolist())
selected_addresses = st.sidebar.multiselect(
    "Select Address",
    addresses,
    default=addresses
)

age_min = int(df["Age"].min()) if not df.empty else 0
age_max = int(df["Age"].max()) if not df.empty else 0

age_range = st.sidebar.slider(
    "Select Age Range",
    min_value=age_min,
    max_value=max(age_max, age_min),
    value=(age_min, age_max)
)

mark_min = int(df["Marks"].min()) if not df.empty else 0
mark_max = int(df["Marks"].max()) if not df.empty else 100

marks_range = st.sidebar.slider(
    "Select Marks Range",
    min_value=mark_min,
    max_value=max(mark_max, mark_min),
    value=(mark_min, mark_max)
)

# Apply all filters to one shared DataFrame
filtered_df = df[
    df["Gender"].isin(selected_genders)
    & df["Address"].isin(selected_addresses)
    & df["Age"].between(age_range[0], age_range[1])
    & df["Marks"].between(marks_range[0], marks_range[1])
].copy()

# ---------------- KPI CARDS ----------------
st.subheader("📌 Student Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Students", len(filtered_df))
c2.metric(
    "Average Age",
    f"{filtered_df['Age'].mean():.1f}"
    if not filtered_df.empty else "N/A"
)
c3.metric(
    "Average Marks",
    f"{filtered_df['Marks'].mean():.1f}"
    if not filtered_df.empty else "N/A"
)
c4.metric(
    "Locations",
    filtered_df["Address"].nunique()
)

if filtered_df.empty:
    st.warning("No students match the selected filters.")
    st.stop()

# ---------------- BAR CHART ----------------
st.subheader("📊 Student Count by Address")

location_counts = (
    filtered_df.groupby("Address")
    .size()
    .reset_index(name="Students")
)

fig_bar = px.bar(
    location_counts,
    x="Address",
    y="Students",
    color="Address",
    text="Students",
    title="Students in Each Location"
)
st.plotly_chart(fig_bar, use_container_width=True)

# ---------------- PIE CHART ----------------
left, right = st.columns(2)

with left:
    st.subheader("🥧 Gender Distribution")
    gender_counts = (
        filtered_df.groupby("Gender")
        .size()
        .reset_index(name="Students")
    )
    fig_pie = px.pie(
        gender_counts,
        names="Gender",
        values="Students",
        hole=0.35,
        title="Students by Gender"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ---------------- HISTOGRAM ----------------
with right:
    st.subheader("📈 Age Distribution")
    fig_hist = px.histogram(
        filtered_df,
        x="Age",
        nbins=10,
        color="Gender",
        title="Distribution of Student Ages"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------------- LINE CHART ----------------
st.subheader("📉 Average Marks by Age")

age_marks = (
    filtered_df.groupby("Age", as_index=False)["Marks"]
    .mean()
    .sort_values("Age")
)

fig_line = px.line(
    age_marks,
    x="Age",
    y="Marks",
    markers=True,
    title="Average Marks Across Ages"
)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------- SCATTER PLOT ----------------
st.subheader("🔵 Age vs Marks")

fig_scatter = px.scatter(
    filtered_df,
    x="Age",
    y="Marks",
    color="Gender",
    hover_data=["Student Name", "Address"],
    title="Student Performance Comparison"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------- BOX PLOT ----------------
st.subheader("📦 Marks Distribution by Gender")

fig_box = px.box(
    filtered_df,
    x="Gender",
    y="Marks",
    color="Gender",
    points="all",
    title="Marks Spread by Gender"
)
st.plotly_chart(fig_box, use_container_width=True)

# ---------------- STUDENT TABLE ----------------
st.subheader("📋 Filtered Student Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ---------------- DOWNLOAD ----------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Student Data",
    data=csv_data,
    file_name="filtered_student_details.csv",
    mime="text/csv"
)

st.caption("Student Details Dashboard | Built with Python and Streamlit")
