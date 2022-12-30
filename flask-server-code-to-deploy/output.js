$(function () {
  $('[data-toggle="popover"]').popover()
})

$(document).ready(function(){
  $("#modalButton1").click(function(){
    $("#Modal1").modal();
  });
});

$(document).ready(function(){
  $("#modalButton2").click(function(){
    $("#Modal2").modal();
  });
});

const backend_url = "system_output_updated.json";
//const backend_url = "https://cs787-proj-app.herokuapp.com/"

async function getapi(url) {
	myHeaders = new Headers();
	
    // Storing response
    const response = await fetch(url, {method: 'GET', headers: myHeaders, mode: 'cors'});
	//const response = await fetch(url);
    
    // Storing data in form of JSONg7f
    var data = await response.json();
    show(data);
}

getapi(backend_url);

function show(data) {
	console.log("i'm in SHOW");
	console.log("data is...")
	console.log(data)
	var yearlyInvestmentContribution = 0;
	var costIncurred = 0;
	var subAccountNames = [];
	var graph_x_axis = [];
	var dataToplotArr = [];
	
	subAccounts = data.Recommendation1_BeforeRet.sub_account_outputs;
	allAccountsBal = data.Recommendation1_BeforeRet.total_balance_from_all_investments_at_end_of_year_range;
	
	//for line plotting:
	startAge = data.Recommendation1_BeforeRet.user_information.year_range_running_model_on.start_age;
	endAge = data.Recommendation1_BeforeRet.user_information.year_range_running_model_on.end_age;
	
	//for pie plotting:
	var bondChoice= 0;
	var intrnlChoice = 0;
	var usChoice = 0;
	const accTable = [];
	
	for (const acc of subAccounts){
		yearlyInvestmentContribution += acc.total_yearly_investment_contributions_to_account;
		costIncurred += acc.total_cost_incurred_on_account_by_end_of_range;
		
		//for line plotting
		subAccountNames.push(acc.account_type);
		dataToplotArr.push(acc.total_account_balance_each_year);

		//for pie plotting
		var accType = acc.account_type
		var totaccBal = acc.total_account_balance_at_end_of_range
		for (var i in acc["account_asset_info"])
		{
			var ticker = acc["account_asset_info"][i]["ticker"]
			var contriPer = acc["account_asset_info"][i]["weight"]
			
			var indiAccWgt = contriPer * totaccBal;

			if (i == "bondChoice"){
				var bondChoice = bondChoice + (indiAccWgt/allAccountsBal);
				accTable.push({"AccCategory": i, "Ticker": ticker, "Account": accType, "Individual": (indiAccWgt/allAccountsBal)*100});
			} else if (i == "intrnlChoice"){
				var intrnlChoice = intrnlChoice + (indiAccWgt/allAccountsBal);
				accTable.push({"AccCategory": i, "Ticker": ticker, "Account": accType, "Individual": (indiAccWgt/allAccountsBal)*100});
			} else if (i == "usChoice"){
				var usChoice = usChoice + (indiAccWgt/allAccountsBal);
				accTable.push({"AccCategory": i, "Ticker": ticker, "Account": accType, "Individual": (indiAccWgt/allAccountsBal)*100});
			} else {}
		}
	} //end of for loop
	
	//finalized data for individual contribution
	console.log("Individual Contribution");
	console.log(accTable);

	//finalized data for pie chart
	console.log("Combined Contribution");
	console.log("Bonds");
	console.log(bondChoice*100);
	console.log("International");
	console.log(intrnlChoice*100);
	console.log("US");
	console.log(usChoice*100);

	yearlyInvestmentContribution = Number(yearlyInvestmentContribution.toFixed(2));
	costIncurred =  Number(costIncurred.toFixed(2));
	
	for (var age = startAge;  age < endAge; age++){
		graph_x_axis.push(age);
	}
	
	document.querySelector("#yr-contrib").innerText = yearlyInvestmentContribution;
	document.querySelector("#cost-contrib").innerText = costIncurred;

	//Line Chart
	const ctx = document.getElementById('myChart').getContext('2d');
	const data0 = {
			labels: graph_x_axis,
			datasets: [{ 
					data: dataToplotArr[0],
					label: subAccountNames[0],
					borderColor: "rgb(62,149,205)",
					backgroundColor: "rgb(62,149,205,0.1)",
				}, { 
					data: dataToplotArr[1],
					label: subAccountNames[1],
					borderColor: "rgb(60,186,159)",
					backgroundColor: "rgb(60,186,159,0.1)",
				}],
			options: {
				scales: {
				yAxes: [{
					id: subAccountNames[0],
					type: 'linear',
					position: 'left',
				}, {
					id: subAccountNames[1],
					type: 'linear',
					position: 'right',
					ticks: {
					max: 1,
					min: 0
					}
				}]
				}
			}
		};
	const config = {type: 'line', data: data0,};
	const myChart = new Chart(ctx, config);
	//end of line chart

	//Pie Chart
	const ctx1 = document.getElementById('myPieChart').getContext('2d');
	const data1 = {
				labels: ["Bonds", "US Stocks", "International Stocks"],
				datasets: [{
					label: 'Asset Allocation',
					data: [(bondChoice*100), (usChoice*100), (intrnlChoice*100)],
					backgroundColor: ['rgb(255, 99, 132)','rgb(54, 162, 235)','rgb(255, 205, 86)'],
					hoverOffset: 4
				}]
			};
	const config1 = {type: 'pie', data: data1,};
	const myPieChart = new Chart(ctx1, config1);
	//end of pie chart

	//data collection for individual contributions
	var displayData1 = [];
	var displayData2 = [];
	var displayData3 = [];
	var individualContributions = [];
	for (var i in accTable) {
		if ( (accTable[i]["AccCategory"]) == "bondChoice") {
			displayData1.push({"Account": accTable[i]["Account"], "Contribution": accTable[i]["Individual"]})
		}
		if ( (accTable[i]["AccCategory"]) == "usChoice") {
			displayData2.push({"Account": accTable[i]["Account"], "Contribution": accTable[i]["Individual"]})
		}
		if ( (accTable[i]["AccCategory"]) == "intrnlChoice") {
			displayData3.push({"Account": accTable[i]["Account"], "Contribution": accTable[i]["Individual"]})
		}	
	}
	individualContributions.push({"Bonds":displayData1, "US Stocks":displayData2, "International Stocks":displayData3});
	//console.log(individualContributions);

	//table for individual contributions
	let placeholder = document.querySelector("#indiOutput");
	let out = "";
	for (var x in individualContributions[0]){
		//console.log(x);
		for (var y in individualContributions[0][x]){
			var mergeRows = Object.keys(individualContributions[0][x]).length;
			out += `
			<tr>
				<td>${x}</td>
				<td>${individualContributions[0][x][y]["Account"]}</td>
				<td>${individualContributions[0][x][y]["Contribution"]}</td>
			</tr>
		`;
		}
	}
	//document.querySelector("#merge").setAttribute("colspan", 2);
	placeholder.innerHTML = out;
	console.log(mergeRows)
} //end of show function