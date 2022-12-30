var turn_on = document.getElementById("turn_on");
var box = document.querySelector(".box");
var field5 = document.getElementById("field5_option");
var add = document.getElementById("add");
var form = document.getElementById("form");
var count = 0;
var options = field5.options;
var optionsLength = Array.from(options).length - 1;
console.log(optionsLength);

turn_on.addEventListener("click", function () {
  box.style.display = "block";
});

field5.addEventListener("change", function () {
  selectedValue = field5.value;
  console.log(optionsLength);
  if (selectedValue === "all" || count === optionsLength) {
    add.style.display = "none";
  } else {
    add.style.display = "block";
  }
});

add.addEventListener("click", function () {
  var newField = `<h6><u><em>Other Account</h6></em></u><br><label for="option" class="col-sm-2">Option</label>
    <div class="col-sm-10">
  <select class="form-select" name="field5_option">
    <option value="Trad IRA">Trad IRA</option>
    <option value="Roth IRA">Roth IRA</option>
    <option value="Trad 401k">Trad 401k</option>
    <option value="Roth 401k">Roth 401k</option>
    <option value="HSA">HSA</option>
    <option value="Brokerages">Brokerages</option>
    <option value="Option 7">Option 7</option>
  </select>
    </div>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">What would be your total yearly investment contribution?</label>
  <div class="col-sm-9 mt-3">
  <input type="text" name="total_yearly_investment_contribution" class="form-control" />
  </div>
  <label for="field5" class="col-sm-2 mt-3 col-form-label">What is your current balance in your investment account?</label>
  <div class="col-sm-9 mt-3">
  <input type="text" name="current_balance_investment_accounts" class="form-control" />
  </div>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">What would be the rate of return of your investment?</label>
  <div class="col-sm-9 mt-3">
  <input type="text" name="rate_of_return_all_investments" class="form-control" />
  </div>
  <button class="col-sm-1 remove btn btn-outline-danger">X</button>
  <h2 class="h6 mt-3 mb-4"><u><em>Please select your ETF and mutual funds:</em></u></h2>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">US Stocks
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="usChoice" id="usChoice">
      <option value="VOO">VOO</option>
      <option value="2">y</option>
      <option value="3">z</option>
      <option value="4">a</option>
      <option value="5">b</option>
    </select>
    <span class="error">This data is required</span>
  </div>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">International Stocks
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="intrnlChoice" id="intrnlChoice">
      <option value="VXUS">VXUS</option>
      <option value="2">y1</option>
      <option value="3">z1</option>
      <option value="4">a1</option>
      <option value="5">b1</option>
    </select>
    <span class="error">This data is required</span>
  </div>
  <label for="field5" class="col-sm-2 mt-3 col-form-label">Bonds
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="bondChoice" id="bondChoice">
      <option value="BND">BND</option>
      <option value="2">y2</option>
      <option value="3">z2</option>
      <option value="4">a2</option>
      <option value="5">b2</option>
    </select>
    <span class="error">This data is required</span>
  </div>`;
  var newDiv = document.createElement("div");
  newDiv.classList.add("row");
  newDiv.classList.add("mt-4");
  newDiv.innerHTML = newField;
  field5.parentElement.parentElement.appendChild(newDiv);
  count++;
  if (count == optionsLength) {
    add.style.display = "none";
  }
});

document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("remove")) {
    e.target.parentElement.remove();
    count--;
    if (count < optionsLength) {
      add.style.display = "block";
    }
  }
});

