import math
from matplotlib import pyplot as plt
import numpy as np

# ******************** PARAMETERS FOR THE MODEL ********************************** #

# ******************** KNOWN PARAMETERS ********************************** #
# I call these "known" because you know these before you buy the home in question. There's little doubt here,
# and you should feel confident setting these knobs when considering a purchase. Most of the "exploration"
# will come from the assumed parameters in the section below.

# How much is the house you're looking to buy, in dollars?
PURCHASE_PRICE = 765700

# What percent of the purchase price are you willing to put down?
# If you are receiving a gift for your down payment, put only the percentage you are solely contributing here.
# There's a different parameter, GIFT, to represent how much money you'll receive as a gift towards your down payment.
DOWN_PAYMENT_PERCENTAGE = 20

# What interest rate did you qualify for? A percentage value, i.e. "6.6" is "a 6.6% interest rate".
INTEREST_RATE = 6.6

# What is the term of the mortgage? Usually 15 or 30. This calculator does not model adjustable-rate mortgages.
YEARS_OF_MORTGAGE = 30

# What is the initial home insurance estimate, in dollars per year?
# NOTE: This will be modeled as growing once every 12 months, per the assumed general inflation rate.
HOME_INSURANCE = 1000

# What is the property tax rate for your prospective home, as a percentage of the home's value?
# NOTE: This will model as growing only once every 12 months. The percentage remains the same, but as the home's value grows,
# naturally the payment will grow as well. In most places, tax-assessed value correlates strongly with home value, but
# this could be very different if you live in California.
PROPERTY_TAX_RATE = 1

# In dollars, how much do you currently pay in rent, or how much would you pay in rent if you don't live in this prospective home?
RENT = 2700

# This is the Private Mortgage Insurance rate you qualify for, as a percentage of the debt.
# This is only applied if your down payment is below 20%. It will add an insurance cost to your monthly payment
# so long as the loan-to-value ratio exceeds 80%, and will automatically terminate when the ratio drops below 80%,
# whether that results from paying down your principal or home apprecation or a combination of the two.
# Based on federal law, it will also end halfway through the mortgage term automatically, even if none of the
# above conditions are satisfied. 
PMI_RATE = 1.5

# Add Homeowner's Assocation fees if the home you are looking at has them. 
# It's assumed to increase once per year at the rate of assumed general inflation.
# This is the current monthly HOA fee, in dollars.
HOA_FEES = 0

# If you are receiving a gift to contribute to your down payment, add how much
# you are receiving here, in dollars.
GIFT = 0

# California? If true, tax-assessed value will increase at the maximum California value
# of 2% per year or the ASSUMED_ANNUAL_APPRECIATION, whichever is lower.
# If not in California, tax-assessed value will match whatever the home value is throughout
# the period.
IN_CALIFORNIA = True
# ******************** END KNOWN PARAMETERS ********************************** #

# ******************** ASSUMED PARAMETERS ********************************** #
# These are all educated guesses and start at some reasonable assumptions. This is where things get wonky, 
# and playing with these numbers lets you better understand just how much is out of your hands.
# You can also play around with additional simulations (parameters below) to give a few of these some variance.
# I've attempted to order these in what I expect, under most circumstances, to be the most impacful.

# How much will we assume the home's value appreciates over time, as a percentage of the home's value per year?
# e.g. a value of "3" here assumes the home accrues 3% of its value per year.
ASSUMED_ANNUAL_APPRECATION = 3

# How much do you expect the after-tax annual return on your investments to be?
AFTER_TAX_ANNUAL_RETURN_ON_INVESTMENTS = 5

# How much do we assume inflation is generally, as a percentage per year? e.g. 3 is "3% inflation per year".
ASSUMED_INFLATION = 3

# If you rent, how much do you expect your rent to increase, as a percent of your rent per year?
# A value of 3 means you expect your rent to increase 3% per year.
# If you don't have rent control or any data on your rental zip code, you can just use the same value as ASSUMED_INFLATION.
RENTAL_ANNUAL_INFLATION = 2

# What is your marginal income tax rate, as a percentage of income?
MARGINAL_INCOME_TAX = 24

# How much do you expect to spend on maintenance/renovations for the home, as a percentage of the home's value per year?
ANNUAL_MAINTENANCE = 2

# How much do you expect it to cost to sell the house, as a percent of its value?
# A basic assumption is "6" for 6 percent: 3% for each agent of the real estate transaction. 
TRANSACTION_COST = 6

# ******************** END ASSUMED PARAMETERS ********************************** #

