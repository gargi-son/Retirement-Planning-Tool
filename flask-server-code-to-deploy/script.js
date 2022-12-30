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
  <select class="form-select" name="field5_option" required>
    <option value="Trad IRA">Trad IRA</option>
    <option value="Roth IRA">Roth IRA</option>
    <option value="Trad 401k">Trad 401k</option>
    <option value="Roth 401k">Roth 401k</option>
    <option value="HSA">HSA</option>
    <option value="Brokerages">Brokerages</option>
  </select>
    </div>
  
  <label for="field5" class="col-sm-2 mt-3 col-form-label">What would be your total yearly investment contribution?</label>
  <div class="col-sm-9 mt-3">
  <input type="number" name="total_yearly_investment_contribution" onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
  min="0" class="form-control" required/>
  </div>
  <label for="field5" class="col-sm-2 mt-3 col-form-label">What is your current balance in your investment account?</label>
  <div class="col-sm-9 mt-3">
  <input type="number" name="current_balance_investment_accounts" onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
  min="0" class="form-control" required/>
  </div>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">What would be the rate of return of your investment?</label>
  <div class="col-sm-9 mt-3">
  <input type="number" name="rate_of_return_all_investments" onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
  min="0" class="form-control" required/>
  </div>
  <button class="col-sm-1 remove btn btn-outline-danger">X</button>
  <h2 class="h6 mt-3 mb-4"><u><em>Please select your ETF and mutual funds:</em></u></h2>	

  <label for="field5" class="col-sm-2 mt-3 col-form-label">US Stocks
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="usChoice" id="usChoice" required>
      <option value="VOO">VOO</option>
      <option value="VTI">VTI</option>
      <option value="DFAC">DFAC</option>
      <option value="IVV">IVV</option>
      <option value="VUG">VUG</option>
      <option value="SPY">SPY</option>
      <option value="QQQ">QQQ</option>
      <option value="VTV">VTV</option>
    </select>
    <span class="error">This data is required</span>
  </div>

  <label for="field5" class="col-sm-2 mt-3 col-form-label">International Stocks
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="intrnlChoice" id="intrnlChoice" required>
      <option value="VXUS">VXUS</option>
      <option value="SPDW">SPDW</option>
      <option value="VWO">VWO</option>
      <option value="IXUS">IXUS</option>
    </select>
    <span class="error">This data is required</span>
  </div>
  <label for="field5" class="col-sm-2 mt-3 col-form-label">Bonds
  </label>
  <div class="col-sm-9 mt-3 form-field-inside">
    <select class="form-select" name="bondChoice" id="bondChoice" required>
      <option value="BND">BND</option>
      <option value="AGG">AGG</option>
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


form.addEventListener("submit", function (e) {
  e.preventDefault();

  /*var fields = document.querySelectorAll("input[type=text]");
  console.log(fields)
  var fieldsArray = Array.from(fields);*/

  var age_error = document.querySelectorAll(".age_error");
  var retire_age_error = document.querySelectorAll(".retire_age_error");

  var current_age = document.getElementById('field2').value;
  var current_age_prop = document.getElementById('field2');
  var retire_age_prop = document.getElementById('field6');
  console.log("current_age",current_age);
  var retirement_age = document.getElementById('field6').value;
  console.log("retirement_age",retirement_age);
  var age_flag=1;
  var retire_age_flag=1;


  if(current_age_prop && current_age_prop.value){
    if(current_age>0){
      if(current_age < retirement_age){
        age_flag=0;
        age_error[0].style.display="none";
        console.log("no age error");
      }
      else{
        age_flag=1;
        age_error[0].style.display="block";
        console.log("age error");
      }
    }
    else{
      age_flag=1;
      age_error[0].style.display="block";
      console.log("age error");
    }
  }
  

   if(retire_age_prop && retire_age_prop.value){
    console.log("ret")
    if(retirement_age>0){
      if(current_age < retirement_age){
        retire_age_flag=0;
        retire_age_error[0].style.display="none";
        console.log("no age error");
      }
      else{
        retire_age_flag=1;
        retire_age_error[0].style.display="block";
        console.log("age error");
      }
    }
    else{
      retire_age_flag=1;
      retire_age_error[0].style.display="block";
      console.log("age error");
    }
  }


  var current_spending=document.getElementById('field3').value;
  var current_income=document.getElementById('field1').value;
  var taxes_payment=document.getElementById('field4').value;
  var spent_constraint_flag=1;
  spent_error=document.querySelectorAll(".spent_error");

  var sum=current_spending+taxes_payment;
  if(current_income>sum){
    spent_constraint_flag=0;
    spent_error[0].style.display="none";
  }
  else{
    spent_constraint_flag=1;
    spent_error[0].style.display="block";
  }



  /*var filteredArray = fieldsArray.filter(function (field) {
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
  }*/
  //   if all fields are filled, send data to API
  //if (errorCount === 0 && age_flag===0 && retire_age_flag===0) {
  if (age_flag===0 && retire_age_flag===0 && spent_constraint_flag===0) {
    sendData();
  }
});
// send data to API
function sendData() {
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
  // send data to API
   // source used to construct GET and POST requests according to fetch() function syntax: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
  fetch("http://127.0.0.1:5000/getrecs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    
    mode:'cors',
    body: JSON.stringify(obj)
  })
    .then((response) => response.json())
    .then(function(response){
      if (response.status === 200) {
        location.href = "output.html";
        getData();
      }
    })
    .then((data) => {
      console.log("Success:", data);
    });

}


function getData(){

myHeaders = new Headers();

fetch('https://cs787-proj-app.herokuapp.com/',{
  method: 'GET',headers: myHeaders,mode: 'cors'
})
  .then((response) => response.json())
  .then((data) => console.log(data));
}