form.addEventListener("submit", async function (e) {
  e.preventDefault();

  var fields = document.querySelectorAll("input[type=text]");
  var fieldsArray = Array.from(fields);

  var filteredArray = fieldsArray.filter(function (field) {
    return field.id !== "field14" && field.id !== "field15" && field.id!=="field16" && field.id!=="field17";
  });

  var error = document.querySelectorAll(".error");
  var errorCount = 0;
  for (var i = 0; i < filteredArray.length; i++) {
    if (filteredArray[i].value === "") {
      error[i].style.display = "block";
      errorCount++;
    } else {
      if (error[i]) {
        error[i].style.display = "none";
      }
    }
  }
  var sysOutput = {};
  //   if all fields are filled, send data to API
  if (errorCount === 0) {
    sysOutput = await sendData();
  }
  console.log("in submit listener function got sysOutput", sysOutput);
  // if globalerror == 0:  (no error occurred)
  // hide Shravani's form (div)
  // 
});
// send data to API
// Saarika's notes:
// async added to make sendData() asynchronous and call async function for fetch() call
// (according to syntax in link1 and link2 below)
async function sendData() {
  // source used to access form elements using .name from html form: https://javascript.info/form-elements
  var form = document.getElementById("form");
  var data = new FormData(form);
  var obj = {};
  for (var [key, value] of data.entries()) {
    obj[key] = value;
  }
  delete obj.field5_option;
  delete obj.total_yearly_investment_contribution;
  delete obj.current_balance_investment_accounts;
  delete obj.rate_of_return_all_investments;
  delete obj.usChoice;
  delete obj.intrnlChoice;
  delete obj.bondChoice;

  var total_yearly_investment_contribution = document.querySelectorAll("input[name=total_yearly_investment_contribution]");
  var field5_sub1Array = Array.from(total_yearly_investment_contribution);
  var current_balance_investment_accounts = document.querySelectorAll("input[name=current_balance_investment_accounts]");
  var field5_sub2Array = Array.from(current_balance_investment_accounts);
  var rate_of_return_all_investments = document.querySelectorAll("input[name=rate_of_return_all_investments]");
  var field5_sub3Array = Array.from(rate_of_return_all_investments);

  var field5_option = document.querySelectorAll("select[name=field5_option]");
  var field5_optionArray = Array.from(field5_option);

  var usChoice = document.querySelectorAll("select[name=usChoice]");
  var field5_sub4Array = Array.from(usChoice);

  var intrnlChoice = document.querySelectorAll("select[name=intrnlChoice]");
  var field5_sub5Array = Array.from(intrnlChoice);

  var bondChoice = document.querySelectorAll("select[name=bondChoice]");
  var field5_sub6Array = Array.from(bondChoice);

  var field5Array = [];
  for (var i = 0; i < field5_optionArray.length; i++) {
    var field5Obj = {};
    field5Obj["type"] = field5_optionArray[i].value;
    field5Obj["total_yearly_investment_contribution"] = field5_sub1Array[i].value;
    field5Obj["current_balance_investment_accounts"] = field5_sub2Array[i].value;
    field5Obj["rate_of_return_all_investments"] = field5_sub3Array[i].value;

    field5Obj["usChoice"] = field5_sub4Array[i].value;
    field5Obj["intrnlChoice"] = field5_sub5Array[i].value;
    field5Obj["bondChoice"] = field5_sub6Array[i].value;

    field5Array.push(field5Obj);
  }
  obj["accounts"] = field5Array;

  console.log(obj);
/// Starting Saarika's changes here:
  var systemOutput = {};
  errormsg = "Error: Can't get initial recommendations from server."
  // // send data to API

  // Note: applied information from the links below:
  //  Link1: https://stackoverflow.com/questions/41775517/waiting-for-the-fetch-to-complete-and-then-execute-the-next-instruction
  //  Link2: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function
  // mainly Link1  describes via an answer's example that returning a call to fetch() (with a .then(return json data)) returns the json data from the fetch call
  // and both Link1 and Link2 described that async and await keywords can be used to stall execution until the fetch() call returns data
  systemOutput = await fetchDataFromServer("http://127.0.0.1:5000/getInitRecs", obj, systemOutput, errormsg);
  //  // source used to construct GET and POST requests according to fetch() function syntax: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
  //  // https://cs787-proj-app.herokuapp.com/
  //  // http://127.0.0.1:5000/
  //  //"https://cs787-proj-app.herokuapp.com/getrecs"
  // fetch("http://127.0.0.1:5000/getrecs", {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json"
  //   },
  //
  //   mode:'cors',
  //   body: JSON.stringify(obj)
  // })
  //   .then((response) => response.json())
  //   .then((initData) => {
  //     console.log(initData.Recommendation1_BeforeRet)
  //     systemOutput = initData
  //     console.log("Success:", initData);
  //   })
  //   .catch((error) => {
  //     alert("An error occurred with getting initial recommendations from server. Please check console for details")
  //   console.error('Error:', error);
  // });
  console.log("SystemOutput:", systemOutput);
  if ((systemOutput !== {})) {
    if (systemOutput.rec1feasible === true) {
    // call /getOptimizedMetric to get minY, maxY, minX, maxX (4 times call)
    var urlOptXY = "http://127.0.0.1:5000/getOptimizedMetric"
    var optInput = {};
    optInput["sysInput"] = obj;
    var axes = ["X", "Y"]
    var minmaxArr = ["min", "max"]
    var optXandYs = {};
    var val = null;
    var containsNull = false;
    var errormsg = "Error: cannot get values for "
    for (var i = 0; i < axes.length; i++) {
      for (var j = 0; j < minmaxArr.length; j++) {
        strBoth = minmaxArr[j] + axes[i]
        errormsg += strBoth + " "
        optInput["orderMetric"] = axes[i]
        optInput["minOrMaxStr"] = minmaxArr[j]
        val = await fetchDataFromServer(urlOptXY, optInput, val, errormsg)
        if (val === null) {
          containsNull = true;
        }
        optXandYs[strBoth] = val
        console.log("got " + strBoth + ":", val)
        val = null
      }
    }
    if (containsNull === false) {
      // get the values for rec1 options:

      // extract min and max values for axes
      minXval = optXandYs["minX"]
      maxXval = optXandYs["maxX"]
      minYval = optXandYs["minY"]
      maxYval = optXandYs["maxY"]
      console.log("minXval: ", minXval)
      console.log("maxXval: ", maxXval)
      console.log("minYval: ", minYval)
      console.log("maxYval: ", maxYval)

      // get 3 points (calling api 3 times):
      var rec1Input = {};
      rec1Input["sysInput"] = obj
      var rec1OutputParams = {};
      rec1OutputParams["optionCoords"] = [];
      var optionVals = {};
      optionVals["options"] = [];
      rec1OutputParams["optionVals"] = optionVals;
      rec1Input["rec1OutputParams"] = rec1OutputParams;
      rec1Input["minXVal"] = minXval;
      rec1Input["maxXVal"] = maxXval;
      rec1Input["minYVal"] = minYval;
      rec1Input["maxYVal"] = maxYval;

      var numPoints = 3
      var urlRec1Point = "http://127.0.0.1:5000/getOneRec1Option"
      var errormsg3 = "Error: cannot get points:  "
      for (var i = 0; i < numPoints; i++) {
        rec1Input["nextPoint"] = i + 1
        // reference link : https://www.w3schools.com/jsref/jsref_string.asp
        // to get syntax to convert integer to a string via String() method and use this method below
        errormsg3 += "\n"  + String(i + 1) +  " of " + String(numPoints) + " points\n"
        rec1Input["totalNumPoints"] = numPoints
        rec1Input["rec1OutputParams"] = await fetchDataFromServer(urlRec1Point, rec1Input, rec1OutputParams, errormsg3)
      }
      // todo: check if error occurred
      systemOutput.Recommendation1_BeforeRet.values = rec1Input["rec1OutputParams"]["optionVals"]

    }
    else {
      console.log("error with getting min and max vals for axes")
    }
  }
  else {
    console.log("after checking rec1feasible = false, returning systemoutput")
  }
}
else {
  console.log("after checking initial api, cannot reach server")
}

// NEEd: send this systemOutput to Shilpa's output.html
console.log("systemoutput after rec1check:", systemOutput)
return systemOutput;
// calls: hides index.html form, runs output.js function (add Shilpa's logic here in the function)
}

async function fetchDataFromServer(url, postBody, outputVar, errormsg) {
  // send data to API
   // source used to construct GET and POST requests according to fetch() function syntax: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
   // https://cs787-proj-app.herokuapp.com/
   // http://127.0.0.1:5000/
   //"https://cs787-proj-app.herokuapp.com/getrecs"
  return await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },

    mode:'cors',
    body: JSON.stringify(postBody)
  })
    .then((response) => response.json())
    .then((initData) => {
      //console.log(initData.Recommendation1_BeforeRet)
      //location.href = "https://www.google.com/";
      outputVar = initData
      // console.log("Success:", initData);
      return outputVar
    })
    .catch((error) => {
      errormsg += "Please check console for details"
      alert(errormsg)
    console.error('Error:', error);
  });
  //return outputVar;

}
// Saarika's changes end here

function getData(){

myHeaders = new Headers();

fetch('https://cs787-proj-app.herokuapp.com/',{
  method: 'GET',headers: myHeaders,mode: 'cors'
})
  .then((response) => response.json())
  .then((data) => console.log(data));
}
