from modelcode import *
import dgalPy as dgal
import copy
import math

def getPrincipal(data):
    pmt = float(data["expected_annual_spending_in_retirement"])/12
    r = 0.02
    n = 12
    t = int(data["expected_number_of_years_left_to_live_after_retirement"])
    p = (pmt*(1-(math.pow(1+(r/n),(-n*t)))))/(r/n)
    return p

# formats arguments as "user_information" dictionary structure to be inputted into models
def packUserInfo(data, start_age, end_age, income, spending, taxes):
    return {
                    "total_current_income": income,
                    "current_spending": spending,
                    "current_amount_paying_in_taxes_annually": taxes,
                    "retirement_age": data["retirement_age"],
                    "year_range_running_model_on": {
                        "start_age": start_age,
                        "end_age": end_age

                    },
                    "utility_of_expected_return": data["how_important_expected_return_is_to_user"],
                    "utility_of_volatility": data["how_important_volatility_is_to_user"],
                    "utility_of_total_cost": data["how_important_cost_is_to_user"]

            }


# returns account info with decision variables (yearly_contribution and weights) annotated with dgal type real
# for optimizer to find values for
def packAnnotAccountInfo(type, current_balance, usChoice, intrnlChoice, bondChoice):
    return {
            "account_information": {
                "account_type": type,
                "account_asset_info": {
                    usChoice: {
                        "weight": {"dgalType": "real?"}
                    },
                    intrnlChoice: {
                        "weight": {"dgalType": "real?"}
                    },
                    bondChoice: {
                        "weight": {"dgalType": "real?"}
                    }
                },
                "total_yearly_investment_contribution": {"dgalType": "real?"},
                "current_balance_investment_account": current_balance
            }
    }

def normalizeAndMultAngle(metric, normOption, minvalue, maxvalue, angle):
    normalizedVal = ((metric - minvalue)/(maxvalue - minvalue))
    if (normOption == "max"):
        return normalizedVal * angle
    elif (normOption == "min"):
        return (1 - normalizedVal) * angle
    elif (normOption == "noNorm"):
        return metric
    else:
        return 0

# Note: we reused the code from Homework 2 and 3 in CS 787 (given by the Professor to invoke the optimizer and return packaged results) in runOptimizer()
def runOptimizer(annotated_input, firstMetricOpts, secondMetricOpts, optSetting):
    firstMetric = firstMetricOpts["metric"]
    normOptFirst = firstMetricOpts["normOpt"]
    firstAngle = firstMetricOpts["angle"]
    minFirst = firstMetricOpts["minVal"]
    maxFirst = firstMetricOpts["maxVal"]
    secondMetric = secondMetricOpts["metric"]
    normOptSecond = secondMetricOpts["normOpt"]
    secondAngle = secondMetricOpts["angle"]
    minSecond = secondMetricOpts["minVal"]
    maxSecond = secondMetricOpts["maxVal"]
    def constraints(o):
        return (dgal.all([ o["constraints"]]))

        #"total_growth_of_all_accounts"
    paramObj = {
        "model": combiningAccountsMod,
        "input": annotated_input,
        "obj": lambda o: normalizeAndMultAngle(o[firstMetric], normOptFirst, minFirst, maxFirst, firstAngle) + normalizeAndMultAngle(o[secondMetric], normOptSecond, minSecond, maxSecond, secondAngle), #utility = account balance * angle + std * angle
        "constraints": constraints,
        "options": {"problemType": "mip", "solver":"glpk","debug": True}
    }
    if (optSetting == "max"):
        optAnswer = dgal.max(paramObj)
    else:
        optAnswer = dgal.min(paramObj)

    # testcombinedannot = open("testcombinedannot.json", "w")
    # testcombinedannot.write(json.dumps(optAnswer["solution"]))
    optOutput = combiningAccountsMod(optAnswer["solution"])
    #optOutput = "testing"
    # dgal.debug("optOutput",optOutput)
    # dgal.debug("constraints", optOutput["constraints"])

    output = {
    #    "input":input,
    #    "varInput":varInput,
        "optAnswer": optAnswer,
        "optOutput": optOutput
    }
    return output

