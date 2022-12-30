# todo: finish 5, produce output
# make combined model function with constraints sum of Ci must be <= A - B - O
# make optfile
# test models
# figure out how utility function should look like

# in presentation give these todos: rebalancing, utility incorporation
# for now make combined model work
# connect with flask and pyomo
# have optimization maximize the expected return
# vidya said don't use monte carlo simulation: no benefit
# because prices are random and expected return over time will match index expected return


import copy
import json
import importlib.util
# import sys
# # # sys.path.append("../aaa_dgalPy")
# sys.path.append("./lib")
# # sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code/aaa_dgalPy")
import dgalPy as dgal
import pandas
import pandas_datareader.data as webscraper
from datetime import datetime
from pyomo.environ import *
import math
# from datasource.api using to get the logarithmic return of prices in calculating geometric mean below
import numpy as np
# problem with below so just summing the standard deviation
# from :https://www.statology.org/weighted-standard-deviation-in-python/
# from statsmodels.stats.weightstats import DescrStatsW



# must find webscraper that returns expenseratio of security
def getExpenseRatioAndDateOfInception(security):
    #  todo: if security type is a stock, return 0 (no expense ratios on stocks)
    etfFile = open("etf_options.json", "r")
    etfDict = json.loads(etfFile.read())
    # documentation referenced for try/except clause syntax: https://docs.python.org/3/tutorial/errors.html
    # try:
    exp_rat = etfDict[security]["Expense Ratio"]
    inc_date = etfDict[security]["Inception Date"]
    # except Exception as e:
    #     print(e)
    #     return {"error": e}

    etfFile.close()
    return {"exp_rat": exp_rat, "inc_date": inc_date}

# must find webscraper to return dateofInception:
# ToDO: replace with extracting data of inception for a security (either from a db or other webscraper)
# def getDateOfInception(securityTicker):
#     #return datetime(end.year - 30, end.month, end.day)
#     return "needToGETFromDB"
# todo: make database holding legal limits for each account_type
def getLegalLimits(account_type, age):
    # Vidya and Bruce:
    # make database holding limits for >50, <50 for all the accounts
    # two columns: >50, <50  each row in column: 2022/2023 maximum limit
    # if (account_type == "IRA"):
    #     return 6500
    # elif (account_type == "401k"):
    #     return 22500
    # elif (account_type == "HSA"):
    #     return 3800
    # elif (account_type == "Trad IRA"):
    #     return 6500
    # elif (account_type == "Roth IRA"):
    #     return 3800
    # elif (account_type == "all"):
    #     return 3800
    # elif (account_type == "Trad 401k"):
    #     return 22500
    IRSLimitsFile = open("IRSLimits.json", "r")
    IRSLimitsDict = json.loads(IRSLimitsFile.read())

    limit = IRSLimitsDict[account_type]["limit"]
    if (age >= 50):
        limit += IRSLimitsDict[account_type]["catch_up"]
    IRSLimitsFile.close()
    return limit


# # calculate and return the betaValue of the security
# def getBetaValue(security):
#     return 1.0
#
# # calculate and return the sharpe ratio of the security:
# def getSharpeRatio(security):
#     return 3.0


# useful links to calc expected return of portfolio = sum(annualized rate of return (geometric mean) * weight of asset in portfolio)
#  annualized return code ex: https://python.plainenglish.io/calculating-annualized-expected-stock-returns-using-python-aaba430ca8a9
#   calcs useful metrics - log return inst geometric as above https://www.datasource.ai/uploads/1c79c40efac8fff409e7c23fe8167d04.html
#   calcs annualized expected returns using simple daily return * 250 to get yearly rate of return (annualized return)
#   ** really useful article: https://www.investopedia.com/articles/08/annualized-returns.asp
#     - says geometric mean better (1.rateofreturnasset1)*(1.rateofreturnasset2) ^ 1/2 - 1 shows the return of investment more accurately than just averaging yearly rate of returns since it accounts for compoundin
#       https://www.investopedia.com/terms/c/cagr.asp
#   video gives good info on different types of returns: https://www.youtube.com/watch?v=xpUpwEsMV9Y
#

