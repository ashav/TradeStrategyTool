import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def calculate_expectancy(win_rate, avg_profit, avg_loss):
    loss_rate = 100 - win_rate
    expectancy = (win_rate * avg_profit - loss_rate * avg_loss) / 100
    return expectancy

def calculate_contracts(portfolio_value, max_loss_percent, avg_loss):
    max_loss_amount = portfolio_value * max_loss_percent / 100
    return max_loss_amount / avg_loss if avg_loss != 0 else 0

def calculate_yearly_profit(expectancy, number_of_contracts, trades_per_week):
    weeks_per_year = 52
    return expectancy * number_of_contracts * weeks_per_year * trades_per_week

def generate_heatmap_data(portfolio_value, avg_profit, avg_loss, trades_per_week):
    risks = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5]  # Risk percentages
    win_rates = [80, 85, 90, 95, 98, 100]  # Win rates
    data = []
    for risk in risks:
        for win_rate in win_rates:
            expectancy = calculate_expectancy(win_rate, avg_profit, avg_loss)
            contracts = calculate_contracts(portfolio_value, risk, avg_loss)
            yearly_profit = calculate_yearly_profit(expectancy, contracts, trades_per_week)
            profit_percent = yearly_profit / portfolio_value * 100
            data.append({
                "Risk Per Trade (%)": risk,
                "Strategy Win Rate (%)": win_rate,
                "Yearly Profit (%)": profit_percent
            })
    df = pd.DataFrame(data)
    return df.pivot_table(index='Strategy Win Rate (%)', columns='Risk Per Trade (%)', values='Yearly Profit (%)', aggfunc='first')

def main():
    st.title("Trading Strategy Analysis Tool")

    with st.expander("1. Strategy Expectancy Calculator"):
        win_rate = st.slider("Win Rate (%)", min_value=0, max_value=100, value=98)
        avg_profit = st.number_input("Average Profit for Wins ($)", min_value=0, value=104, format="%d")
        avg_loss = st.number_input("Average Loss for Losses ($)", min_value=0, value=402, format="%d")
        expectancy = calculate_expectancy(win_rate, avg_profit, avg_loss)
        st.write("Expectancy of the Strategy: $", round(expectancy, 2))

    with st.expander("2. Risk Management"):
        portfolio_value = st.number_input("Portfolio Value ($)", min_value=0, value=1000000, step=100000)
        max_loss_percent = st.slider("Max Loss per Trade (%)", min_value=0.01, max_value=3.0, value=1.0, step=0.01)
        number_of_contracts = calculate_contracts(portfolio_value, max_loss_percent, avg_loss)
        st.write("Maximum Number of Contracts to Trade: ", int(number_of_contracts))

    with st.expander("3. Trade Frequency and Yearly Profits"):
        trades_per_week = st.slider("Number of Trades per Week", min_value=1, max_value=5, value=3)
        yearly_profit = calculate_yearly_profit(expectancy, number_of_contracts, trades_per_week)
        st.write("Yearly Profit: $", round(yearly_profit, 2))
        profit_ratio = yearly_profit / portfolio_value * 100 if portfolio_value else 0
        st.write("Yearly Profit as % of Portfolio: ", round(profit_ratio, 2), "%")

    with st.expander("4. Risk vs. Win Rate Heatmap (Yearly Profit %)"):
        heatmap_df = generate_heatmap_data(portfolio_value, avg_profit, avg_loss, trades_per_week)
        fig, ax = plt.subplots()
        sns.heatmap(heatmap_df, annot=True, cmap='RdYlGn', center=0, fmt=".2f", linewidths=.5, ax=ax)
        st.pyplot(fig)

if __name__ == "__main__":
    main()