# returns the optimizer results including the following metrics:
# cumulative and each individual account's growth, total costs, variance, and expected return
# the optimal yearly contribution and asset allocations (as decimal value) for each account
def packOptimizerResults(sys_input, annotated_input, firstMetricOpts, secondMetricOpts, optSetting, subAccounts):
    optValues = runOptimizer(annotated_input, firstMetricOpts, secondMetricOpts, optSetting)
    sub_account_outputs = list()
    for acnt in subAccounts:
        sub_account_outputs.append(optValues["optOutput"]["account_information"]["sub_account_outputs"][acnt]["account_information"])

    inputted_accounts = sys_input["accounts"]
    # source for deepcopy (copies contents of dictionary): https://note.nkmk.me/en/python-copy-deepcopy/
    sub_account_outputs_updated = copy.deepcopy(sub_account_outputs)
    for acnt in inputted_accounts:
        for out_acnt in sub_account_outputs:
            if (acnt["type"] == out_acnt["account_type"]):
                usChoiceInfo = out_acnt["account_asset_info"][acnt["usChoice"]]
                usChoiceInfo.update({"ticker": acnt["usChoice"]})
                intrnlChoiceInfo = out_acnt["account_asset_info"][acnt["intrnlChoice"]]
                intrnlChoiceInfo.update({"ticker": acnt["intrnlChoice"]})
                bndChoiceInfo = out_acnt["account_asset_info"][acnt["bondChoice"]]
                bndChoiceInfo.update({"ticker": acnt["bondChoice"]})
                out_acnt.update({
                        "account_asset_info": {
                            "bondChoice": bndChoiceInfo ,
                            "usChoice": usChoiceInfo,
                            "intrnlChoice": intrnlChoiceInfo
                        }
                })

    return {
            # first listing combined metrics
            "constraints": optValues["optOutput"]["constraints"],
            "total_balance_from_all_investments_at_end_of_year_range": optValues["optOutput"]["total_balance_from_all_investments_at_end_of_year_range"],
            "total_balance_from_all_investments_plus_std_dev" : optValues["optOutput"]["total_balance_from_all_investments_plus_std_dev"],
            "total_balance_from_all_investments_minus_std_dev" : optValues["optOutput"]["total_balance_from_all_investments_minus_std_dev"],
            "total_expected_return": optValues["optOutput"]["total_expected_return"],
            "total_variance": optValues["optOutput"]["total_variance"],
            "total_std_dev": optValues["optOutput"]["total_std_dev"],
            "total_growth_of_all_accounts": optValues["optOutput"]["total_growth_of_all_accounts"],
            # then listing user metrics
            "user_information": optValues["optOutput"]["user_information"],
            # then listing each individual account metrics in a list
            "sub_account_outputs": sub_account_outputs

    }

