import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Attendance Mailer", layout="centered")

st.title("📧 Attendance Mailer System")
st.write("Upload a CSV file with student attendance and send personalized emails.")

# Step 1: Upload CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Preview of Attendance Data")
    st.dataframe(df)

    # Email sender credentials
    st.subheader("✉️ Sender Gmail Details")
    sender_email = st.text_input("Your Gmail address", placeholder="example@gmail.com")
    app_password = st.text_input("App Password", type="password")

    # Subject and Message Template
    st.subheader("📨 Email Content")
    subject = st.text_input("Email Subject", "Test Mail for Cloud Computing Assignment / Your Attendance Report")
    message_template = st.text_area("Email Message Template", 
        "Hi {name},\n\nHere is your attendance summary:\n\n{attendance}\n\nRegards,\nFaculty")

    # Send Emails
    if st.button("📬 Send Emails"):
        if not sender_email or not app_password:
            st.error("Please enter your Gmail and App Password.")
        else:
            sent_count = 0
            for i, row in df.iterrows():
                name = row["Name"]
                recipient_email = row["Email"]

                # Format attendance string
                attendance_info = "\n".join([
                    f"{col}: {row[col]}" for col in df.columns if col not in ["Name", "Email"]
                ])

                # Final message
                message = message_template.format(name=name, attendance=attendance_info)

                # Compose email
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, app_password)
                        server.sendmail(sender_email, recipient_email, msg.as_string())
                        sent_count += 1
                except Exception as e:
                    st.error(f"❌ Failed to send to {recipient_email}: {e}")
                    continue

            st.success(f"✅ Emails sent to {sent_count} students successfully!")
