import streamlit as st
import pandas as pd
import gspread

st.set_page_config(page_title="Ticket Search Dashboard", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    """Load and preprocess the data dynamically from Google Sheets using Service Account."""
    try:
        # Secure Authentication Logic
        # 1. Check if we are running on Streamlit Cloud (using secrets)
        has_secrets = False
        try:
            if "gcp_service_account" in st.secrets:
                has_secrets = True
        except FileNotFoundError:
            pass # No secrets file locally, which is completely fine
            
        if has_secrets:
            gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        else:
            # 2. Fallback to local file if running locally
            gc = gspread.service_account(filename='service_account.json')
        
        # Open the Google Sheet by its ID (extracted from your link)
        sheet_id = "1zX7AQmHrZcV7G_PuWm1S29DYVbeelA-wI3rKax4hnlE"
        spreadsheet = gc.open_by_key(sheet_id)
        
        # Fetch the specific sheet named 'Dump'
        sheet = spreadsheet.worksheet("Dump")
        
        # Convert sheet records to a Pandas DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Standardize formatting for searching (handle float conversion artifacts)
        df['Ticket Id'] = df['Ticket Id'].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '', case=False).str.strip()
        df['Registration Number'] = df['Registration Number'].astype(str).str.replace('nan', '', case=False).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        st.info("💡 Hint: Open your service_account.json, find the 'client_email', and share the Google Sheet with that email address!")
        return pd.DataFrame()

def main():
    st.title("🎫 Ticket Search Dashboard")
    st.markdown("Search for ticket details using **Ticket ID** or both **Ticket ID & Registration Number**.")

    df = load_data()
    
    if df.empty:
        return

    # User Inputs
    with st.form("search_form"):
        st.subheader("Search Parameters")
        ticket_id = st.text_input("Ticket ID (Required)", placeholder="e.g., 256, 332")
        reg_number = st.text_input("Registration Number (Optional)", placeholder="e.g., DL1LAH0922")
        
        submitted = st.form_submit_button("Search Tickets")

    # Defined columns for output mapping
    # display_columns = {
    #     'Status (Ticket)': 'Ticket Status',
    #     'Customer Name': 'Customer Name',
    #     'Phone (Ticket)': 'Phone Number',
    #     'Created Time (Ticket)': 'Ticket Created Time',
    #     'Last Customer Connect Date': 'Last Customer Connect Date',
    #     'Due Date': 'Due Date'
    # }
    display_columns = {
        'Status (Ticket)': 'Ticket Status',
        'Customer Name': 'Customer Name',
        'Phone (Ticket)': 'Phone Number',
        'Created Time (Ticket)': 'Ticket Created Time',
        # 'Last Customer Connect Date': 'Last Customer Connect Date',
        'Due Date': 'Due Date',
        'Revised Due Date': 'Revised Due Date',
        'Type of Escalation': 'Type of Escalation',
        'Registration Number': 'Registration Number',
        'Store Name': 'Store Name',
        'Vehicle Delivery Date': 'Vehicle Delivery Date'
    }

    if submitted:
        search_ticket_id = ticket_id.strip()
        search_reg_number = reg_number.strip().upper()

        # Validate logic: Only Ticket ID, or Both Ticket ID and Registration Number
        if not search_ticket_id:
            st.warning("⚠️ Ticket ID is required to perform a search.")
        else:
            # Filter the dataframe
            filtered_df = df.copy()
            
            # Apply conditions
            if search_reg_number:
                # Search by BOTH
                filtered_df = filtered_df[
                    (filtered_df['Ticket Id'] == search_ticket_id) & 
                    (filtered_df['Registration Number'] == search_reg_number)
                ]
            else:
                # Search by ONLY Ticket ID
                filtered_df = filtered_df[filtered_df['Ticket Id'] == search_ticket_id]

            # Output results
            if filtered_df.empty:
                st.error("❌ No tickets found matching the provided criteria.")
            else:
                st.success(f"✅ Found {len(filtered_df)} matching record(s)!")
                
                # Filter down to the required columns
                result_df = filtered_df[list(display_columns.keys())].rename(columns=display_columns)
                
                # Display Results
                st.markdown("### Search Results")
                
                # Loop through and display each matched record clearly
                for idx, row in result_df.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        # with col1:
                        #     st.markdown(f"**🏷️ Ticket Status:** {row['Ticket Status']}")
                        #     st.markdown(f"**👤 Customer Name:** {row['Customer Name']}")
                        #     st.markdown(f"**📞 Phone Number:** {row['Phone Number']}")
                        # with col2:
                        #     st.markdown(f"**🕒 Ticket Created Time:** {row['Ticket Created Time']}")
                        #     st.markdown(f"**📅 Last Connect Date:** {row['Last Customer Connect Date']}")
                        #     st.markdown(f"**📅 Due Date:** {row['Due Date']}")
                        with col1:
                            st.markdown(f"**🏷️ Registration Number:** {row['Registration Number']}")
                            st.markdown(f"**🏷️ Ticket Status:** {row['Ticket Status']}")
                            st.markdown(f"**👤 Customer Name:** {row['Customer Name']}")
                            st.markdown(f"**📞 Phone Number:** {row['Phone Number']}")
                            st.markdown(f"**📅 Vehicle Delivery Date:** {row['Vehicle Delivery Date']}")

                        with col2:
                            st.markdown(f"**🕒 Ticket Created Time:** {row['Ticket Created Time']}")
                            st.markdown(f"**📅 Due Date:** {row['Due Date']}")
                            st.markdown(f"**📅 Revised Due Date:** {row['Revised Due Date']}")
                            st.markdown(f"**␛ Type of Escalation:** {row['Type of Escalation']}")
                            st.markdown(f"**🏬 Store Name:** {row['Store Name']}")

if __name__ == "__main__":
    main()
