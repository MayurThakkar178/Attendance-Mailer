import streamlit as st
import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Attendance Mailer", layout="centered")
st.title("📧 Attendance Mailer System")
st.write("Upload a CSV or Excel (.xlsx) file and automatically email students using roll numbers.")

# Upload file
uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

if uploaded_file:
    # Detect and read file format
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(df)

    st.subheader("✉️ Email Settings")
    sender_email = st.text_input("Sender Gmail", placeholder="example@gmail.com")
    app_password = st.text_input("App Password", type="password")

    subject = st.text_input("Email Subject", "Test Mail for Cloud Computing Assignment / Your Attendance Report")
    template = st.text_area("Email Template", 
        "Hi {name},\n\nHere is your attendance summary:\n\n{attendance}\n\nRegards,\nFaculty")

    if st.button("📬 Send Emails"):
        if not sender_email or not app_password:
            st.error("❗ Please enter both Gmail and App Password.")
        else:
            grouped = df.groupby(["Name", "Roll Number"])
            sent_count = 0
            skipped_count = 0

            for (name, roll), group in grouped:
                email = f"{roll}@nirmauni.ac.in"
                st.write(f"📤 Sending email to: {name} <{email}>")
                attendance_lines = []

                for _, row in group.iterrows():
                    try:
                        avg = float(str(row["Average"]).replace('%', '').strip())
                        if avg < 85:
                            course = row["Course Name"]
                            code = row["Course Code"]
                            present = row["Present"]
                            total = row["Total Sessions"]
                            attendance_lines.append(
                                f"| {course:<22} | {code:<12} | {present}/{total:<7} | {avg:.2f}%{'':<10} |"
                            )
                    except Exception as e:
                        st.warning(f"⚠️ Error processing row: {e}")
                        continue

                if attendance_lines:
                    table_header = (
                        "+------------------------+--------------+---------+-------------------+\n"
                        "| Course Name            | Course Code  | Present | Attendance (%)    |\n"
                        "+------------------------+--------------+---------+-------------------+"
                    )
                    table_body = "\n".join(attendance_lines)
                    table_footer = "+------------------------+--------------+---------+-------------------+"
                    attendance_summary = f"{table_header}\n{table_body}\n{table_footer}"

                    final_message = template.format(name=name, attendance=attendance_summary)

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(final_message, 'plain'))

                    try:
                        with smtplib.SMTP("smtp.gmail.com", 587) as server:
                            server.starttls()
                            server.login(sender_email, app_password)
                            server.sendmail(sender_email, email, msg.as_string())
                            sent_count += 1
                            st.success(f"✅ Sent to {name} <{email}> successfully")
                    except Exception as e:
                        st.error(f"❌ Failed to send to {email} ({name}): {e}")
                    
                    time.sleep(1)  # Prevent spam block
                else:
                    st.info(f"✅ {name} has all attendance ≥ 85% — skipped.")
                    skipped_count += 1

            st.success(f"📨 Emails sent to {sent_count} students. Skipped {skipped_count} students with sufficient attendance.")
