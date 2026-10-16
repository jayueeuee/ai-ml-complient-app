import streamlit as st
import database
import pandas as pd
from PIL import Image
from email_service import send_resolution_email
import utils

st.set_page_config(page_title="Nagar Sevak Dashboard", page_icon="👨‍💼", layout="wide")
utils.render_sidebar()

try:
    database.setup_database()
except Exception:
    pass

st.title("👨‍💼 Nagar Sevak Dashboard")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in from the Home Page to access this portal.")
    st.stop()

if st.session_state.user_info.get("role") != "Sevak":
    st.warning("This page is restricted to Nagar Sevaks.")
    st.stop()

sevak_info = st.session_state.user_info
selected_ward = sevak_info.get('ward_name', 'Unknown')

col_title, col_logout = st.columns([4, 1])
with col_title:
    st.subheader(f"Welcome, {sevak_info.get('nagar_sevak_name', 'Sevak')} ({selected_ward})")
with col_logout:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()

# Load complaints for this ward
complaints_df = database.get_complaints_df()
ward_complaints = complaints_df[complaints_df['ward'] == selected_ward].copy()

if ward_complaints.empty:
    st.info("No complaints assigned to this ward yet.")
else:
    # Quick Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(ward_complaints))
    c2.metric("Pending", len(ward_complaints[ward_complaints['status'] == 'Pending']))
    c3.metric("Resolved", len(ward_complaints[ward_complaints['status'] == 'Resolved']))
    c4.metric("High Priority", len(ward_complaints[ward_complaints['priority'] == 'High']))

    st.markdown("---")
    
    col_cat, col_pri = st.columns(2)
    with col_cat:
        st.write("**Complaints by Category**")
        cat_counts = ward_complaints['category'].value_counts()
        st.bar_chart(cat_counts)
    with col_pri:
        st.write("**Complaints by Priority**")
        pri_counts = ward_complaints['priority'].value_counts()
        st.bar_chart(pri_counts)
        
    st.markdown("---")
    
    # Sort so High Priority is first, then by submission date
    priority_map = {'High': 1, 'Medium': 2, 'Low': 3}
    ward_complaints['priority_rank'] = ward_complaints['priority'].map(priority_map).fillna(4)
    ward_complaints = ward_complaints.sort_values(by=['priority_rank', 'status', 'submission_date'], ascending=[True, True, False])
    
    # Show Top High Priority Complaint Notification
    high_priority_complaints = ward_complaints[(ward_complaints['priority'] == 'High') & (ward_complaints['status'] != 'Resolved')]
    if not high_priority_complaints.empty:
        st.warning("🚨 Attention: You have high priority complaints pending!")
        first_high = high_priority_complaints.iloc[0]
        st.write(f"**Top High Priority Complaint ID:** {first_high['id']}")
        st.write(f"**Category:** {first_high['category']} | **Status:** {first_high['status']}")
        st.write(f"**Description:** {first_high['description']}")
        st.markdown("---")

    st.subheader("Assigned Complaints Overview")
    
    display_cols = ['id', 'category', 'priority', 'status', 'submission_date']
    if 'user_name' in ward_complaints.columns:
        display_cols.append('user_name')
        
    st.dataframe(ward_complaints[display_cols].reset_index(drop=True), use_container_width=True)

    st.markdown("---")
    st.subheader("View / Update Complaint")
    
    # Search
    search_id = st.text_input("Search Complaint by ID (leave empty to select from list below)")
    
    if search_id:
        choices = [c for c in ward_complaints['id'].tolist() if search_id.upper() in c.upper()]
    else:
        choices = ward_complaints['id'].tolist()
        
    # Selection
    comp_id = st.selectbox("Select Complaint ID", choices)
    
    if comp_id:
        comp_data = ward_complaints[ward_complaints['id'] == comp_id].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Description:** {comp_data['description']}")
            user_n = comp_data.get('user_name', 'Unknown')
            user_c = comp_data.get('user_contact', 'Unknown')
            st.write(f"**Reported By:** {user_n if pd.notna(user_n) else 'Unknown'} | **Contact:** {user_c if pd.notna(user_c) else 'Unknown'}")
            st.write(f"**Category:** {comp_data['category']} | **Priority:** {comp_data['priority']}")
            st.write(f"**AI Verification:** {comp_data['verification_status']}")
            st.write(f"**Submitted On:** {comp_data['submission_date']}")
            st.write(f"**Current Status:** {comp_data['status']}")
            
        with col2:
            try:
                img = Image.open(comp_data['image_path'])
                st.image(img, caption="User Uploaded Proof", use_container_width=True)
            except:
                st.warning("Image not found.")
                
        st.markdown("### Update Status")
        new_status = st.radio("Change Status To:", ['Pending', 'Work in Progress', 'Resolved', 'Black Zone'], 
                              index=['Pending', 'Work in Progress', 'Resolved', 'Black Zone'].index(comp_data['status']) if comp_data['status'] in ['Pending', 'Work in Progress', 'Resolved', 'Black Zone'] else 0)
        comments = st.text_area("Resolution Comments", value=comp_data['sevak_comments'] if pd.notna(comp_data['sevak_comments']) else "")
        proof_file = st.file_uploader("Upload Resolution Proof (Optional)", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Update Complaint"):
            proof_path = comp_data['resolution_proof']
            if proof_file:
                proof_path = f"uploads/{comp_id}_resolution.jpg"
                img = Image.open(proof_file)
                img.save(proof_path)
                
            database.update_complaint_status(comp_id, new_status, comments, proof_path)
            st.success("Complaint updated successfully!")
            
            # Send resolution email to user when status is set to Resolved
            if new_status == "Resolved":
                user_n = comp_data.get('user_name', 'User')
                user_c = comp_data.get('user_contact', '')
                cat = comp_data.get('category', 'N/A')
                
                if pd.notna(user_n) and pd.notna(user_c) and user_c:
                    try:
                        send_resolution_email(
                            user_contact=user_c,
                            user_name=user_n,
                            complaint_id=comp_id,
                            category=cat,
                            sevak_comments=comments
                        )
                        st.toast("📧 Resolution email sent to user!", icon="✅")
                    except Exception as e:
                        st.warning(f"Could not send email: {e}")
                else:
                    st.info("User contact not available — email not sent.")
            
            st.rerun()

