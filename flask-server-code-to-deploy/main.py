from flask import Flask, jsonify, request

#from flask_restful import Resource, Api
from flask_cors import CORS
from packingFunctions import *
from modelcode import *
import dgalPy as dgal
from personWillBeOkCode import *
# import json
# import copy
#from modelcode import *

 # create new flask app
app = Flask(__name__)

#api = Api(app)
CORS(app)

# route below for testing optimizers
# downloaded couenne by following the instructions at this link: https://notebook.community/jdhp-docs/python_notebooks/nb_dev_python/python_pyomo_getting_started_0_installation_instructions_pyomo_and_solvers
@app.route("/", methods=["GET", "POST"])
def initialAccess():
    if (request.method == "GET"):
        # return jsonify({"data": "hello"})
        # return jsonify({"data": "hello"})

        # dgal.startDebug()
        # f = open("exampleSCinput.json", "r")
        # input = json.loads(f.read())
        f = open("combined_accounts_model_input_var.json","r")
        varInput = json.loads(f.read())

        def constraints(o):
            return (dgal.all([ o["constraints"]]))

        optAnswer = dgal.max({
            "model": combiningAccountsMod,
            "input": varInput,
            # total_expected_return
            #"total_growth_of_all_accounts"
            #"total_variance_proxy"
            "obj": lambda o: o["total_growth_of_all_accounts"],
            "constraints": constraints,
            "options": {"problemType": "mip", "solver": "glpk","debug": True}
        })
        optOutput = combiningAccountsMod(optAnswer["solution"])
        # dgal.debug("optOutput",optOutput)
        # dgal.debug("constraints", optOutput["constraints"])

        output = {
        #    "input":input,
        #    "varInput":varInput,
            "optAnswer": optAnswer,
            "optOutput": optOutput
        }
        return jsonify(output)
    elif (request.method == "POST"):
        #print(request)
        data = request.get_json()
        # optimalOutputOption1 = getOptAllocsAndCont(data)

        print(data)
        # data is a dict type
        print(type(data))
        output = {
                "responseFromServer": "server response1",
                "secondField": 2
        }
        return jsonify(output)
        # print(request.get_json())
        # print(1)
        # return "got form"

# Use the below route for debugging
@app.route("/testSystemInput", methods=["POST"])
def testInputs():
    if (request.method == "POST"):
        data = request.get_json()
        return jsonify(data)

