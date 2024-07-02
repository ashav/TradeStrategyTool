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
    return int(max_loss_amount / avg_loss) if avg_loss != 0 else 0

def bpr_to_strategy(portfolio_value, bpr_to_strategy):
    return portfolio_value*bpr_to_strategy/100

def calculate_contracts_bpr_method(portfolio_value, deployed_bpr, strategy_bpr,bpr,dit):
    return portfolio_value*deployed_bpr*strategy_bpr/bpr if bpr != 0 else 0

def calculate_yearly_profit(expectancy, number_of_contracts, trades_per_week):
    weeks_per_year = 52
    return expectancy * number_of_contracts * weeks_per_year * trades_per_week

def generate_heatmap_data(portfolio_value, avg_profit, avg_loss, trades_per_week):
    risks = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]  # Risk percentages
    win_rates = [75,80, 85, 90, 95, 98, 100]  # Win rates
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

def generate_bpr_heatmap_data(portfolio_value, bpr, avg_days, avg_profit, avg_loss):
    bps = [5, 10, 15, 20, 25, 30, 40, 50, 60]  # BP Percentage
    win_rates = [75,80, 85, 90, 95, 98, 100]  # Win rates
    data = []
    for bp in bps:
        for win_rate in win_rates:
            dollar_to_strategy = bpr_to_strategy (portfolio_value, bp)
            contracts_per_week = round((dollar_to_strategy/bpr)*(7/avg_days),2)
            expectancy = calculate_expectancy(win_rate, avg_profit, avg_loss)
            yearly_profit = calculate_yearly_profit(expectancy, contracts_per_week, 1)
            profit_percent = yearly_profit / portfolio_value * 100
            data.append({
                "BP Allocated to Strategy (%)": bp,
                "Strategy Win Rate (%)": win_rate,
                "Yearly Profit (%)": profit_percent
            })
    df = pd.DataFrame(data)
    return df.pivot_table(index='Strategy Win Rate (%)', columns='BP Allocated to Strategy (%)', values='Yearly Profit (%)', aggfunc='first')

def main():
    st.title("Trading Strategy Analysis Tool")
    st.write("Methods to analyze campaign option trades")

    st.header ("Trade Strategy Parameters")
    with st.expander("1.Enter details for strategy. For example, the default entries are set below for a typical ES LT112 trade.", expanded=True):
        win_rate = st.slider("Win Rate (%)", min_value=0, max_value=100, value=95)
        avg_profit = st.number_input("Average Profit for Wins ($)", min_value=0, value=1200, format="%d")
        avg_loss = st.number_input("Average Loss for Losses ($)", min_value=0, value=2400, format="%d")
        bpr = st.number_input("BPR per Unit/Contract ($)", min_value=0, value=6000, format="%d")
        avg_days = st.number_input("Average Days in Trade", min_value=0, value=90, format="%d")
        expectancy = calculate_expectancy(win_rate, avg_profit, avg_loss)
        st.write("Strategy Expectancy: $", round(expectancy, 2))
        st.write("Average Profit per Day: $", round(expectancy/avg_days, 2))
        st.write("Average Monthly Return on BPR: %", round((expectancy/bpr)*(30/avg_days)*100, 2))

    st.header ("Position Sizing Based on Per-Trade Risk ")
    with st.expander("2. This method allows to set per-trade maximum portfolio risk and number of trades per week as follows:", expanded=True):
        portfolio_value = st.number_input("Portfolio Value: $", min_value=0, value=1000000, step=10000)
        max_loss_percent = st.slider("Max Loss per Trade (%)", min_value=0.01, max_value=3.0, value=1.0, step=0.01)
        number_of_contracts = calculate_contracts(portfolio_value, max_loss_percent, avg_loss)
        st.write("Maximum Number of Contracts to Trade (rounded): ", int(number_of_contracts))
        st.write("Buying Power Reduction (BPR) per Trade ($)", bpr*int(number_of_contracts))
        st.write("Max Portfolio Loss: $", number_of_contracts*avg_loss)
        trades_per_week = st.slider("Number of Trades per Week", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        yearly_profit = calculate_yearly_profit(expectancy, number_of_contracts, trades_per_week)
        st.write("Yearly Profit: $", round(yearly_profit, 2))
        profit_ratio = yearly_profit / portfolio_value * 100 if portfolio_value else 0
        st.write("Yearly Profit as % of Portfolio: ", round(profit_ratio, 2), "%")
        st.write("Fully Deployed Strategy BPR: $", round(bpr*int(number_of_contracts)*trades_per_week*avg_days/7))
        st.write("Fully Deployed BPR as % of Portfolio", round(round(bpr*int(number_of_contracts)*trades_per_week*avg_days/7)*100/portfolio_value),"%")
        st.write ("The heatmap below shows yearly profit % for this strategy and trading size")


        heatmap_df = generate_heatmap_data(portfolio_value, avg_profit, avg_loss, trades_per_week)
        fig, ax = plt.subplots()
        sns.heatmap(heatmap_df, annot=True, cmap='RdYlGn', center=0, fmt=".2f", linewidths=.5, ax=ax)
        st.pyplot(fig)
   
    st.header ("Position Sizing Based on BPR Allocation")
    with st.expander("3. This method allows to set BPR allocation to the strategy as follows:", expanded=True):
        portfolio_value = st.number_input("Portfolio Value: $", min_value=0, value=1000000, step=100000)
        deployed_bpr = st.number_input("Total Deployed Margin/Buying-Power: %", min_value=0, max_value = 100, value=50, step=1)
        strategy_bpr = st.number_input("BP from Above Deployed to this Strategy: %",min_value=0, max_value = 100, value=50, step=1)
        st.write("Total Portfolio(%) dedicated to this Strategy:" ,deployed_bpr*strategy_bpr/100,"%")
        dollar_to_strategy = bpr_to_strategy(portfolio_value,deployed_bpr*strategy_bpr/100)
        st.write("Buying Power (BP) of Fullly Deployed Strategy: $", dollar_to_strategy)
        number_of_contracts_per_month = round((dollar_to_strategy/bpr)*(30/avg_days),2)
        number_of_contracts_per_week = round((dollar_to_strategy/bpr)*(7/avg_days),2)
        st.write("Number of contracts per month:", number_of_contracts_per_month)
        st.write("Number of contracts per week:", number_of_contracts_per_week, "Risk:", round((number_of_contracts_per_week*avg_loss)*100/portfolio_value,2)   , "%")
        st.write("Number of contracts bi-weekly:", number_of_contracts_per_week*2, "Risk:", round((2*number_of_contracts_per_week*avg_loss)*100/portfolio_value,2)   , "%")
        yearly_profit = calculate_yearly_profit(expectancy, number_of_contracts_per_week, 1)
        st.write("Yearly Profit: $", round(yearly_profit, 2))
        profit_ratio = yearly_profit / portfolio_value * 100 if portfolio_value else 0
        st.write("Yearly Profit as % of Portfolio: ", round(profit_ratio, 2), "%")
        st.write ("The heatmap below shows yearly profit % for this strategy and trading size")


        bp_heatmap_df = generate_bpr_heatmap_data(portfolio_value, bpr, avg_days, avg_profit, avg_loss)
        fig, ax = plt.subplots()
        sns.heatmap(bp_heatmap_df, annot=True, cmap='RdYlGn', center=0, fmt=".2f", linewidths=.5, ax=ax)
        st.pyplot(fig)

   

if __name__ == "__main__":
    main()