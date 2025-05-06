import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import io




# Sidebar for navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.selectbox("Go to", ["Dashboard", "View by Keyword"])

# Upload file
uploaded_file = st.sidebar.file_uploader("📁 Upload Alarm CSV", type=["csv"])

# Predefined keywords
keywords = [
    "Missing YCU messages",
    "Lost redundant YCU FSW",
    "Transmission locked to YCU",
    "COM5 has restarted",
    "Yard communication problem",
    "OC Reboot"
]

if uploaded_file:
    df = pd.read_csv(uploaded_file, delimiter=';')

    # Filter alarms
    alarm_df = df[df['Type'].str.lower() == 'alarm']

    # Filter by keywords
    filtered_df = alarm_df[alarm_df['Information'].str.contains('|'.join(keywords), case=False, na=False)].copy()
    filtered_df['Timestamp'] = pd.to_datetime(filtered_df['Date'] + ' ' + filtered_df['Time'], dayfirst=True)

    if page == "Dashboard":
        st.title("📊 Alarm Log Dashboard")

        if not filtered_df.empty:
            min_date = filtered_df['Date'].min()
            max_date = filtered_df['Date'].max()
            st.markdown(f"**🗓 Date Range:** {min_date} to {max_date}")

            info_counts = filtered_df['Information'].value_counts()
            status_counts = filtered_df['Status'].value_counts()
            class_counts = filtered_df['Code'].value_counts()
            alarms_per_hour = filtered_df.set_index('Timestamp').resample('H').size()

            fig, axs = plt.subplots(2, 2, figsize=(14, 10))

            info_counts.head(10).plot(kind='barh', color='skyblue', ax=axs[0, 0])
            axs[0, 0].set_title("Top 10 Alarm Types (Information)")
            axs[0, 0].set_xlabel("Count")
            axs[0, 0].invert_yaxis()

            status_counts.head(10).plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=axs[0, 1])
            axs[0, 1].set_title("Alarm Status Distribution")
            axs[0, 1].set_ylabel("")

            class_counts.plot(kind='bar', color='salmon', ax=axs[1, 0])
            axs[1, 0].set_title("Alarm Code Distribution")
            axs[1, 0].set_xlabel("Code")
            axs[1, 0].set_ylabel("Count")

            alarms_per_hour.plot(kind='line', marker='o', ax=axs[1, 1])
            axs[1, 1].set_title("Alarms Over Time (Hourly)")
            axs[1, 1].set_xlabel("Time")
            axs[1, 1].set_ylabel("Alarm Count")

            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No alarms matching the keywords were found.")

    elif page == "View by Keyword":
        st.title("📂 View Alarms by Keyword")

        keyword_choice = st.selectbox("Select a keyword to filter alarms:", keywords)

        keyword_df = filtered_df[filtered_df['Information'].str.contains(keyword_choice, case=False, na=False)]

        if not keyword_df.empty:
            display_df = keyword_df[['Date', 'Time', 'Information']].copy()

            st.markdown("### Matching Alarm Entries")
            st.table(display_df)  # ✅ This wraps long text properly
        else:
            st.info(f"No alarms found for keyword: {keyword_choice}")



else:
    st.warning("Please upload a valid alarm CSV file to get started.")
