import yfinance as yf
import streamlit as st
import pandas as pd

def get_total_return_data(stock_symbols, start_date, end_date, initial_investment):
    total_return_data = pd.DataFrame()
    cagr_data = {}
    current_value_data = {}
    
    for symbol in stock_symbols:
        symbol = symbol.strip().upper()
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if not data.empty:
            # Ensure 'Dividends' column exists; if not, create it with all zeros
            if 'Dividends' not in data.columns:
                data['Dividends'] = 0.0

            # Adjust the closing prices for dividends
            adj_factor = (1 + data['Dividends'].cumsum() / data['Close']).fillna(1)
            data['Adj Close'] *= adj_factor
            
            # Rebase the adjusted closing prices
            data['Rebased'] = initial_investment * data['Adj Close'] / data['Adj Close'].iloc[0]
            total_return_data[symbol] = data['Rebased']
            
            # Calculate CAGR including dividends
            years = (data.index[-1] - data.index[0]).days / 365.25
            ending_value = data['Rebased'].iloc[-1]
            starting_value = initial_investment  # Initial investment amount
            cagr = ((ending_value / starting_value) ** (1 / years) - 1) * 100  # Convert to percentage
            cagr_data[symbol] = '{:.1f}%'.format(cagr)  # Format as percentage with one decimal place
            
            # Calculate current value of investment
            current_value_data[symbol] = round(ending_value, 2)

    # Create and sort the DataFrame for CAGR and current value data
    cagr_df = pd.DataFrame.from_dict(cagr_data, orient='index', columns=['CAGR (%)'])
    current_value_df = pd.DataFrame.from_dict(current_value_data, orient='index', columns=['Current Value'])
    
    # Combine all the dataframes
    result_df = pd.concat([cagr_df, current_value_df], axis=1)
    result_df = result_df.sort_values(by='CAGR (%)', ascending=False)  # Sort by CAGR in high to low
    
    return total_return_data, result_df

# Streamlit user interface setup
st.title('Total Stock Return Viewer')

# Add text explaining Australian ticker format
st.write("For Australian shares, enter the ticker with '.AX' (e.g. CBA.AX)")

# Input for stock symbols
stock_symbols = st.text_input('Enter Stock Symbols (comma separated):', 'VHY.AX, VESG.AX, VDHG.AX').split(',')

# Input for the date range
start_date = st.date_input('Start Date', value=pd.to_datetime('2019-01-01'))
end_date = st.date_input('End Date', value=pd.to_datetime('2023-12-31'))

# Input for the initial investment
initial_investment = st.number_input('Initial Investment:', value=10000)

# Button to show the results
if st.button('Show Total Stock Return'):
    total_return_data, result_df = get_total_return_data(stock_symbols, start_date, end_date, initial_investment)
    if not total_return_data.empty:
        st.write('### Total Stock Return (Rebased to Initial Investment)')
        st.line_chart(total_return_data)

        st.write('### Annualised Return and Current Value')
        st.write('##### Ordered by Annualised Return (including dividend reinvestment)')
        st.dataframe(result_df)
    else:
        st.write('No data available for the given symbols or date range.')