def calcOtherMetrics(startyr, endyr, yearly_C, newAssetInfo, portfolio_expected_return, total_cost_incurred_by_end_of_range, total_account_balance_at_end_of_range, total_account_balance_each_year ):
    for y in range(startyr, endyr):
        growth = total_account_balance_at_end_of_range * portfolio_expected_return
        growth += yearly_C
        #total_growth_of_account_over_range += growth
        total_account_balance_at_end_of_range += growth
        #   calculation for cost: in terms of expense ratios (leave out taxes for now - user input taxes - assume its standard )
        # do we want to include inflation?
        # interesting: optimizer gives this issue since multiplying objective (total_account_balance) by weight (decision variable):
        #RuntimeError: Selected solver is unable to handle objective functions with quadratic terms. Objective at issue: pyomoObjective.
        total_yearly_cost = sum([newAssetInfo[security]["expense_ratio"]* newAssetInfo[security]["weight"] * total_account_balance_at_end_of_range
                                for security in newAssetInfo])

        total_cost_incurred_by_end_of_range += total_yearly_cost
        total_account_balance_at_end_of_range -= total_yearly_cost
        total_account_balance_each_year.append(total_account_balance_at_end_of_range)
        # total_account_balance_at_end_of_range += yearly_C
    return {
        "total_cost_incurred_by_end_of_range" : total_cost_incurred_by_end_of_range,
        "total_yearly_cost" : total_yearly_cost,
        "total_account_balance_at_end_of_range" :  total_account_balance_at_end_of_range,
        "total_account_balance_each_year" : total_account_balance_each_year
    }

def getYearCost(newAssetInfo, total_account_balance_at_end_of_range ):
    return sum([newAssetInfo[security]["expense_ratio"]* newAssetInfo[security]["weight"] * total_account_balance_at_end_of_range
                for security in newAssetInfo])

# now: if treat as one account: run twice before and after retirement -  because O changes, A and B changes
def singleAccountMod(input):

    # separat the input into variables:
    # get user info
    total_current_income = float(input["user_information"]["total_current_income"])
    current_spending = float(input["user_information"]["current_spending"])
    current_amount_paying_in_taxes_annually = float(input["user_information"]["current_amount_paying_in_taxes_annually"])
    startyr = int(input["user_information"]["year_range_running_model_on"]["start_age"])
    endyr = int(input["user_information"]["year_range_running_model_on"]["end_age"])
    retirement_age = int(input["user_information"]["retirement_age"])

    # get account info
    asset_info = input["account_information"]["account_asset_info"]
    # note: Pyomo throws type error when try to convert yearly_C to float - don't convert decision variables
    yearly_C = input["account_information"]["total_yearly_investment_contribution"]
    investment_starting_balance = float(input["account_information"]["current_balance_investment_account"])
    account_type = input["account_information"]["account_type"]
    yrs_til_retirement = retirement_age - startyr
    # metrics: expected return, cost, volatility (standard deviation)


    # Important notes on calculating expected return:
#     Calculating Ei:
# Sources ([57,58]) calculate simple annualized return rate: (mean daily return in adjusted close prices  * 250/252 trading days/yr)
# Geometric Mean: more accurate (accounts for growth on reinvestments) [59,60]
# What we are deciding on:
#  use the expected return from the past 10 years for each security
# Currently: calculating geometric mean with yearly returns


    # calculate expected return = sum(asset allocation value for a security key in asset_allocations * a security's annualized expected return)
    # According to https://www.w3schools.com/python/python_datetime.asp : datetime.now() gets todays date, and year,month, and day properties can be accessed with .
    # According to https://pandas-datareader.readthedocs.io/en/latest/remote_data.html#remote-data-yahoo : datetime.today() also gets todays date

    #
    # IMPORTANT NOTE: code below from the following sources:
        # https://python.plainenglish.io/calculating-annualized-expected-stock-returns-using-python-aaba430ca8a9
        # https://medium.com/python-data/calculating-expected-rates-of-returns-for-a-portfolio-of-stocks-with-python-e3afbd4eeba5
        # https://www.datasource.ai/uploads/1c79c40efac8fff409e7c23fe8167d04.html
    # code below based on the following: https://www.investopedia.com/terms/a/annualize.asp
    # code from the first 2 links above, calculates the annualized return by multiplying the average of  the daily returns over some number of years by number of trading days in a year
    # so I followed their algorithm below
    endDay = datetime.today()
    #startDay = getDateOfInception("TBD")
    startDay = datetime(endDay.year - 30, endDay.month, endDay.day)


    # how to calculate annual return?
    # ** if assumed the investor reinvested their earnings, then must multiply annual returns (have another loop)
    # geometric mean?: https://www.investopedia.com/terms/g/geometricmean.asp
    # how will we account for dividends (adjusted close price includes this see the link above it)

    # **really important article link says more realistic figure of expected return is geometric mean, gives example to calculate geometric mean: https://www.investopedia.com/articles/08/annualized-returns.asp

    # calculating expected return using simple average annual return of each asset
    portfolio_expected_return = 0
    asset_std_devs = dict()
    all_asset_returns = pandas.DataFrame()
    #security_returns = pandas.DataFrame()
    newAssetInfo = dict()
    for securityTicker in asset_info:
        info = getExpenseRatioAndDateOfInception(securityTicker)
        incption = info["inc_date"]
        expense_ratio = info["exp_rat"]
        security_returns_list = list()
        # get date of inception
        print("ticker getting info for: ", securityTicker)
        holder_df = webscraper.DataReader(securityTicker, data_source="yahoo", start = incption, end = endDay)
        # daily_adj_close_prices is a one column dataframe (called a Series in Pandas) which holds the closing prices
        # for the securityTicker everyday from 30 years from today to today
        # according to this link: https://www.investopedia.com/ask/answers/06/adjustedclosingprice.asp  :
        #   its better to use adjusted close price for calculating financial metrics since this price = price after any stock dividends or splits are given to the investor (who bought the shares)
        daily_adj_close_prices = holder_df["Adj Close"]
        print(daily_adj_close_prices)
        # according to: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pct_change.html
        #    pct_change() method is called on a Pandas series (one column dataframe) and returns how much
        #    the price changed from the previous day (in the previous row)
        #    so according to example under the link above:
            #     if dataFrame x = pd.Series([90,91]), then x.pct_change() returns a series with Nan in first row (since no row exists prior to first), and .011 in second = current row val - prev row val/ prev row =
            #     91 - 90 / 90 = .011
        #all_yr_daily_returns = daily_adj_close_prices.pct_change()

        # code below calculates geometric mean by implementing the formula from the links below:
        # https://www.investopedia.com/terms/g/geometricmean.asp
        # https://www.investopedia.com/articles/08/annualized-returns.asp

        # references used to make the following code:
        #  https://www.datasource.ai/uploads/1c79c40efac8fff409e7c23fe8167d04.html
        # geom_mean = 1
        # I use this counters to separate the dataframe of close prices by year
        # first_trade_day = 0
        # last_trade_day = 252
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.size.html - this link describes that size property gets the number of rows in the pandas series
        # so I use it to get the number of days in the dataframe
        #numYearsOfReturns = int(daily_adj_close_prices.size/252)
        days_hold = int(yrs_til_retirement * 252)
        print("daily_adj_close_prices.size", daily_adj_close_prices.size)
        # PROBLEM: if days to retirement > adjusted close prices available, then just take total return from day 0 (inception date) to current date/2 (so that standard deviation won't be 0) -> error
        # not sure how to get more data
        if (daily_adj_close_prices.size < days_hold):
            days_hold = int(daily_adj_close_prices.size/2)
            # use SPY for us or some really old international fund?
        lastPoint = int(daily_adj_close_prices.size/days_hold )
        print("yrs_til_retirement:", yrs_til_retirement)
        for i in range(lastPoint):
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.iloc.html - according to this link
            # can use iloc[slice] - to get a portion of rows from the pandas dataframe
            # I use the property to get the close prices for each year (from first to last trading day of that year (+250 rows for 250 trading days in a year according to: https://python.plainenglish.io/calculating-annualized-expected-stock-returns-using-python-aaba430ca8a9 ))
            #yrly_prices = daily_adj_close_prices.iloc[first_trade_day: last_trade_day]
            # yrly_returns = np.log((yrly_prices/yrly_prices.shift(1)))
            print("daily_adj_close_prices.iloc[i + days_hold]:", daily_adj_close_prices.iloc[i + days_hold - 1])
            time_forward = (i + days_hold) - 1
            security_returns_list.append( float((daily_adj_close_prices.iloc[time_forward])/(daily_adj_close_prices.iloc[i])))
            #yrly_returns = yrly_prices.pct_change()
            #yr_i_annualized_return = yrly_returns.mean() * 252
            # first_trade_day += 252
            # last_trade_day += 252
            # geom_mean = geom_mean * (1 + yr_i_annualized_return)
        # according to https://www.w3schools.com/python/ref_math_pow.asp :
        # math.pow() function returns the first argument raised to the power of the second argument
        # I used this function to calculate geometric mean below
        #geom_mean = (math.pow(geom_mean, (1/numYearsOfReturns))) - 1
        #annualized_rate_of_return = daily_returns.mean() * 250
        print(security_returns_list)
        security_returns_pd = pandas.Series(security_returns_list)
        avg_return_for_days_held = security_returns_pd.mean()
        annualized_avg_rate_of_return = math.pow((avg_return_for_days_held), (1/yrs_til_retirement)) - 1
        # storing information for calculating standard deviation of returns
        security_rates_pd = pandas.Series([math.pow(x, 1/yrs_til_retirement) - 1 for x in security_returns_list])
        all_asset_returns[securityTicker] = security_rates_pd
        annualized_security_std_dev = security_rates_pd.std()
        #annualized_avg_rate_of_return = security_rates_pd.mean()
        asset_std_devs.update({securityTicker: annualized_security_std_dev})

        newAssetInfo.update({securityTicker: {
                                    "weight": asset_info[securityTicker]["weight"],
                                     "dateOfInception": incption,
                                     "expense_ratio": expense_ratio,
                                     "std_dev_since_inception": annualized_security_std_dev,
                                     "annualized_rate_of_return": annualized_avg_rate_of_return
                                     # "betaValue": getBetaValue(securityTicker),
                                     # "sharpeRatio": getSharpeRatio(securityTicker)
                                     }
                            })
        # total_annualized_return *= (1 + annualized_rate_of_return)
        # pow(end)
        portfolio_expected_return += asset_info[securityTicker]["weight"] * annualized_avg_rate_of_return


    # followed the equation at the links below to calculate portfolio standard deviation:
    # https://www.wallstreetmojo.com/portfolio-standard-deviation/
    # according to this link: https://www.investopedia.com/terms/v/volatility.asp :
    #   standard deviation is a metric frequently used to measure volatility (since prices are usually normally distributed according to the link's description)

    # Referenced the following documentation to understand and use the methods in calculating standard deviation below:
    # for corr() : https://www.w3schools.com/python/pandas/pandas_correlations.asp
    # for fillna(): https://www.w3schools.com/python/pandas/pandas_cleaning_empty_cells.asp
    # according to https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html :
        # to access the rows of the dataframe (asset_correlation_matrix) can use index
        # to access the columns of the dataframe can use columns property
        # to access a specific element can use .loc
    # also to get specific element can use .loc[dataframe row, dataframe column] according to https://pandas.pydata.org/docs/user_guide/indexing.html

    asset_correlation_matrix = all_asset_returns.corr()
    asset_correlation_matrix.fillna(0)
    portfolio_var = sum([
                        (asset_info[r]["weight"] * asset_info[c]["weight"]* asset_std_devs[r] * asset_std_devs[c] * asset_correlation_matrix.loc[r,c])
                        for r in asset_correlation_matrix.index
                        for c in asset_correlation_matrix.columns
                    ])

    # optimizer cannot handle math.sqrt: throws type error - "Implicit conversion of Pyomo numeric value"
    # so just take sqrt of variance returned
    # fix from this link (import * from pyomo fixes the math.sqrt problem) - https://stackoverflow.com/questions/48171498/finding-pyomo-provided-math-functions
    portfolio_std_dev = sqrt(portfolio_var)


    print(newAssetInfo)

    # replace with calculation for volatility (either standard deviation, or beta values, or sharpe ratio):
    volatility = portfolio_var

    portfolio_var_proxy = 0
    for asset in asset_info:
        portfolio_var_proxy += asset_info[asset]["weight"] * asset_std_devs[asset]

    #portfolio_var_proxy = portfolio_std_dev
    # another measure for volatility (user may not be familiar):
    # portfolio_beta =  (input["%_allocation_VTI"] * beta of VTI)
    #                             + (input["%_allocation_VOO"] * beta of Voo)
    #                             + (input["%_allocation_VXUS"] * beta of BND)
    #                             + (input["%_allocation_BND"] * beta of BND)


    # replace with calcualtion for growth of investment account over year range
    total_account_balance_at_end_of_range = investment_starting_balance
    total_cost_incurred_by_end_of_range = 0
    total_growth_of_account_over_range = 0
    total_yearly_cost = 0
    total_expense_ratio_cost = 0
    total_account_balance_each_year = list()

    # interesting note:
    # adding the growth within loop to total_growth_of_account_over_range
    # slows the optimizer substantially when total_growth_of_all_accounts (sum of total_growth_of_account_over_range for all accounts)
    # is the objective function
    # so I decided to use the calculation below instead of the loop (runtime to compute total_growth_of_account_over_range reduced from O(n), where n = number of years in [startyr, endyr], to O(1))
    # I decided to use the equation below because it combines expected return and contributions (decision variables), so the optimizer will produce
    # non-zero values for both when maximizing this objective
    length_run = endyr - startyr
    total_growth_of_account_over_range = (length_run * (total_account_balance_at_end_of_range * portfolio_expected_return)) + (length_run * (yearly_C))

    # for y in range(startyr, endyr):
    #     total_yearly_cost = sum([newAssetInfo[security]["expense_ratio"]* newAssetInfo[security]["weight"] * total_account_balance_at_end_of_range  for security in newAssetInfo])
    #
    #     total_cost_incurred_by_end_of_range += total_yearly_cost
    #     total_account_balance_at_end_of_range -= total_yearly_cost

    # maybe cancel the helper function and just use this code:
    # def calcOtherMetrics(startyr, endyr, yearly_C, newAssetInfo, portfolio_expected_return, total_cost_incurred_by_end_of_range, total_account_balance_at_end_of_range, total_account_balance_each_year ):
    # for y in range(startyr, endyr):
    #     growth = total_account_balance_at_end_of_range * portfolio_expected_return
    #     growth += yearly_C
    #     #total_growth_of_account_over_range += growth
    #     total_account_balance_at_end_of_range += growth
    #         #   calculation for cost: in terms of expense ratios (leave out taxes for now - user input taxes - assume its standard )
    #         # do we want to include inflation?
    #         # interesting: optimizer gives this issue since multiplying objective (total_account_balance) by weight (decision variable):
    #         #RuntimeError: Selected solver is unable to handle objective functions with quadratic terms. Objective at issue: pyomoObjective.
    #     total_yearly_cost = sum([newAssetInfo[security]["expense_ratio"]* newAssetInfo[security]["weight"] * total_account_balance_at_end_of_range
    #                             for security in newAssetInfo])
    #
    #     total_cost_incurred_by_end_of_range += total_yearly_cost
    #     total_account_balance_at_end_of_range -= total_yearly_cost
    #     # total_account_balance_minus_std_dev += ((((total_account_balance_minus_std_dev) * (portfolio_expected_return - portfolio_std_dev)) + yearly_C) - getYearCost(newAssetInfo, total_account_balance_minus_std_dev ))
    #     # total_account_balance_plus_std_dev += ((((total_account_balance_minus_std_dev) * (portfolio_expected_return + portfolio_std_dev)) + yearly_C) - getYearCost(newAssetInfo, total_account_balance_plus_std_dev ))
    #     total_account_balance_each_year.append(total_account_balance_at_end_of_range)
            # total_account_balance_at_end_of_range += yearly_C

    # question for Vidya should we add yearly_C to total cost?
    # for y in range(startyr, endyr):
    #     total_account_balance_at_end_of_range += yearly_C

    metricCalcs = calcOtherMetrics(startyr, endyr, yearly_C, newAssetInfo, portfolio_expected_return, total_cost_incurred_by_end_of_range, total_account_balance_at_end_of_range, total_account_balance_each_year )
    total_cost_incurred_by_end_of_range = metricCalcs["total_cost_incurred_by_end_of_range"]
    total_yearly_cost = metricCalcs["total_yearly_cost"]
    total_account_balance_at_end_of_range = metricCalcs["total_account_balance_at_end_of_range"]
    total_account_balance_each_year = metricCalcs["total_account_balance_each_year"]

    metricCalcsMinusOneStd = calcOtherMetrics(startyr, endyr, yearly_C, newAssetInfo, (portfolio_expected_return - portfolio_std_dev), 0, investment_starting_balance, [] )
    total_cost_incurred_minus = metricCalcsMinusOneStd["total_cost_incurred_by_end_of_range"]
    total_yearly_cost_minus = metricCalcsMinusOneStd["total_yearly_cost"]
    total_account_balance_minus_std_dev = metricCalcsMinusOneStd["total_account_balance_at_end_of_range"]
    total_account_balance_each_year_minus = metricCalcsMinusOneStd["total_account_balance_each_year"]

    metricCalcsPlusOneStd = calcOtherMetrics(startyr, endyr, yearly_C, newAssetInfo, (portfolio_expected_return + portfolio_std_dev), 0, investment_starting_balance, [] )
    total_cost_incurred_plus = metricCalcsPlusOneStd["total_cost_incurred_by_end_of_range"]
    total_yearly_cost_plus = metricCalcsPlusOneStd["total_yearly_cost"]
    total_account_balance_plus_std_dev = metricCalcsPlusOneStd["total_account_balance_at_end_of_range"]
    total_account_balance_each_year_plus = metricCalcsPlusOneStd["total_account_balance_each_year"]


    # constraints:
    # 1. % in VTI + % in VOO + % in VXUS + % in BND = 1
    assetWeightsSum = sum([asset_info[security]["weight"] for security in asset_info])
    assetWeightsSumWithinRange = (assetWeightsSum >= 0.999)
    #assetWeightsSumWithinRange = True

    assetWeightsSumLessThanOne = (assetWeightsSum <= 1)
    assetWeightsSumToOne = dgal.all([assetWeightsSumWithinRange, assetWeightsSumLessThanOne])

    #2 % in VTI >= 0, % in VOO >= 0, % in VXUS >= 0, % in BND >= 0:
    allAssetWeightsGreaterThanEqualZero = dgal.all([asset_info[security]["weight"] >= 0 for security in asset_info])

    # 3 yearly Contribution amount >= 0
    yearlyContributionGreaterThanEqualZero = (yearly_C >= 0)


    # assuming legal limits for user's current age (at time of input to model)
    accountLegalLimits = getLegalLimits(account_type, startyr)
    #4 legal limits on C:
    legalYearlyLimitsOnContributionSatisfied = (yearly_C <= accountLegalLimits  )

    #5 age limits on C:
    # - we assume that after retirement the user does not contribute to their 401k - contribute to another account (IRA or brokerage)
    # question for Professor: should we ask the user for employer constraints on maximum % of salary they can contribute to a 401k or leave it?

    if ((startyr >= retirement_age and (account_type == "Trad 401k" or account_type == "Roth 401k")) or (startyr >= 65 and account_type == "HSA")):
        ageLegalLimitsOnContributionSatisfied = (yearly_C == 0)
    else:
        ageLegalLimitsOnContributionSatisfied = True
    # note: in combined function: yearly Contribution amount <= annual salary - annual spending - annual taxes
    years_left_til_retirement = retirement_age - startyr

    # 6 allocateMoreAccordingToTraits
    allocateMoreAccordingToTraits = True

    def getLeastRiskyAsset():
        # call getBetaValue
        # calculate and return the asset with the lowest beta value (farthest from 1, closest to 0)
        #return asset_info["BND"]
        # new: return the asset with lowest std dev
        minStdDev = min([asset_std_devs[security] for security in asset_std_devs])
        for security in asset_std_devs:
            if (asset_std_devs[security] == minStdDev):
                return security
    def getHighestReturnAsset():
        # call getSharpeRatio
        # calculate and return the asset with the highest sharpe ratio or beta value
        # with sharpe ratio choose to allocat more in funds with ratio closer to 3 (since these mean they are returning more than the risk)
        #return asset_info["VTI"]
        # return asset with the highest expected return
        maxRateOfReturn = max([newAssetInfo[security]["annualized_rate_of_return"] for security in newAssetInfo])
        for security in newAssetInfo:
            if (newAssetInfo[security]["annualized_rate_of_return"] == maxRateOfReturn):
                return security
    highestAllocationSecurity = ""

    # todo put this in the presentation: found evidence to support the constraint logic below : https://en.wikipedia.org/wiki/Trinity_study
    # yes we are considering investment_starting_balance = to net worth:
    # todo: find  evidence that shows a set age at which to shift most towards least risky asset
    # note: try to make the if statements so that bonds/least risky asset is not just 0 or 50%
    #or (current_spending > (0.04 * investment_starting_balance))
    #todo: leave out if can get pareto optimal stuff to work
    if (years_left_til_retirement < 20 or (current_spending > (0.04 * investment_starting_balance))):
        leastRiskyAsset = getLeastRiskyAsset()
        highestAllocationSecurity = leastRiskyAsset

        # % in BND >= % in VTI
        # % in BND >= % in Voo
        # % in BND >= % in VXUS
    else:
        highestReturnAsset = getHighestReturnAsset()
        highestAllocationSecurity = highestReturnAsset
        # % in VTI >= % in BND
        # % in VTI >= % in Voo
        # % in VTI >= % in VXUS
    print(highestAllocationSecurity)
    # allocateMoreAccordingToTraits = dgal.all([asset_info[highestAllocationSecurity]["weight"] >= asset_info[security]["weight"]
    #                                             for security in asset_info
    #                                             if (security != highestAllocationSecurity)
    #                                         ])
    allocateMoreAccordingToTraits = True

    # constraint 7:
    # ensure that the account contribution is <= A - B - O
    yearlyContributionWithInBudget = (yearly_C <= total_current_income - current_spending - current_amount_paying_in_taxes_annually)
    #yearlyContributionWithInBudget = (yearly_C <= retirement_income - ret_spending - ret_amount_paying_in_taxes_annually)
    constraints = dgal.all([
                            allAssetWeightsGreaterThanEqualZero,
                            assetWeightsSumToOne,
                            yearlyContributionGreaterThanEqualZero,
                            legalYearlyLimitsOnContributionSatisfied,
                            ageLegalLimitsOnContributionSatisfied,
                            allocateMoreAccordingToTraits,
                            yearlyContributionWithInBudget
                        ])
    return {
            "account_information" : {
                "account_type": account_type,
                "account_expected_return" : portfolio_expected_return,
                "account_variance": portfolio_var,
                "account_std_dev": portfolio_std_dev,
                "total_account_balance_minus_std_dev": total_account_balance_minus_std_dev,
                "total_account_balance_plus_std_dev" : total_account_balance_plus_std_dev,
                "total_growth_of_account_over_range": total_growth_of_account_over_range,
                "total_account_balance_at_end_of_range": total_account_balance_at_end_of_range,
                "total_cost_incurred_on_account_by_end_of_range": total_cost_incurred_by_end_of_range,
                "total_yearly_cost_on_account": total_yearly_cost,
                "portfolio_var_proxy" : portfolio_var_proxy,
                "constraints": constraints,
                "total_account_balance_each_year": total_account_balance_each_year,
                "debug": {
                    "constraintbreakdown": {
                        "allAssetWeightsGreaterThanEqualZero": allAssetWeightsGreaterThanEqualZero,
                        "assetWeightsSumToOne": assetWeightsSumToOne,
                        "yearlyContributionGreaterThanEqualZero": yearlyContributionGreaterThanEqualZero ,
                        "legalYearlyLimitsOnContributionSatisfied" : legalYearlyLimitsOnContributionSatisfied,
                        "ageLegalLimitsOnContributionSatisfied" : ageLegalLimitsOnContributionSatisfied ,
                        "allocateMoreAccordingToTraits" : allocateMoreAccordingToTraits,
                        "yearlyContributionWithInBudget" : yearlyContributionWithInBudget
                    }
                },
                "account_asset_info": newAssetInfo,
                "total_yearly_investment_contributions_to_account": yearly_C,
                "legal_limits_on_C_for_year_range": accountLegalLimits
            },
            "user_information": {
                "total_current_income": total_current_income,
                "current_spending": current_spending,
                "current_amount_paying_in_taxes_annually": current_amount_paying_in_taxes_annually,
                "year_range_running_model_on": input["user_information"]["year_range_running_model_on"],
                "retirement_age": retirement_age

            }
    }
    # if we use portfolio beta have constraint: portfolio beta <= 1
    # if we use standard deviation not sure what constraints to put on it

