
import json
import string

def getPercentage(age):

    f = open("table_iii.json", "r")
    rmd = json.loads(f.read())

    if age>=120:
        d = rmd["120"]["distribution_period"]
        return (1/d)
    else:
        d = rmd[str(age)]["distribution_period"]
        return (1/d)
