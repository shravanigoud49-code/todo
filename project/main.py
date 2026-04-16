import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Task Manager", layout="centered")

# Title
st.title("🧠 Smart Task Manager")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------------- ADD TASK ----------------
st.subheader("➕ Add New Task")

task_name = st.text_input("Task Name")
priority = st.selectbox("Priority", ["Low", "Medium", "High"])
due_date = st.date_input("Due Date")

if st.button("Add Task"):
    if task_name:
        st.session_state.tasks.append({
            "Task": task_name,
            "Priority": priority,
            "Due Date": due_date,
            "Status": "Pending",
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        st.success("Task Added Successfully!")
    else:
        st.warning("Please enter task name")

# ---------------- DISPLAY TASKS ----------------
st.subheader("📋 Your Tasks")

if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)

    # Filter
    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

    if status_filter != "All":
        df = df[df["Status"] == status_filter]

    st.dataframe(df, use_container_width=True)

    # ---------------- MARK COMPLETE ----------------
    st.subheader("✅ Update Task Status")

    task_index = st.selectbox("Select Task", range(len(st.session_state.tasks)))

    if st.button("Mark as Completed"):
        st.session_state.tasks[task_index]["Status"] = "Completed"
        st.success("Task marked as completed!")
        st.rerun()

    # ---------------- DELETE TASK ----------------
    st.subheader("🗑 Delete Task")

    delete_index = st.selectbox("Select Task to Delete", range(len(st.session_state.tasks)), key="delete")

    if st.button("Delete Task"):
        st.session_state.tasks.pop(delete_index)
        st.warning("Task deleted!")
        st.rerun()

else:
    st.info("No tasks added yet!")

# ---------------- DOWNLOAD ----------------
st.subheader("⬇ Download Tasks")

if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="tasks.csv",
        mime="text/csv"
    )