def combiningAccountsMod(input):
    # questions for Professor:
    # are we calculating expected return, and standard deviation for combining accounts properly?
    #utility = (weight * expected return) + (weight * volatility) + (weight * cost)
    # separate variables from input combined_accounts_model_input_structure.json
    subAccounts = input["account_information"]["subAccounts"]
    userInfo = input["user_information"]
    current_salary = userInfo["total_current_income"]
    current_spending = userInfo["current_spending"]
    current_taxes = userInfo["current_amount_paying_in_taxes_annually"]
    subAccountInputs = input["account_information"]["sub_account_inputs"]
    allSubAccountModelOutputs = {}

    # collect the outputs of single model on each subAccount
    for acnt in subAccounts:
        singleModelInput = dgal.merge([subAccountInputs[acnt], {"user_information": userInfo} ])
        singleModelOutput = singleAccountMod(singleModelInput)
        allSubAccountModelOutputs.update({acnt: singleModelOutput})

    #print(allSubAccountModelOutputs)
    # sum all account balances, standard deviation, and costs
    # get expected return for all the investments =
    # weight of account i = current_balance account i/ sum(current total account balances)
    # expected return of i (from output)
    # expected return = sum([account weight * expected return for i in accounts])

    #  calculate avg expected return and std deviation for all investments
    # get total money currently invested in all investment accounts (sum of current balances)
    total_money_invested = sum([subAccountInputs[acnt]["account_information"]["current_balance_investment_account"] for acnt in subAccountInputs])

    # according to links below:
    # https://www.itl.nist.gov/div898/software/dataplot/refman2/ch2/weightsd.pdf :
    # https://www.statology.org/weighted-standard-deviation-in-python/

    # calculate standard deviation using python pkg in second link
    total_expected_return = sum([allSubAccountModelOutputs[acnt]["account_information"]["account_expected_return"] for acnt in subAccounts])
    total_variance = sum([allSubAccountModelOutputs[acnt]["account_information"]["account_variance"] for acnt in subAccounts])
    total_variance_proxy = sum([allSubAccountModelOutputs[acnt]["account_information"]["portfolio_var_proxy"] for acnt in subAccounts])
    total_std_dev = sum([allSubAccountModelOutputs[acnt]["account_information"]["account_std_dev"] for acnt in subAccounts])


    # variances = []
    # account_weights = []
    # for acnt in subAccounts:
    #     # get weight of account in future
    #     accountCurrentBalance = subAccountInputs[acnt]["account_information"]["current_balance_investment_account"]
    #     accountWeight = accountCurrentBalance / total_money_invested
    #     accountExpectedReturn = allSubAccountModelOutputs[acnt]["account_information"]["account_expected_return"]
    #     accountVar = allSubAccountModelOutputs[acnt]["account_information"]["account_variance"]
    #     # optimizer does not like using below either (math.sqrt not from Pyomo)
    #     accountStdDev = accountVar
    #     variances.append(accountVar)
    #     account_weights.append(accountWeight)
    #     all_investment_accounts_avg_expected_return += (accountExpectedReturn * accountWeight)
    #     # not using this measure for averaging std_dev (?):
    #     all_investment_accounts_avg_std_dev += (accountStdDev * accountWeight)

    # problem with below code (divide by zero error)
    #all_investment_accounts_avg_std_dev = DescrStatsW(variances, weights=account_weights, ddof=1).std
    # calculate total potential balance of all investment accounts:
    total_balance_from_all_investments_at_end_of_year_range = sum([allSubAccountModelOutputs[acnt]["account_information"]["total_account_balance_at_end_of_range"] for acnt in allSubAccountModelOutputs])
    total_balance_from_all_investments_minus_std_dev = sum([allSubAccountModelOutputs[acnt]["account_information"]["total_account_balance_minus_std_dev"] for acnt in allSubAccountModelOutputs])
    total_balance_from_all_investments_plus_std_dev = sum([allSubAccountModelOutputs[acnt]["account_information"]["total_account_balance_plus_std_dev"] for acnt in allSubAccountModelOutputs])
    # calculate total cost incurred by end of year range on all investment accounts:
    total_cost_incurred_on_all_accounts_by_end_of_year_range = sum([allSubAccountModelOutputs[acnt]["account_information"]["total_cost_incurred_on_account_by_end_of_range"] for acnt in allSubAccountModelOutputs])

    total_growth_of_all_accounts = sum([allSubAccountModelOutputs[acnt]["account_information"]["total_growth_of_account_over_range"] for acnt in allSubAccountModelOutputs])

    # constraint that sum(Ci) <= salary - spending - taxes
    yearlyContributionsToAllAccounts = sum([subAccountInputs[acnt]["account_information"]["total_yearly_investment_contribution"] for acnt in subAccountInputs])
    moneyLeftEveryYear = current_salary - current_spending - current_taxes
    # constraint yearlyContributionsToAllAccountsInBudget:
    yearlyContributionsToAllAccountsInBudget = (yearlyContributionsToAllAccounts <= moneyLeftEveryYear  )
    subAccountConstraints = dgal.all([allSubAccountModelOutputs[acnt]["account_information"]["constraints"] for acnt in allSubAccountModelOutputs])
    constraints = dgal.all([yearlyContributionsToAllAccountsInBudget, subAccountConstraints])

    # Cancel code below:
    ####################################################3
    # IMPORTANT TODO: check with professor on whether this process of calc utility is correct
    # calculate utility with steps 1,2,3 below:
    # 1 normalize KPIs:
    # according to lecture notes:
    # if want to maximize metric:
        # normalize it using this equation: m = original value, M = normalized value
        #  M = max - m / max - min (will put value in [0,1])
    # if want to minimize metric:
        # normalize by doing: 1 - M

    # here kpis are expected return, standard deviation (volatility), and cost of maintenance:
    # want to maximize expected return so:
    # normalized_expected_return = (1.0 - all_investment_accounts_avg_expected_return)/ (1.0 - 0.0)
    # # want to minimize standard deviation, so:
    # # question for Professor: what is the maximum value of standard dev?
    # normalized_standard_deviation = "TBD"
    #
    # # what is the maximum total cost (do we calcluate using the maximum expense ratio on all accounts?)
    # normalized_cost = "TBD"
    #
    # # 2 get user weights (how much they value) for each kpi
    # userPreferenceExpectedReturn = userInfo["utility_of_expected_return"]
    # userPreferenceStdDev = userInfo["utility_of_std_dev"]
    # userPreferenceCost = userInfo["utility_of_total_cost"]
    #
    # # 3 calculate the utilityFunction
    #utilityFunction = (userPreferenceExpectedReturn * normalized_expected_return) + (userPreferenceStdDev * normalized_std_deviation) + (userPreferenceCost * normalized_cost)

    ###############################################################################
    return {
            # "utility": utilityFunction,
            "constraints": constraints,
            "total_balance_from_all_investments_at_end_of_year_range" : total_balance_from_all_investments_at_end_of_year_range,
            "total_expected_return" : total_expected_return,
            "total_variance": total_variance,
            "total_std_dev" : total_std_dev,
            "total_variance_proxy": total_variance_proxy,
            "total_balance_from_all_investments_minus_std_dev" : total_balance_from_all_investments_minus_std_dev,
            "total_balance_from_all_investments_plus_std_dev": total_balance_from_all_investments_plus_std_dev,
            "total_growth_of_all_accounts": total_growth_of_all_accounts,
            # "all_investment_accounts_avg_expected_return" : all_investment_accounts_avg_expected_return,
            # "all_investment_accounts_avg_std_dev": all_investment_accounts_avg_std_dev,
            "account_information": {
                "account_type": "combined",
                "subAccounts": subAccounts,
                "sub_account_outputs": allSubAccountModelOutputs
            },
            "user_information": userInfo

    }