# ******************** MODEL PARAMETERS FOR VARIED SIMULATIONS ******************* # 
# These two parameters allow you to run multiple simulations at once.
# Each simulation adds a bit of variance to four of the assumed parameters, listed in order:
# home appreciation, anual investment return, inflation, and rental inflation.
#
# What this does is takes the values you set above as the default value and continues
# to graph them as a solid line. Then it runs additional simulations (the number of which
# can be set below) but adds a bit of variance to each of those four values
# every time it starts over and runs a new simulation. 
# 
# The way variance is added is by assuming each of the parameters follows a random normal
# distribution whose mean is the value you set. The VARIANCE value refers one standard deviation
# around the mean you provided. So we take a normal sample for each value before running a new simulation.
# The results of those simulations are drawn as dotted lines on the resulting graphs.
#
# This is useful for showing you how much a little variance in only four of these parameters
# that are completely out of your control can have enormous impact on the financial outcome.

# How many simulations do you want, in addition to the default one using your provided values?
# Set this to 0 if you don't want any additional simulations.
NUM_ADDITIONAL_SIMULATIONS = 10

# Set the variance (1 standard deviation) for each of the four assumed parameters.
VARIANCES = [
    0.5,    # ASSUMED_ANNUAL_APPRECATION
    0.5,    # AFTER_TAX_ANNUAL_RETURN_ON_INVESTMENTS
    0.5,    # ASSUMED_INFLATION
    0.5,    # RENTAL_ANNUAL_INFLATION
]

# ******************** END MODEL PARAMETERS FOR MULTI-SIMULATION ******************* # 


# ******************** DO NOT CHANGE ANYTHING BELOW THIS LINE ********************************** #

num_periodic_payments = YEARS_OF_MORTGAGE * 12
periodic_interest_rate = INTEREST_RATE / 100 / 12
discount_factor_helper = math.pow((1+periodic_interest_rate), num_periodic_payments)
discount_factor = (discount_factor_helper - 1) / (periodic_interest_rate * discount_factor_helper)
down_payment = PURCHASE_PRICE * DOWN_PAYMENT_PERCENTAGE / 100 + GIFT
mortgage_payment = round((PURCHASE_PRICE - down_payment) / discount_factor, 2)

print("Your down payment will be ${}".format(down_payment))
if GIFT != 0: print("Since you had a gift, your portion of the down payment will only be ${}".format(down_payment - GIFT))
print("Your monthly mortgage payment, excluding insurance and taxes, will be ${}".format(mortgage_payment))

# ******************** CODE THAT BUILDS AND RUNS THE MODEL ********************************** #
breakeven_periods = []
net_cashes = []
equities_while_renting = []
present_value_benefits = []

def simulate(assumed_annual_apprecation, after_tax_investment_return, inflation, rental_inflation):
    appreciation_per_period = 1+assumed_annual_apprecation/100 / 12
    home_values = [PURCHASE_PRICE]
    debt = [PURCHASE_PRICE - down_payment]
    tax_assessed_value = [PURCHASE_PRICE]
    equity_in_home = [down_payment]
    
    fixed_costs = {}
    fixed_costs['insurance'] = [HOME_INSURANCE/12]
    fixed_costs['property_tax'] = [PROPERTY_TAX_RATE/100/12*tax_assessed_value[-1]]
    fixed_costs['maintenance'] = []
    
    income_tax_savings = []
    
    interest_on_debt = []
    paid_principal = []
    transaction_cost = [TRANSACTION_COST/100*PURCHASE_PRICE]
    net_cash = []
    rent = [RENT]
    cash_outflow = []
    equity_while_renting = [down_payment - GIFT]
    breakeven = False
    breakeven_period = None
    pmi = [0]
    pmi_ended = (debt[-1] / home_values[-1]) <= 0.8
    hoa = [HOA_FEES]
    present_value_benefit = []
    home_investment_surplus = [0]
    
    for month in range(0, num_periodic_payments):
        home_values.append(home_values[-1]*appreciation_per_period)
        interest_on_debt.append(round(periodic_interest_rate*debt[-1], 2))
        paid_principal.append(mortgage_payment-interest_on_debt[-1])
        debt.append(debt[-1]-paid_principal[-1])
        fixed_costs['maintenance'].append(ANNUAL_MAINTENANCE/12/100 * home_values[-1])
        income_tax_savings.append(interest_on_debt[-1]*MARGINAL_INCOME_TAX/100)
        equity_in_home.append(home_values[-1] - debt[-1])
    
        if (month % 12) == 0 and month != 0:
            fixed_costs['insurance'].append(fixed_costs['insurance'][-1] * (1+inflation/100))
            tax_assessed_value.append(home_values[-1] if not IN_CALIFORNIA else (tax_assessed_value[-1]*(1+max(2,ASSUMED_ANNUAL_APPRECATION)/100)))
            fixed_costs['property_tax'].append(PROPERTY_TAX_RATE/100/12*tax_assessed_value[-1])
            rent.append(rent[-1]*(1+rental_inflation/100))
            hoa.append(hoa[-1]*(1+inflation/100))
        elif month != 0:
            fixed_costs['insurance'].append(fixed_costs['insurance'][-1])
            fixed_costs['property_tax'].append(fixed_costs['property_tax'][-1])
            transaction_cost.append(TRANSACTION_COST/100 * home_values[-1])
            rent.append(rent[-1])
            hoa.append(hoa[-1])
    
        if not pmi_ended:
            loan_to_value = debt[-1] / home_values[-1]
            if loan_to_value <= 0.8 or month > (YEARS_OF_MORTGAGE * 12/2):
                pmi_ended = True
                pmi.append(0)
            else:
                pmi.append(PMI_RATE/100/12 * debt[-1])
    
        cash_outflow_in_month = interest_on_debt[-1] + fixed_costs['maintenance'][-1] + fixed_costs['insurance'][-1] + fixed_costs['property_tax'][-1] + pmi[-1] + hoa[-1] - income_tax_savings[-1]
        cash_outflow.append(cash_outflow_in_month)
        cash_outflow_vs_rent = cash_outflow_in_month - rent[-1]
        home_investment_surplus.append(home_investment_surplus[-1]*(1+after_tax_investment_return/12/100)-min(0, cash_outflow_vs_rent))
        net_cash.append(home_values[-1] - transaction_cost[-1] - debt[-1] + home_investment_surplus[-1])
        equity_while_renting.append((equity_while_renting[-1])*(1+after_tax_investment_return/12/100)+max(0, cash_outflow_vs_rent))
        present_value_benefit.append((net_cash[-1] - equity_while_renting[-1])/math.pow(1+inflation/100/12, month))
    
        if not breakeven and net_cash[-1] > equity_while_renting[-1]:
            breakeven = True
            breakeven_period = month 

    breakeven_periods.append(breakeven_period)
    net_cashes.append(net_cash)
    equities_while_renting.append(equity_while_renting)
    present_value_benefits.append(present_value_benefit)



