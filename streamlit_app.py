import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import tempfile
from PIL import Image
from database import BillDatabase
from gemini_processor import GeminiProcessor
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Ghar Ke Bills Tracker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = BillDatabase()
if 'gemini' not in st.session_state:
    try:
        st.session_state.gemini = GeminiProcessor()
    except Exception as e:
        st.error(f"Failed to initialize Gemini processor: {e}")
        st.session_state.gemini = None

def main():
    st.title("📄 Bill Tracker")
    st.markdown("Extract items from bill photos using AI and track your expenses")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📸 Process Bills", "📊 View Expenses", "📈 Analytics"]
    )
    
    # Auto-refresh cache when switching to data viewing pages
    if page in ["📊 View Expenses", "📈 Analytics"]:
        if 'last_page' in st.session_state and st.session_state.last_page == "📸 Process Bills":
            # Coming from process bills page, refresh the cache
            if 'expenditures_cache' in st.session_state:
                del st.session_state['expenditures_cache']
        
        # Also refresh if we just saved data
        if 'data_just_saved' in st.session_state:
            if 'expenditures_cache' in st.session_state:
                del st.session_state['expenditures_cache']
            del st.session_state['data_just_saved']
    
    # Store current page for next iteration
    st.session_state.last_page = page
    
    if page == "📸 Process Bills":
        process_bills_page()
    elif page == "📊 View Expenses":
        view_expenses_page()
    elif page == "📈 Analytics":
        analytics_page()

def process_bills_page():
    st.header("📸 Process Bills")
    
    if st.session_state.gemini is None:
        st.error("Gemini processor not initialized. Please check your API key configuration.")
        return
    
    # Person selection
    person = st.selectbox(
        "Who made this purchase?",
        ["Aadishesh", "Harsha", "Mathew", "Nishant"],
        help="Select the person who made the purchase"
    )
    
    if person == "Other":
        person = st.text_input("Enter person name:")
    
    # Store person in session state for helper functions
    st.session_state.selected_person = person
    
    # Initialize uploader key if not exists
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0
    
    # Image upload with dynamic key to allow clearing (multiple files)
    uploaded_files = st.file_uploader(
        "Upload bill images",
        type=['jpg', 'jpeg', 'png'],
        help="Upload clear photos of your bills/receipts",
        key=f"bill_image_uploader_{st.session_state.uploader_key}",
        accept_multiple_files=True
    )
    
    # Only show uploaded images if files are present
    if uploaded_files:
        # Display all images in expandable sections
        for idx, uploaded_file in enumerate(uploaded_files):
            with st.expander(f"📸 {uploaded_file.name}", expanded=False):
                image = Image.open(uploaded_file)
                
                # Resize image to a reasonable size for viewing
                max_width = 600
                if image.width > max_width:
                    ratio = max_width / image.width
                    new_height = int(image.height * ratio)
                    resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    st.image(resized_image, caption=uploaded_file.name)
                else:
                    st.image(image, caption=uploaded_file.name)
        
        # Single process button for all images (below the image expanders)
        if st.button("🔍 Process All Bills", type="primary", use_container_width=True):
            process_all_images(uploaded_files)
    
    # Display extracted data if available
    if 'current_bill_data' in st.session_state and st.session_state.current_bill_data:
        display_extracted_data()

