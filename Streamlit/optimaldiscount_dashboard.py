import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and clean data
@st.cache_data
def load_and_prepare_data(file_path):
    data = pd.read_csv(file_path)
    
    # Data Selection and Cleaning
    data = data[['discount', 'profit', 'sales', 'profit_margin']]
    data['discount'] = pd.to_numeric(data['discount'], errors='coerce')
    data['profit_margin'] = pd.to_numeric(data['profit_margin'], errors='coerce') * 100
    data.dropna(subset=['discount', 'profit', 'sales'], inplace=True)
    
    # Categorize discounts into ranges
    bins = [0, 0.1, 0.2, 0.3, 0.4, 1.0]
    labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40%+']
    data['discount_range'] = pd.cut(data['discount'], bins=bins, labels=labels).astype(str)
    
    return data

# Perform discount analysis
@st.cache_data
def perform_discount_analysis(data):
    # Group by discount ranges and calculate metrics
    discount_analysis = data.groupby('discount_range').agg({
        'sales': 'sum',
        'profit': 'sum',
        'profit_margin': 'mean'
    })
    
    # Add a profit-to-sales ratio column
    discount_analysis['profit_to_sales_ratio'] = (discount_analysis['profit'] / discount_analysis['sales']) * 100
    
    return discount_analysis

# Main Streamlit app
def main():
    st.title("Optimal Discount Strategy Dashboard")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload your CSV data file", type=["csv"])
    if uploaded_file:
        # Load and Prepare Data
        data = load_and_prepare_data(uploaded_file)
        
        # Perform Analysis
        discount_analysis = perform_discount_analysis(data)
        
        # Dashboard Options
        st.sidebar.header("Dashboard Options")
        selected_option = st.sidebar.selectbox("Choose a view:", 
                                               ["Overview", "Discount Analysis", "Recommendations"])
        
        # Overview Section
        if selected_option == "Overview":
            st.header("Dataset Overview")
            st.write("### First Few Rows")
            st.write(data.head())
            st.write("### Dataset Statistics")
            st.write(data.describe())
        
        # Discount Analysis Section
        elif selected_option == "Discount Analysis":
            st.header("Discount Analysis")
            st.write("### Discount Metrics")
            st.write(discount_analysis)
            
            # Plot Profit Margin vs. Discount Range
            fig, ax = plt.subplots(figsize=(10, 6))
            discount_analysis['profit_margin'].plot(kind='bar', color='orange', alpha=0.7, ax=ax)
            ax.set_title("Profit Margin vs. Discount Range")
            ax.set_xlabel("Discount Range")
            ax.set_ylabel("Profit Margin (%)")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            st.pyplot(fig)
            
            # Plot Profit-to-Sales Ratio vs. Discount Range
            fig, ax = plt.subplots(figsize=(10, 6))
            discount_analysis['profit_to_sales_ratio'].plot(kind='bar', color='skyblue', alpha=0.7, ax=ax)
            ax.set_title("Profit-to-Sales Ratio vs. Discount Range")
            ax.set_xlabel("Discount Range")
            ax.set_ylabel("Profit-to-Sales Ratio (%)")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            st.pyplot(fig)
        
        # Recommendations Section
        elif selected_option == "Recommendations":
            st.header("Recommendations")
            optimal_range = discount_analysis['profit_margin'].idxmax()
            st.write(f"### Recommended Discount Range: {optimal_range}")
            st.write("""
                Based on the analysis:
                - Discounts in this range provide the highest average profit margin.
                - Maintain sales volume by avoiding excessive discounts (>30%).
                - Implement tiered discount strategies for specific categories if required.
            """)
        
        # Save Results
        if st.button("Save Analysis"):
            discount_analysis.to_csv("discount_analysis.csv")
            st.success("Analysis saved as 'discount_analysis.csv'")
    else:
        st.warning("Please upload a CSV file to proceed.")

if __name__ == "__main__":
    main()