# runs the optimizer to retrieve optimal yearly contributions and asset allocations before and
# after retirement and returns this information as well as metrics for each account
def getOptAllocsAndCont(data, numOptions):
    # package input data for before retirement run:
    preRetUserInfo = packUserInfo(data, int(data["current_age"]), int(data["retirement_age"]), float(data["total_current_income"]), float(data["current_annual_spending"]), float(data["current_amount_paying_in_taxes_annually"]))
    death_age = int(data["retirement_age"]) + int(data["expected_number_of_years_left_to_live_after_retirement"])
    retirement_salary = (float(data["expected_monthly_SS_check_amount_in_retirement"]) * 12) + (float(data["expected_monthly_pension_check_amount_in_retirement"]) * 12) + float(data["expected_part_time_job_annual_income_in_retirement"])
    #postRetUserInfo = packUserInfo(data, data["retirement_age"], death_age , retirement_salary, data["expected_annual_spending_in_retirement"], data["expected_amount_will_pay_in_taxes_annually_in_retirement"])
    subAccounts = [acnt["type"]  for acnt in data["accounts"]]
    # before retirement sub_account_inputs hold current balances inputted by user
    sub_account_inputs = dict()
    for acnt in data["accounts"]:
        sub_account_inputs.update({acnt["type"]: packAnnotAccountInfo(acnt["type"], float(acnt["current_balance_investment_accounts"]), acnt["usChoice"], acnt["intrnlChoice"], acnt["bondChoice"]) })

    combined_accounts_input_var = {
            "account_information":{
                "account_type": "combined",
                "subAccounts": subAccounts,
                "sub_account_inputs": sub_account_inputs
            },
            "user_information": preRetUserInfo
    }


    # combined_accounts_input_var_post = {
    #         "account_information":{
    #             "account_type": "combined",
    #             "subAccounts": subAccounts,
    #             "sub_account_inputs": sub_account_inputs
    #         },
    #         "user_information": postRetUserInfo
    # }
    # get optimal values

    #return runOptimizer(combined_accounts_input_var)
    #return combined_accounts_input_var
    firstMetricOpts = {
            "metric" : "total_growth_of_all_accounts",
            "normOpt": "noNorm",
            "angle": 1,
            "minVal": 0,
            "maxVal": 1
    }

    secondMetricOpts = {
        "metric" : "total_variance_proxy",
        "normOpt": "noNorm",
        "angle": 1,
        "minVal": 0,
        "maxVal": 1
    }
    # finding minY, maxY, minX and maxX
    secondMetricOpts["normOpt"] = "none"
    minFirstMetric = runOptimizer(combined_accounts_input_var, firstMetricOpts, secondMetricOpts, "min")
    minXVal = minFirstMetric["optOutput"][firstMetricOpts["metric"]]
    maxFirstMetric = runOptimizer(combined_accounts_input_var, firstMetricOpts, secondMetricOpts, "max")
    maxXVal = maxFirstMetric["optOutput"][firstMetricOpts["metric"]]

    secondMetricOpts["normOpt"] = "noNorm"
    firstMetricOpts["normOpt"] = "none"
    minSecondMetric = runOptimizer(combined_accounts_input_var, firstMetricOpts, secondMetricOpts, "min")
    minYVal = minSecondMetric["optOutput"][secondMetricOpts["metric"]]
    maxSecondMetric = runOptimizer(combined_accounts_input_var, firstMetricOpts, secondMetricOpts, "max")
    maxYVal = maxSecondMetric["optOutput"][secondMetricOpts["metric"]]

    # add in min and max values to construct parameters for generating points
    firstMetricOpts["normOpt"] = "max"
    firstMetricOpts["minVal"] = minXVal
    firstMetricOpts["maxVal"] = maxXVal
    secondMetricOpts["normOpt"] = "min"
    secondMetricOpts["minVal"] = minYVal
    secondMetricOpts["maxVal"] = maxYVal

    options = []
    # for i in range(numOptions):
    #     options.append("Option" + str(i+1))

    # referenced documentation at this link (https://www.w3schools.com/PYTHON/module_math.asp) for the math module methods used below:
    # math.pi, math.radians(), math.sin(), math.cos()
    optionCoords = set()
    optionVals = dict()
    for i in range(numOptions):
        print("iteration " + str(i) + "\n")
        angle = float(((i + 1) * ((math.pi/2) - math.radians(2)))/numOptions)
        opt = "Option" + str(i+1)
        options.append(opt)
        firstMetricOpts["angle"] = math.cos(angle)
        secondMetricOpts["angle"] = math.sin(angle)
        print("firstMetricOpts\n")
        print(firstMetricOpts)
        print("secondMetricOpts\n")
        print(secondMetricOpts)
        preRetMetrics = packOptimizerResults(data, combined_accounts_input_var, firstMetricOpts, secondMetricOpts, "max", subAccounts)
        maxY = preRetMetrics["total_balance_from_all_investments_plus_std_dev"]
        minY = preRetMetrics["total_balance_from_all_investments_minus_std_dev"]

        if (not((maxY, minY) in optionCoords)):
            optionCoords.add((maxY, minY))
            optionVals.update({
                            opt : {
                                "xcoord": preRetMetrics["total_expected_return"],
                                "maxY": maxY,
                                "minY": minY,
                                "ycoord": preRetMetrics["total_balance_from_all_investments_at_end_of_year_range"],
                                "rec": preRetMetrics

                            }
            })

    optionVals.update({"options": options})
    return optionVals

    # TODO: ** add first metric opts and second metric opts to packoptimizerResults
    # preRetMetrics = packOptimizerResults(data, combined_accounts_input_var, firstMetricOpts, secondMetricOpts, optSetting, subAccounts)
    #return preRetMetrics
    # package data for after retirement run:
    # for acntInfo in preRetMetrics["sub_account_outputs"]:
    #     newBal = acntInfo["total_account_balance_at_end_of_range"]
    #     (combined_accounts_input_var_post["account_information"]["sub_account_inputs"][acntInfo["account_type"]]["account_information"]).update({"current_balance_investment_account": newBal})

    #return combined_accounts_input_var_post
    #combined_accounts_input_var_post.update({"user_information": postRetUserInfo})

    # return {
    #     "combinedAccounts_input_var": combined_accounts_input_var,
    #     "combined_accounts_input_var_post": combined_accounts_input_var_post
    # }
    # get optimal values
    # need to specify post and preretmetrics
    #postRetMetrics = runOptimizer(combined_accounts_input_var_post)
    #packOptimizerResults(combined_accounts_input_var_post, subAccounts)
    # combine and produce the output

    # return {
    #         # "debug": {
    #         # "annotated_inputs": {
    #         #     "beforeRet": combined_accounts_input_var,
    #         #     "afterRet": combined_accounts_input_var_post
    #         # }
    #         # },
    #         # "Recommendation1_BeforeRet": preRetMetrics
    #
    #         # postRetMetrics
    #         #"Recommendation1_PostRetirement": postRetMetrics
    # }
    return preRetMetrics