def process_all_images(uploaded_files):
    """Process all uploaded bill images and combine the results"""
    all_items = []
    processed_count = 0
    
    with st.spinner(f"Processing {len(uploaded_files)} bill(s) with AI..."):
        for idx, uploaded_file in enumerate(uploaded_files):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Process the image
                bill_data = st.session_state.gemini.process_bill_image(tmp_path)
                
                if bill_data and bill_data.get('items'):
                    # Add source info to each item
                    for item in bill_data['items']:
                        item['source_bill'] = f"Bill {idx+1} ({uploaded_file.name})"
                    
                    all_items.extend(bill_data['items'])
                    processed_count += 1
                    
                    # Show progress
                    st.success(f"✅ Processed {uploaded_file.name} - Found {len(bill_data['items'])} items")
                else:
                    st.warning(f"⚠️ No items found in {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    if all_items:
        # Create combined bill data
        combined_bill_data = {
            'items': all_items,
            'date': datetime.now().date()  # Use proper date object
        }
        
        # Store combined data in session state
        st.session_state.current_bill_data = combined_bill_data
        person = st.session_state.get('selected_person', 'Aadishesh')
        st.session_state.current_person = person
        
        st.success(f"🎉 Successfully processed {processed_count} out of {len(uploaded_files)} bills!")
        st.info(f"Found a total of {len(all_items)} items across all bills.")
        st.rerun()
    else:
        st.error("No items were found in any of the uploaded bills. Please try with clearer images.")

def process_bill_image(uploaded_file, image_index=0):
    """Process the uploaded bill image"""
    with st.spinner(f"Processing bill {image_index + 1} with AI..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Process the image
            bill_data = st.session_state.gemini.process_bill_image(tmp_path)
            
            if bill_data and bill_data.get('items'):
                # Store bill data in session state to persist it
                st.session_state.current_bill_data = bill_data
                # Get person from the current session
                person = st.session_state.get('selected_person', 'Aadishesh')
                st.session_state.current_person = person
                st.session_state.processed_image_index = image_index
                st.success(f"✅ Successfully processed bill {image_index + 1}!")
                st.rerun()  # Refresh to show the new layout
            else:
                st.error(f"No items found in bill {image_index + 1}. Please try with a clearer image.")
        
        except Exception as e:
            st.error(f"Error processing bill {image_index + 1}: {e}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

def display_extracted_data():
    """Display the extracted data with edit capability"""
    if 'current_bill_data' not in st.session_state or not st.session_state.current_bill_data:
        return
    
    bill_data = st.session_state.current_bill_data
    current_person = st.session_state.get('current_person', st.session_state.get('selected_person', 'Aadishesh'))
    processed_image_index = st.session_state.get('processed_image_index', 0)
    
    # Create DataFrame for display
    df = pd.DataFrame(bill_data['items'])
    
    st.markdown("---")  # Add a separator
    st.markdown(f"### 📋 Extracted Items from {len(df)} bill(s)")
    
    # Allow editing of the data
    edited_df = st.data_editor(
        df,
        column_config={
            "item": st.column_config.TextColumn("Item", width="medium"),
            "quantity": st.column_config.TextColumn("Quantity", width="small"),
            "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
            "category": st.column_config.SelectboxColumn(
                "Category",
                options=["Groceries", "Snacks", "Beverages", "Personal Care", "Household", "Medicine", "Other"]
            ),
            "source_bill": st.column_config.TextColumn("Source Bill", width="medium")
        },
        hide_index=True,
        use_container_width=True,
        key="extracted_items_editor"
    )
    
    # Save and clear buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Save to Database", type="primary"):
            try:
                for _, row in edited_df.iterrows():
                    st.session_state.db.add_expenditure(
                        item=row['item'],
                        quantity=row['quantity'],
                        date=bill_data['date'],
                        amount=row['amount'],
                        category=row['category'],
                        person=current_person
                    )
                
                st.success("✅ All items saved to database!")
                st.balloons()
                
                # Set flag that data was just saved
                st.session_state.data_just_saved = True
                
                # Clear the extracted data and cache
                if 'current_bill_data' in st.session_state:
                    del st.session_state['current_bill_data']
                if 'current_person' in st.session_state:
                    del st.session_state['current_person']
                if 'processed_image_index' in st.session_state:
                    del st.session_state['processed_image_index']
                if 'expenditures_cache' in st.session_state:
                    del st.session_state['expenditures_cache']
                
                # Clear the uploaded images from UI
                st.session_state.uploader_key += 1
                
                # Show success message with navigation hint
                st.info("💡 Data saved! Switch to 'View Expenses' or 'Analytics' to see your updated data.")
                
                # Force rerun to clear the display
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving to database: {e}")
    
    with col2:
        if st.button("🗑️ Clear Data"):
            # Clear the extracted data
            if 'current_bill_data' in st.session_state:
                del st.session_state['current_bill_data']
            if 'current_person' in st.session_state:
                del st.session_state['current_person']
            if 'processed_image_index' in st.session_state:
                del st.session_state['processed_image_index']
            # Also clear the uploaded images
            st.session_state.uploader_key += 1
            
            st.rerun()

def view_expenses_page():
    st.header("📊 View Expenses")
    
    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh"):
            if 'expenditures_cache' in st.session_state:
                del st.session_state['expenditures_cache']
            st.rerun()
    
    # Get all expenditures (with caching)
    if 'expenditures_cache' not in st.session_state:
        st.session_state.expenditures_cache = st.session_state.db.get_all_expenditures()
    
    expenditures = st.session_state.expenditures_cache
    
    if not expenditures:
        st.info("No expenses found. Start by processing some bills!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(expenditures)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    # Filters section (at the top)
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        date_range = st.date_input(
            "Select date range",
            value=(df['date'].min().date(), df['date'].max().date()),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date()
        )
    with col2:
        months = ['All'] + [str(month) for month in sorted(df['month'].unique())]
        selected_month = st.selectbox("Month", months)
    with col3:
        categories = ['All'] + list(df['category'].unique())
        selected_category = st.selectbox("Category", categories)
    with col4:
        persons = ['All'] + list(df['person'].unique())
        selected_person = st.selectbox("Person", persons)
    
    # Apply filters
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.Timestamp(date_range[0])) &
            (filtered_df['date'] <= pd.Timestamp(date_range[1]))
        ]
    if selected_month != 'All':
        filtered_df = filtered_df[filtered_df['month'] == pd.Period(selected_month)]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_person != 'All':
        filtered_df = filtered_df[filtered_df['person'] == selected_person]
    
    # Display summary
    total_amount = filtered_df['amount'].sum()
    total_items = len(filtered_df)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Amount", f"₹{total_amount:.2f}")
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        current_month = datetime.now().strftime('%Y-%m')
        current_month_spending = filtered_df[filtered_df['month'] == pd.Period(current_month)]['amount'].sum()
        st.metric("Current Month", f"₹{current_month_spending:.2f}")
    
    # Display editable table (index shown, id hidden)
    st.subheader("📋 Expense Details")
    if not filtered_df.empty:
        edit_df = filtered_df.copy()
        edit_df['date'] = edit_df['date'].dt.date
        # Hide the id column by not including it in the display
        columns_to_edit = ['item', 'quantity', 'date', 'amount', 'category', 'person']
        display_df = edit_df[columns_to_edit]
        # Keep the id for reference
        id_mapping = dict(zip(range(len(edit_df)), edit_df['id']))
        
        edited_data = st.data_editor(
            display_df,
            column_config={
                "item": st.column_config.TextColumn("Item", width="medium"),
                "quantity": st.column_config.TextColumn("Quantity", width="small"),
                "date": st.column_config.DateColumn("Date"),
                "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["Groceries", "Snacks", "Beverages", "Personal Care", "Household", "Medicine", "Other"]
                ),
                "person": st.column_config.SelectboxColumn(
                    "Person",
                    options=["Aadishesh", "Harsha", "Mathew", "Nishant"]
                )
            },
            hide_index=False,  # Show index
            use_container_width=True,
            key="expenses_editor"
        )
        
        # Add the id column back to edited_data for operations
        edited_data['id'] = [id_mapping[i] for i in range(len(edited_data))]
        
        # Save Changes button
        st.markdown("---")
        if st.button("💾 Save Changes", type="primary"):
            try:
                # Update each row that has been modified
                for idx, row in edited_data.iterrows():
                    st.session_state.db.update_expenditure(
                        expenditure_id=row['id'],
                        item=row['item'],
                        quantity=row['quantity'],
                        date=row['date'],
                        amount=row['amount'],
                        category=row['category'],
                        person=row['person']
                    )
                
                st.success("✅ Changes saved successfully!")
                # Clear cache to refresh data and update analytics
                if 'expenditures_cache' in st.session_state:
                    del st.session_state['expenditures_cache']
                st.rerun()
            except Exception as e:
                st.error(f"Error saving changes: {e}")
        
        # Add New Entry, Search, and Delete sections below the table
        st.markdown("---")
        # Add New Entry
        st.subheader("➕ Add New Entry")
        with st.expander("Add Manual Entry", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_item = st.text_input("Item Name")
                new_quantity = st.text_input("Quantity", value="1")
                new_amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
            with col2:
                new_date = st.date_input("Date", value=datetime.now().date())
                new_category = st.selectbox("Category", ["Groceries", "Snacks", "Beverages", "Personal Care", "Household", "Medicine", "Other"])
            with col3:
                new_person = st.selectbox("Person", ["Aadishesh", "Harsha", "Mathew", "Nishant"])
            if st.button("💾 Add Entry", type="primary"):
                if new_item and new_amount > 0:
                    try:
                        st.session_state.db.add_expenditure(
                            item=new_item,
                            quantity=new_quantity,
                            date=new_date,
                            amount=new_amount,
                            category=new_category,
                            person=new_person
                        )
                        st.success("✅ Entry added successfully!")
                        if 'expenditures_cache' in st.session_state:
                            del st.session_state['expenditures_cache']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding entry: {e}")
                else:
                    st.error("Please fill in all required fields")
        # Search
        st.subheader("🔍 Search Expenses")
        search_term = st.text_input("Search items (by name)", placeholder="Enter item name to search...")
        if search_term:
            search_df = filtered_df.copy()
            search_df['date'] = search_df['date'].dt.date
            filtered_search = search_df[search_df['item'].str.contains(search_term, case=False, na=False)]
            # Display search results without ID column
            search_display = filtered_search[['item', 'quantity', 'date', 'amount', 'category', 'person']]
            st.dataframe(search_display, use_container_width=True, hide_index=False)
        # Delete Items
        st.subheader("🗑️ Delete Items")
        st.info("💡 Select items to delete from the dropdown below:")
        selected_ids = st.multiselect(
            "Select items to delete:",
            options=edited_data['id'].tolist(),
            format_func=lambda x: f"{edited_data[edited_data['id'] == x]['item'].iloc[0]} - ₹{edited_data[edited_data['id'] == x]['amount'].iloc[0]:.2f} ({edited_data[edited_data['id'] == x]['date'].iloc[0]})",
            key="delete_multiselect",
            help="Select one or more items to delete"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚠️ Confirm Delete", type="secondary", disabled=len(selected_ids) == 0):
                if selected_ids:
                    try:
                        for item_id in selected_ids:
                            st.session_state.db.delete_expenditure(item_id)
                        st.success(f"✅ Deleted {len(selected_ids)} items successfully!")
                        if 'expenditures_cache' in st.session_state:
                            del st.session_state['expenditures_cache']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting items: {e}")
        with col2:
            st.write("")
    else:
        st.info("No expenses match your current filters.")

def analytics_page():
    st.header("📈 Analytics")
    
    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh"):
            if 'expenditures_cache' in st.session_state:
                del st.session_state['expenditures_cache']
            st.rerun()
    
    # Get all expenditures (with caching)
    if 'expenditures_cache' not in st.session_state:
        st.session_state.expenditures_cache = st.session_state.db.get_all_expenditures()
    
    expenditures = st.session_state.expenditures_cache
    
    if not expenditures:
        st.info("No expenses found. Start by processing some bills!")
        return
    
    df = pd.DataFrame(expenditures)
    df['date'] = pd.to_datetime(df['date'])
    
    # Time period selector
    time_period = st.selectbox(
        "Select time period",
        ["All time", "Last 7 days", "Last 30 days", "Last 90 days"],
        index=0  # Default to "All time"
    )
    
    # Filter by time period
    if time_period == "All time":
        cutoff_date = df['date'].min()
    elif time_period == "Last 7 days":
        cutoff_date = datetime.now() - timedelta(days=7)
    elif time_period == "Last 30 days":
        cutoff_date = datetime.now() - timedelta(days=30)
    elif time_period == "Last 90 days":
        cutoff_date = datetime.now() - timedelta(days=90)
    
    filtered_df = df[df['date'] >= cutoff_date]
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Spending by category
        st.subheader("Spending by Category")
        category_spending = filtered_df.groupby('category')['amount'].sum().reset_index()
        
        fig_pie = px.pie(
            category_spending,
            values='amount',
            names='category',
            title="Category-wise Spending"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Spending by person
        st.subheader("Spending by Person")
        person_spending = filtered_df.groupby('person')['amount'].sum().reset_index()
        
        fig_bar = px.bar(
            person_spending,
            x='person',
            y='amount',
            title="Person-wise Spending"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Spending trends section
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily spending trend
        st.subheader("Daily Spending Trend")
        if not filtered_df.empty:
            daily_spending = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum().reset_index()
            daily_spending.columns = ['date', 'amount']  # Ensure proper column names
            
            if not daily_spending.empty:
                fig_daily = px.line(
                    daily_spending,
                    x='date',
                    y='amount',
                    title="Daily Spending Trend",
                    markers=True
                )
                fig_daily.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)",
                    xaxis_tickformat="%Y-%m-%d"  # Format to show only date without time
                )
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("No daily spending data available for the selected period.")
        else:
            st.info("No data available for daily spending trend.")
    
    with col2:
        # Monthly spending trend
        st.subheader("Monthly Spending Trend")
        if not filtered_df.empty:
            # Create month column for grouping
            monthly_data = filtered_df.copy()
            monthly_data['month'] = monthly_data['date'].dt.to_period('M')
            monthly_spending = monthly_data.groupby('month')['amount'].sum().reset_index()
            monthly_spending['month'] = monthly_spending['month'].astype(str)
            
            if not monthly_spending.empty:
                fig_monthly = px.bar(
                    monthly_spending,
                    x='month',
                    y='amount',
                    title="Monthly Spending Trend"
                )
                fig_monthly.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)",
                    xaxis_tickangle=45
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.info("No monthly spending data available for the selected period.")
        else:
            st.info("No data available for monthly spending trend.")

if __name__ == "__main__":
    main()