@app.route("/getrecs", methods=["GET", "POST"])
def getRecommendations():
    #data = request.get_json()

    # Note for Testing to Shravani:
    # when input matches system_input_ex.json structure
    # uncomment line below and comment the code:

    #IMPORTANT: comment out below lines change to get_json() when testing input
    f = open("system_input_ex.json", "r")
    #f = open("system_input_ex_2_person_RMD_ok.json","r")
    #f = open("system_input_ex_3_HSA_cont.json","r")
    #f = open("system_input_ex_4_Brokerages.json", "r")
    #f = open("system_input_ex_5_personNotOkAfterRet.json", "r")
    #f = open("system_input_ex_6_EnoughForAnnuity.json", "r")
    #f = open("system_input_ex_7_DeductsSurplusInRightOrder.json", "r")
    #f = open("system_input_ex_8_test_tickers.json", "r")
    data = json.loads(f.read())
    #data = request.get_json()
    #return jsonify(getOptAllocsAndCont(data))
    #f = open("system_input_ex.json","r")
    #data = json.loads(f.read())
    # fix bug with postRet optimization:
    # need to have user send a separate request because the optimizer is expensive
    # server cannot handle calling it twice in one request


    #formula to calculate annuity principal from: https://www.annuity.org/annuities/immediate/annuity-calculator/

    personIsOk = {"personisOk" : "resultTrueOrFalse", "yearMoneyLastsUpTo": "y", "moneyLeftAtEndOfYear": "remaining_money", "amountInRetirement": "current_investment_account_balance"}
    # person is ok: fixed for multiple accounts
    personIsOk = personWillBeOk(data)
    # make call to optimizer only if person ok for now and may or may not be ok thru retirement
    # if (personIsOk["personisOk"] == True or (personIsOk["personisOk"] == False and personIsOk["retiredcheck"] == False)):

    # else:
    if (float(data["total_current_income"]) >= (float(data["current_annual_spending"]) + float(data["current_amount_paying_in_taxes_annually"]))):
        #optContrbtnAndAllocations = getOptAllocsAndCont(data)
        optContrbtnAndAllocations = {
           "Recommendation1_BeforeRet": {
                "msgToDisplay": "Please choose the option you are comfortable with.",
                "values": getOptAllocsAndCont(data, 3)

           }
        }
        rec1feasible = True
    else:
        optContrbtnAndAllocations = {
                                "Recommendation1_BeforeRet": {
                                 "msgToDisplay": "Please adjust your current annual spending and contributions to retirement accounts to be less than your current income after taxes",
                                 "values": "No run of Optimizer(none)"
                                 }
        }
        rec1feasible = False
    #optContrbtnAndAllocations = {"rec1": "willCall"}
    annuityPrincipal = getPrincipal(data)
    annuitymsg1 = "Cost to you to purchase an annuity which covers your expected retirement spending is "
    annuitymsg1 += str(annuityPrincipal)
    annuitymsg2 = "Amount in retirement accounts (excluding HSA) by retirement (with inputted info): " + str(personIsOk["balanceForAnnuityCheck"])
    if (personIsOk["personisOk"] == True and personIsOk["balanceForAnnuityCheck"] >= annuityPrincipal):
        annuitymsg3 = "You can buy an annuity"
    else:
        annuitymsg3 = "Expected balance in retirement accounts cannot cover annuity purchase. Please follow Recommendation 1\n"

    personisOkMsg1 = ""
    if (personIsOk["personisOk"] == True):
        if (rec1feasible == True):
            personisOkMsg1 = "Great Job! You are on track for retirement. We suggest the following recommendations below your stats. "
        else:
            personisOkMsg1 = "You will make it. But please implement recommendation 1. "
    else:
        personisOkMsg1 = "Sorry. Your savings won't last through retirement. "
    personisOkMsg1 += "Here are your stats:"

    personisOkMsg2 = "Your savings will last up to age : " + str(personIsOk["yearZMoneyLastsUpTo"])
    personisOkMsg3 = "Your surplus after expenses through age " + str(personIsOk["yearZMoneyLastsUpTo"]) + " are: " + str(personIsOk["moneyLeftAfterExpensesByYearZ"])
    personisOkMsg4 = "The total amount in all inputted retirement accounts by age " + str(personIsOk["yearZMoneyLastsUpTo"]) + " will be: " + str(personIsOk["amountInAllRetAccountsAtEndOfSimltn"])

    # annuity code: have in separate api route
    structure_recs = {
        "rec1feasible": rec1feasible,
        "personIsOk": {
                        "msgToDisplay": {
                        "firstLine": personisOkMsg1,
                        "secondLine": personisOkMsg2,
                        "thirdLine": personisOkMsg3,
                        "fourthLine": personisOkMsg4
                        },
                        "values": personIsOk
        },
        "Recommendation2_AnnuityPrincipal": {
                    "msgToDisplay": {
                        "firstLine": annuitymsg1,
                        "secondLine": annuitymsg2,
                        "thirdLine": annuitymsg3
                    },
                    "values": annuityPrincipal
        }
    }
    recs = dgal.merge([structure_recs, optContrbtnAndAllocations])

    # rebalancing
    return jsonify(recs)
    #return jsonify(optContrbtnAndAllocations)

#api.add_resource(getAllocsAndContrib, "/")


if __name__ == '__main__':
    app.run(debug=True)