simulate(ASSUMED_ANNUAL_APPRECATION, AFTER_TAX_ANNUAL_RETURN_ON_INVESTMENTS, ASSUMED_INFLATION, RENTAL_ANNUAL_INFLATION)

for _ in range(0, NUM_ADDITIONAL_SIMULATIONS):
    simulate(np.random.normal(ASSUMED_ANNUAL_APPRECATION, VARIANCES[0]),
             np.random.normal(AFTER_TAX_ANNUAL_RETURN_ON_INVESTMENTS, VARIANCES[1]),
             np.random.normal(ASSUMED_INFLATION, VARIANCES[2]),
             np.random.normal(RENTAL_ANNUAL_INFLATION, VARIANCES[3]))

if NUM_ADDITIONAL_SIMULATIONS == 0:
    if breakeven_periods[0]:
        print("It will take {} years to break even.".format(round(breakeven_periods[0]/12, 2)))
    else:
        print("It will always be better to rent.")
else:
    breakeven_times = len(breakeven_periods) - breakeven_periods.count(None)
    filtered = [x for x in breakeven_periods if x is not None]
    average_breakeven, min_breakeven, max_breakeven = None, None, None
    if len(filtered) > 0:
        average_breakeven = round(np.average(filtered)/12, 2)
        min_breakeven = round(np.min(filtered)/12, 2)
        max_breakeven = round(np.max(filtered)/12, 2)
    if breakeven_periods.count(None) == 0:
        print("After {} attempts, you always break even. It takes on average {} years.".format(breakeven_times, average_breakeven))
        print("Breaking even could take as little as {} years or as long as {} years.".format(min_breakeven, max_breakeven))
    elif breakeven_times == 0:
        print("After {} attempts, you never break even. It'll always be better to rent.".format(len(breakeven_periods)))
    else:
        print("You break even in {} out of {} simulations. When you break even it takes on average {} years.".format(
            breakeven_times, len(breakeven_periods), average_breakeven))
        print("Breaking even could take as little as {} years or as long as {} years.".format(min_breakeven, max_breakeven))

print("The average ending present value benefit of owning over renting is ${}".format(round(np.average([x[-1] for x in present_value_benefits]), 2)))

years = np.arange(0, YEARS_OF_MORTGAGE, 1/12)

_, ax1 = plt.subplots()
ax1.set(xlabel="Year", ylabel="Value")
plt.plot(years, net_cashes[0], label="home proceeds if sold")
plt.plot(years, equities_while_renting[0][1:], label="investments while renting")
plt.legend()
plt.title("Owning vs Renting Values Over Time")
for i in range(1, len(net_cashes)):
    plt.plot(years, net_cashes[i], ':', alpha=0.2, color='blue')
    plt.plot(years, equities_while_renting[i][1:], ':', alpha=0.5, color='orange')
plt.savefig('output/graph_1.png')

_, ax2 = plt.subplots()
ax2.set(xlabel="Year", ylabel="Value")
plt.plot(years, present_value_benefits[0])
plt.title("Present Value Benefit Difference: Owning Minus Renting")
for i in range(1, len(present_value_benefits)):
    plt.plot(years, present_value_benefits[i], ':', alpha=0.5, color='blue')
plt.plot([0] * np.arange(0, YEARS_OF_MORTGAGE), '--')
plt.savefig('output/graph_2.png')