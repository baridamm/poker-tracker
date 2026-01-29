import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File to store poker hands
DATA_FILE = "poker_hands.csv"

# Initialize the CSV file if it doesn't exist
def init_data_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'timestamp', 'position', 'hole_cards', 'action', 
            'result', 'profit_loss', 'notes'
        ])
        df.to_csv(DATA_FILE, index=False)

# Load existing hands
def load_hands():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

# Save a new hand
def save_hand(hand_data):
    df = load_hands()
    new_hand = pd.DataFrame([hand_data])
    df = pd.concat([df, new_hand], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Main app
def main():
    st.set_page_config(page_title="Poker Hand Tracker", page_icon="🃏", layout="wide")
    
    st.title("🃏 Poker Hand Tracker")
    
    # Initialize data file
    init_data_file()
    
    # Sidebar for navigation
    page = st.sidebar.radio("Navigate", ["Log Hand", "Hand History", "Stats"])
    
    if page == "Log Hand":
        log_hand_page()
    elif page == "Hand History":
        hand_history_page()
    elif page == "Stats":
        stats_page()

def log_hand_page():
    st.header("Log a New Hand")
    
    with st.form("hand_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            position = st.selectbox(
                "Position",
                ["UTG", "UTG+1", "MP", "CO", "BTN", "SB", "BB"]
            )
            
            hole_cards = st.text_input(
                "Hole Cards",
                placeholder="e.g., AhKd",
                help="Enter your two cards (e.g., AhKd for Ace of hearts, King of diamonds)"
            )
            
            action = st.selectbox(
                "Your Action",
                ["Fold", "Call", "Raise", "All-in"]
            )
        
        with col2:
            result = st.selectbox(
                "Result",
                ["Won", "Lost", "Chopped"]
            )
            
            profit_loss = st.number_input(
                "Profit/Loss ($)",
                value=0.0,
                step=0.5,
                help="Enter positive for wins, negative for losses"
            )
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Any observations about the hand..."
            )
        
        submitted = st.form_submit_button("Log Hand")
        
        if submitted:
            if not hole_cards:
                st.error("Please enter your hole cards!")
            else:
                hand_data = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'position': position,
                    'hole_cards': hole_cards,
                    'action': action,
                    'result': result,
                    'profit_loss': profit_loss,
                    'notes': notes
                }
                save_hand(hand_data)
                st.success("✅ Hand logged successfully!")
                st.balloons()

def hand_history_page():
    st.header("Hand History")
    
    df = load_hands()
    
    if df.empty:
        st.info("No hands logged yet. Go to 'Log Hand' to get started!")
    else:
        # Show total hands
        st.metric("Total Hands Logged", len(df))
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_position = st.multiselect(
                "Filter by Position",
                options=df['position'].unique(),
                default=df['position'].unique()
            )
        with col2:
            filter_result = st.multiselect(
                "Filter by Result",
                options=df['result'].unique(),
                default=df['result'].unique()
            )
        
        # Apply filters
        filtered_df = df[
            (df['position'].isin(filter_position)) & 
            (df['result'].isin(filter_result))
        ]
        
        # Display the table
        st.dataframe(
            filtered_df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"poker_hands_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def stats_page():
    st.header("Statistics")
    
    df = load_hands()
    
    if df.empty:
        st.info("No hands logged yet. Log some hands to see your stats!")
    else:
        # Overall stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_hands = len(df)
        total_profit = df['profit_loss'].sum()
        won_hands = len(df[df['result'] == 'Won'])
        win_rate = (won_hands / total_hands * 100) if total_hands > 0 else 0
        
        with col1:
            st.metric("Total Hands", total_hands)
        with col2:
            st.metric("Total P/L", f"${total_profit:.2f}")
        with col3:
            st.metric("Hands Won", won_hands)
        with col4:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        st.divider()
        
        # Position analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Profit by Position")
            position_stats = df.groupby('position')['profit_loss'].sum().sort_values(ascending=False)
            st.bar_chart(position_stats)
        
        with col2:
            st.subheader("Hands by Position")
            position_counts = df['position'].value_counts()
            st.bar_chart(position_counts)
        
        st.divider()
        
        # Recent performance
        st.subheader("Recent 10 Hands Performance")
        recent = df.tail(10)[['timestamp', 'position', 'hole_cards', 'result', 'profit_loss']]
        st.dataframe(recent.sort_values('timestamp', ascending=False), hide_index=True)

if __name__ == "__main__":
    main()
