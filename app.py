import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Attendance Mailer", layout="centered")

st.title("📧 Attendance Mailer System (Grouped by Student)")
st.write("Upload a CSV file with multiple course rows per student and send summary emails.")

# Upload file
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(df)

    # Email input
    st.subheader("✉️ Email Credentials")
    sender_email = st.text_input("Sender Gmail", placeholder="example@gmail.com")
    app_password = st.text_input("App Password", type="password")

    subject = st.text_input("Email Subject", "Test Mail for Cloud Computing Assignment / Your Attendance Report")
    template = st.text_area("Message Template", 
        "Hi {name},\n\nHere is your attendance summary:\n\n{attendance}\n\nRegards,\nFaculty")

    if st.button("📬 Send Emails"):
        if not sender_email or not app_password:
            st.error("Please enter Gmail and App Password.")
        else:
            # Group by student (assuming each student has unique Name)
            grouped = df.groupby("Name")

            sent_count = 0

            for name, group in grouped:
                attendance_lines = []
                student_email = None

                for _, row in group.iterrows():
                    course = row["Course Name"]
                    code = row["Course Code"]
                    present = row["Present"]
                    total = row["Total Sessions"]
                    avg = row["Average"]

                    # You can also use: student_email = row["Email"] if you have email column
                    student_email = st.text_input(f"Enter email for {name}", key=name)

                    attendance_lines.append(f"{course} ({code}): {present}/{total} - {avg}")

                if not student_email:
                    st.warning(f"No email entered for {name}, skipping.")
                    continue

                attendance_summary = "\n".join(attendance_lines)
                final_message = template.format(name=name, attendance=attendance_summary)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = student_email
                msg['Subject'] = subject
                msg.attach(MIMEText(final_message, 'plain'))

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, app_password)
                        server.sendmail(sender_email, student_email, msg.as_string())
                        sent_count += 1
                except Exception as e:
                    st.error(f"❌ Failed to send to {student_email}: {e}")
                    continue

            st.success(f"✅ Emails sent to {sent_count} students successfully!")
