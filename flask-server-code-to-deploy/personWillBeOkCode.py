
# code below on logging from: https://realpython.com/python-logging/
import logging
import json
import string

def getRMDPercentage(age):

    f = open("table_iii.json", "r")
    rmd = json.loads(f.read())

    if age>=120:
        d = rmd["120"]["distribution_period"]
        return (1/d)
    else:
        d = rmd[str(age)]["distribution_period"]
        return (1/d)

# def getRMDPercentage(z):
#     return 0.1
#logging.basicConfig(filename='personWillBeOk-debug.log', filemode='w', format='%(asctime)s - %(message)s')
#logging.warning('This will get logged to a file')
def growAccounts(future_balances_all_accounts):
    current_investment_account_balance = 0
    for acnt in future_balances_all_accounts:
        acnt["current_balance_investment_accounts"] += (acnt["current_balance_investment_accounts"] * acnt["rate_of_return_all_investments"]) + acnt["total_yearly_investment_contribution"]
        current_investment_account_balance += acnt["current_balance_investment_accounts"]
    return current_investment_account_balance



def personWillBeOk(input):
    debugfile = open('personWillBeOk-debug.log', "w")
    # check whether person will last through retirement:
    current_income = float(input["total_current_income"])
    current_spending = float(input["current_annual_spending"])
    accounts = input["accounts"]
    # this is the sum of all Ci from each account
    current_contributions = sum([float(acnt["total_yearly_investment_contribution"]) for acnt in accounts])
    #current_investment_account_balance = float(input["current_balance_investment_accounts"])
    current_investment_account_balance = sum([float(acnt["current_balance_investment_accounts"]) for acnt in accounts])
    #investment_return_rate = float(input["rate_of_return_all_investments"])
    future_balances_all_accounts = [{"type": acnt["type"],
                                    "current_balance_investment_accounts": float(acnt["current_balance_investment_accounts"]),
                                    "total_yearly_investment_contribution": float(acnt["total_yearly_investment_contribution"]),
                                    "rate_of_return_all_investments": float(acnt["rate_of_return_all_investments"])
                                    }
                                    for acnt in accounts]
    current_taxes = float(input["current_amount_paying_in_taxes_annually"])
    current_age = int(input["current_age"])
    retirement_age = int(input["retirement_age"])
    monthly_pension_check = float(input["expected_monthly_pension_check_amount_in_retirement"])
    monthly_social_security_check = float(input["expected_monthly_SS_check_amount_in_retirement"])
    expected_inflation = float(input["expected_inflation"])
    expected_salary_increase = float(input["expected_salary_increase"])
    death_age = retirement_age + int(input["expected_number_of_years_left_to_live_after_retirement"])
    post_retirement_taxes = float(input["expected_amount_will_pay_in_taxes_annually_in_retirement"])
    post_retirement_spending = float(input["expected_annual_spending_in_retirement"])
    post_retirement_part_time_income = float(input["expected_part_time_job_annual_income_in_retirement"])
    #brokerage_balance = 0
    # for acnt in accounts:
    #     if ((acnt["type"] == "Brokerages") or (acnt["type"] == "Brokerage")):
    #         brokerage_balance = acnt["current_balance_investment_accounts"]

    # how will we handle taxes on brokerage?:
    # brokerage_tax = input["brokerage_taxes_on_gains"]
    investment_growth = 0.0
    remaining_money = 0.0
    balanceForAnnuityCheck = 0

    # note: python does not store references to atomic variables so I must pass in age and contributions (int and float) but
    # do not need to pass in future_balances_all_accounts since the function below is within scope that declared the dictionary (nonatomic variable)
    def adjustIncomeToAge(age, current_contributions):
        income = 0
        # after 65 add back HSA contributions to income (since >=65 not allowed to contribute to HSA)
        if (age >= 65):
            for acnt in future_balances_all_accounts:
                if (acnt["type"] == "HSA"):
                    current_contributions -= acnt["total_yearly_investment_contribution"]
                    income += acnt["total_yearly_investment_contribution"]
                    debugfile.write("income" + str(income) + "\n")
                    acnt["total_yearly_investment_contribution"] = 0
        # after 72 person must take out of traditional ira accounts (we assume they don't take out required min distributions from their current traditional 401ks)
        if (age >= 72):
            for acnt in future_balances_all_accounts:
                if ((acnt["type"] == "Trad IRA") or (acnt["type"] == "Traditional IRA")):
                    income += acnt["current_balance_investment_accounts"] * getRMDPercentage(age)
                    debugfile.write("adding req min dist %: " + str(getRMDPercentage(age)) + "\n")
                    acnt["current_balance_investment_accounts"] -= income
        return (income, current_contributions)

    for y in range(current_age, retirement_age):
        #print(current_income)
        print(y)
        incomecont =  adjustIncomeToAge(y, current_contributions)
        current_income += incomecont[0]
        current_contributions = incomecont[1]
        remaining_money = (current_income + remaining_money) - current_spending - current_contributions - current_taxes
        # remaining_money -= additional_yearly_spending
        # additional_yearly_spending = 0
        debugfile.write("At iter " + str(y) + ":current_investment_account_balance= " + str(current_investment_account_balance) + ", remaining_money = " + str(remaining_money) + "\n")
        debugfile.write("income " + str(current_income) + " spending : " + str(current_spending) + " contributions " + str(current_contributions) + " taxes: " + str(current_taxes) + "\n")
        debugfile.write("accounts : \n")
        for acnt in future_balances_all_accounts:
            debugfile.write(acnt["type"] + " balance: " + str(acnt["current_balance_investment_accounts"]) + "\n")
        if (remaining_money < float(0)):
            # check brokerage: (assume user can only take out of brokerage in excess spending before retirement)
            # todo?: - taxes_on_gains
            for acnt in future_balances_all_accounts:
                if ((acnt["type"] == "Brokerages") or (acnt["type"] == "Brokerage")):
                    brokerage_balance = acnt["current_balance_investment_accounts"]
                    if (brokerage_balance > 0):
                        if ((brokerage_balance - abs(remaining_money))  < 0):
                            debugfile.write("brokerage not enough: " + str((brokerage_balance - abs(remaining_money))) + "\n")
                            return {"personisOk" : False,
                                    "yearZMoneyLastsUpTo": y,
                                    "moneyLeftAfterExpensesByYearZ": remaining_money,
                                    "amountInAllRetAccountsAtEndOfSimltn": current_investment_account_balance,
                                    "balanceForAnnuityCheck" : balanceForAnnuityCheck,
                                    "retiredcheck": False,
                                    "yearly_income": current_income,
                                    "yearly_spending": current_spending
                                    }
                        else:
                            acnt["current_balance_investment_accounts"] -= abs(remaining_money)
                            remaining_money = 0
                            debugfile.write("brokerage covers, new brokerage_balance: " + str(acnt["current_balance_investment_accounts"] ) + "\n")


            # additional_yearly_spending += taxes_on_gains
            # return false and the year user would run out of money
            #return {"personisOk" : False, "yearMoneyLastsUpTo": y, "moneyLeftAtEndOfYear": remaining_money, "amountInRetirement": current_investment_account_balance}
        #else:
            # calculate how much new worth grew in year

            #investment_growth = current_investment_account_balance * investment_return_rate
            #current_investment_account_balance += investment_growth + current_contributions
            # for acnt in future_balances_all_accounts:
            #     acnt["current_balance_investment_accounts"] += (acnt["current_balance_investment_accounts"] * acnt["rate_of_return_all_investments"]) + acnt["total_yearly_investment_contribution"]
            #     current_investment_account_balance += acnt["current_balance_investment_accounts"]
            # debugfile.write("At iter " + str(y) + ":current_investment_account_balance= " + str(current_investment_account_balance) + ", remaining_money = " + str(remaining_money) + "\n")
            # debugfile.write("income " + str(current_income) + " spending : " + str(current_spending) + " contributions " + str(current_contributions) + " taxes: " + str(current_taxes) + "\n")

        current_investment_account_balance = growAccounts(future_balances_all_accounts)
        debugfile.write("accounts after growth : \n")
        for acnt in future_balances_all_accounts:
            debugfile.write(acnt["type"] + " balance: " + str(acnt["current_balance_investment_accounts"]) + "\n")


            # todo:
        # account of expected_inflation
        current_spending += (current_spending * expected_inflation)
        # acount for expected_salary_increase
        current_income += (current_income * expected_salary_increase)
            # future updates:
            #  break down new worth calculation to individual accounts:

            # for each Ci: (i in {traditional IRA, traditional 401k, roth IRA, roth 401k, after-tax 401k, HSA, brokerage})
            #     if i is in 401k then add employer contribution to Ci put into traditional 401k
            #     Growth-of-i-account = account i balance * account i rate of return
            #     Account-i-new-balance += Ci + Growth-of-i-account
            #     T = T + Account-i-new-balance
    balanceForAnnuityCheck = current_investment_account_balance
    for acnt in future_balances_all_accounts:
        if (acnt["type"] == "HSA"):
            balanceForAnnuityCheck = current_investment_account_balance - acnt["current_balance_investment_accounts"]
            break

    for z in range(retirement_age, death_age):
        #[checked] todo: calculate RMD after 72 and add to salary:
            # RMD @ z = (required minimum distribution) withdrawal at year z = (amount in traditional IRA in year z =  user input is amount in starting balance in T-C2a * ) * (rmd percentage  user is required to withdraw in year z from IRS)
            # T -= RMD @ z
        # calculating RMD:
        post_ret_income = 0
        #post_ret_income += adjustIncomeToAge(future_balances_all_accounts,z, current_contributions)
        incomecont =  adjustIncomeToAge(z, current_contributions)
        post_ret_income += incomecont[0]
        debugfile.write("\n incomecont[0]" + str(incomecont[0])  + " incomecont[1]" + str(incomecont[1]))
        current_contributions = incomecont[1]
        debugfile.write("\n post_ret_income b4 ss and pension " + str(post_ret_income) + "\n")

        #moved to helper:
        # if (z >= 72):
        #     for acnt in future_balances_all_accounts:
        #         if ((acnt["type"] == "Trad IRA") or (acnt["type"] == "Traditional IRA")):
        #             post_ret_income = acnt["current_balance_investment_accounts"] * getRMDPercentage(z)
        #             debugfile.write("adding req min dist %: " + str(getRMDPercentage(z)) + "\n")
        #             acnt["current_balance_investment_accounts"] -= post_ret_income

        #["checked"] todo: calculat total contributions
        # if ( z < year user turns 65 or starts to receive social security check):
        #     C = C2a + C2b + C3 + C4
        #
        # else:
        #     // at this point in user gets Medicare, so they can't make any more contributions to HSA (C3 = 0 here)
        #     C = C2a + C2b + C4
        # todo: remove expense from HSA yearly and add to spending
        # adding back HSA contribution if user > 65:
        # moved to helper:
        # if (z >= 65):
        #     for acnt in future_balances_all_accounts:
        #         if (acnt["type"] == "HSA"):
        #             post_ret_income += acnt["total_yearly_investment_contribution"]
        #             current_contributions -= acnt["total_yearly_investment_contribution"]
        #             acnt["total_yearly_investment_contribution"] = 0

        post_ret_income += (monthly_social_security_check * 12) + (monthly_pension_check * 12) + (post_retirement_part_time_income)
        remaining_money = (post_ret_income + remaining_money) - post_retirement_spending - current_contributions - post_retirement_taxes
        debugfile.write("At iter " + str(z) + ":current_investment_account_balance= " + str(current_investment_account_balance) + ", remaining_money = " + str(remaining_money) + "\n")
        debugfile.write("income " + str(post_ret_income) + " spending : " + str(post_retirement_spending) + " contributions " + str(current_contributions) + " taxes: " + str(post_retirement_taxes) + "\n")
        debugfile.write("accounts : \n")
        for acnt in future_balances_all_accounts:
            debugfile.write(acnt["type"] + " balance: " + str(acnt["current_balance_investment_accounts"]) + "\n")
        order_accounts = ["Brokerages", "Trad IRA", "Trad 401k", "Roth IRA", "Roth 401k"]
        if (remaining_money < 0):
            # todo: check other accounts to cover the remaining balance
                    # // check the traditional brokerage accounts:
                    # if (traditional brokerage amount - absoluteValue(remainingMoneyCanUseInZ)  ) < 0):
                    #     remaining = abs(traditional brokerage amount - absoluteValue(remainingMoneyCanUseInZ) )
                    #     Opostretirement += tax on capital gains on withdrawal;
            for acnt_type in order_accounts:
                for acnt in future_balances_all_accounts:
                    if (acnt["type"] == acnt_type):
                        if (remaining_money < 0):
                            acnt["current_balance_investment_accounts"] -= abs(remaining_money)
                            debugfile.write("\ndeducting from " + acnt["type"] )
                            if (acnt["current_balance_investment_accounts"]< 0):
                                remaining_money = acnt["current_balance_investment_accounts"]
                                acnt["current_balance_investment_accounts"] = 0
                            else:
                                remaining_money = 0
                            debugfile.write("\n new account balance" + str(acnt["current_balance_investment_accounts"]) + "remaining money "  + str(remaining_money))



                    # if (traditional IRA amount - remaining) < 0) :
                    #      remaining = abs(traditional IRA amounts - absoluteValue(remaining) )
                    #        Opostretirement += income tax on full amount of withdrawal;
                    # if (traditional 401k amount - remaining) < 0) :
                    #       remaining = abs(traditional 401k amount - absoluteValue(remaining) )
                    #         Opostretirement += tax on capital gains on withdrawal;
                    # if (roth IRA amount - remaining) < 0) :
                    #     remaining = abs(roth IRA amount - absoluteValue(remaining) )
                    # if (roth 401k amount - remaining) < 0) :
                    #     remaining = abs(roth 401k amount - absoluteValue(remaining) )
            # if (current_investment_account_balance - abs(remaining_money) >= float(0)):
            #     current_investment_account_balance -= abs(remaining_money)
            #     remaining_money = 0
                # add to taxes on withdrawal for next year
            if (remaining_money < float(0)):
                return {"personisOk" : False,
                        "yearZMoneyLastsUpTo": z,
                        "moneyLeftAfterExpensesByYearZ": remaining_money,
                        "amountInAllRetAccountsAtEndOfSimltn": current_investment_account_balance,
                        "balanceForAnnuityCheck": balanceForAnnuityCheck,
                        "retiredcheck": False,
                        "yearly_income": post_ret_income,
                        "yearly_spending": post_retirement_spending
                        }
                        #return (False,z, remaining_money, current_investment_account_balance)
        #else:

            # investment_growth = current_investment_account_balance * investment_return_rate
            # current_investment_account_balance += investment_growth + current_contributions
            # for acnt in future_balances_all_accounts:
            #     acnt["current_balance_investment_accounts"] += (acnt["current_balance_investment_accounts"] * acnt["rate_of_return_all_investments"]) + acnt["total_yearly_investment_contribution"]
            #     current_investment_account_balance += acnt["current_balance_investment_accounts"]
            # debugfile.write("At iter " + str(z) + ":current_investment_account_balance= " + str(current_investment_account_balance) + ", remaining_money = " + str(remaining_money) + "\n")
            # debugfile.write("income " + str(post_ret_income) + " spending : " + str(post_retirement_spending) + " contributions " + str(current_contributions) + " taxes: " + str(post_retirement_taxes) + "\n")
        current_investment_account_balance = growAccounts(future_balances_all_accounts)
        debugfile.write("accounts after growth : \n")
        for acnt in future_balances_all_accounts:
            debugfile.write(acnt["type"] + " balance: " + str(acnt["current_balance_investment_accounts"]) + "\n")

            # account of expected_inflation (assuming same rate postretirement?)
        post_retirement_spending += (post_retirement_spending * expected_inflation)





    #debugfile.close()
    return {"personisOk" : True,
            "yearZMoneyLastsUpTo": death_age,
            "moneyLeftAfterExpensesByYearZ": remaining_money,
            "amountInAllRetAccountsAtEndOfSimltn": current_investment_account_balance,
            "balanceForAnnuityCheck": balanceForAnnuityCheck,
            "retiredcheck": True,
            "yearly_income": post_ret_income,
            "yearly_spending": post_retirement_spending
            }
