Our Submission includes: 

1. "Final Report.pdf" : contains our report 

2. "CS 787 - Group Project Presentation.pdf" : contains our presentation (presented on 11/16/2022) 

3. "CS 787 Project Citations.pdf" : lists a description of sources we referenced throughout our project 

4. "Final Project Demo-HD1080p.mov": demonstrates use of our application (run locally ) with two different use cases 

5. "flask-server-code-to-deploy-updated.zip": contains our codebase (relevant individual files are listed below): 
- main.py: includes our server code 
- packingFunctions.py: includes code to run optimizer, calculate annuity investment amount, generate a pareto optimal front, and package system/model input and output
- modelcode.py: includes implementations of our 2 models (used to generate optimal asset allocations and contribution amounts): singleAccountMod() and combiningAccountsMod() 
- personWillBeOKCode.py: includes our diagnosis code implementation 
- our frontend code files: index.html, script.js, .png/.img files, and .css files 

Our application (JS,HTML, CSS files) is currently deployed at the following link (on AWS EC2): 

http://18.212.70.29/

(Please note: Some use cases will cause server errors since our funds inception dates 
may be less than the years to retirement) 

Our back end code is deployed on Heroku at: https://cs787-proj-app.herokuapp.com/ 
It includes the following routes (which our GUI invokes with user input via fetch calls in script.js to get resulting recommendations and diagnosis from our backend code files):
 
https://cs787-proj-app.herokuapp.com/getInitRecs : returns the initial recommendations (our diagnosis code results, annuity investment Recommendation 2 result, and whether our Recommendation 1 is feasible) 

https://cs787-proj-app.herokuapp.com/getOptimizedMetric : returns the optimal value (min or max) when our model is run with objective function being the X or Y metric (proxies we define in our backend)

https://cs787-proj-app.herokuapp.com/getOneRec1Option : returns one option (point) of optimal allocation and contribution amounts to graph in the pareto optimal range 

Change: in this version of our submission, we include a file 
called "deployed-app-gui-updated.zip". This file contains our front end 
code which accesses our backend APIs deployed on Heroku

To locally run our application (to see any results from the backend and frontend execution): 
please follow the steps below: 
1. unzip flask-server-code-to-deploy-updated.zip 
2. cd to flask-server-code-to-deploy in terminal 
3. run python main.py 
4. in script.js lines 345,353, and 411: change the endpoint (before /getInitRecs, /getOptimizedMetric, /getOneRec1Option) in fetch call parameter from "https://cs787-proj-app.herokuapp.com/" to "http://127.0.0.1:5000"
5. open index.html in the browser and enter information into the form
6. results from backend and frontend execution are printed in the terminal and Chrome Browser's console 
(respectively)


