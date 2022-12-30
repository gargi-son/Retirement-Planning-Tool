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
  
const backend_url = "sample_pareto_opt_output_updated.json";
//const backend_url = "https://cs787-proj-app.herokuapp.com/"

async function getapi(url) {
	myHeaders = new Headers();
	
    // Storing response
    const response = await fetch(url, {method: 'GET', headers: myHeaders, mode: 'cors'});
    
    // Storing data in form of JSON
    var data = await response.json();
    show(data);
}

getapi(backend_url);

function show(data) {
	console.log("i'm in SHOW of paretoOutput");
	console.log("data is...")
	console.log(data)

	personOKmsg1.innerHTML = data.personIsOk.msgToDisplay.firstLine;
	personOKmsg2.innerHTML = data.personIsOk.msgToDisplay.secondLine;
	personOKmsg3.innerHTML = data.personIsOk.msgToDisplay.thirdLine;
	personOKmsg4.innerHTML = data.personIsOk.msgToDisplay.fourthLine;

	rec1Possibility = data.rec1feasible;
	console.log(rec1Possibility);

	if (rec1Possibility == "true"){

	var paretoValues = data.Recommendation1_BeforeRet.values;

	const plotData = []; //['X', 'minY', 'Y', 'Y', 'maxY'];
	for (var i in paretoValues){
		if (i != "options"){
			plotData.push([paretoValues[i]["xcoord"], paretoValues[i]["minY"], paretoValues[i]["ycoord"], paretoValues[i]["ycoord"], paretoValues[i]["maxY"]]);
		}
	} //end of for-loop 

	//choose options message
	var candleStickMsg = data.Recommendation1_BeforeRet.msgToDisplay
	chooseMsg.innerHTML = candleStickMsg;

    //annuities message
	var Annutiesmsg0 = data.Recommendation2_AnnuityPrincipal.msgToDisplay;
	var Annutiesmsg = (Annutiesmsg0["firstLine"] +  " " + Annutiesmsg0["secondLine"] + " " + Annutiesmsg0["thirdLine"]);
	var AnnuitiesVal = parseFloat(data.Recommendation2_AnnuityPrincipal.values).toFixed(2);
	document.getElementById('pop').setAttribute('data-content', Annutiesmsg); //https://stackoverflow.com/questions/33217791/change-data-content-in-a-bootstrap-popover

	google.charts.load('current', { 'packages': ['corechart', 'table', 'gauge'] } );
    google.charts.setOnLoadCallback(drawChart);

	function drawChart() {
		var figure = google.visualization.arrayToDataTable(plotData, true);

		var options = {
		  legend:'none',
		  candlestick: {
			risingColor: {stroke: '#4CAF50'}, //green
      		fallingColor: {stroke: '#F44336'} //red
		  },
		  //colors: ['magenta'] for changing the color of the stick
		};
	
		var chart = new google.visualization.CandlestickChart(document.getElementById('chart_div'));
		chart.draw(figure, options);

		// Every time the table fires the "select" event, it should call your selectHandler() function.
		google.visualization.events.addListener(chart, 'select', selectHandler);

		function selectHandler(e) {
  			//alert('A chart point was selected');
			var userSelection = chart.getSelection(); //shows which option the user selected on the graph

			var optionSelected = ("Option" + ((userSelection[0].row) + 1));  //adding '1' beacuse the options are starting with 0
			console.log(optionSelected)
			
			targetOptionJSON = paretoValues[optionSelected] //JSON of selected option
			console.log(targetOptionJSON)

			/* Granular processing */
			var yearlyInvestmentContribution = 0;
			var costIncurred = 0;
			var subAccountNames = [];
			var graph_x_axis = [];
			var dataToplotArr = [];

			subAccounts = targetOptionJSON.rec.sub_account_outputs;
			allAccountsBal = targetOptionJSON.rec.total_balance_from_all_investments_at_end_of_year_range;

			//for line plotting:
			startAge = targetOptionJSON.rec.user_information.year_range_running_model_on.start_age;
			endAge = targetOptionJSON.rec.user_information.year_range_running_model_on.end_age;

			console.log(startAge)
			console.log(endAge)

			//for pie plotting:
			var bondChoice = 0;
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
			
			//xcoord for line chart
			for (var age = startAge;  age < endAge; age++){
				graph_x_axis.push(age);
			}

			document.querySelector("#yr-contrib").innerText = yearlyInvestmentContribution;
			document.querySelector("#cost-contrib").innerText = costIncurred;

			//Line Chart - https://stackoverflow.com/questions/71805869/chart-js-using-for-loop
			var colorList = ['orange', 'blue', 'brown', 'green', 'violet', 'black', 'red'];
			const ctx = document.getElementById('myChart').getContext('2d');
			const data0 = {
					labels: graph_x_axis,
					datasets: graph_x_axis.map((ds, i) => ({
						label: subAccountNames[i],
						data: dataToplotArr[i],
						borderColor: colorList[i],
						borderWidth: 1
					  })),
					options: {
						scales: {
						  y: {
							min: 0        
						  }
						}
					}
				};
			const config = {type: 'line', data: data0,};
			const myChart = new Chart(ctx, config);
					
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
			console.log(mergeRows) //computed for future use

            $('#showInput').toggle();
			$('#showOutput').toggle("slide"); //displays the pie and line charts
			$('#showHomePage').toggle();
		} // click event function
	}
} //rec1feaibility = true
else{
	$('#showInput').toggle();
	$('#rec1msgAnnuity').toggle();
	$('#rec2msgAnnuity').toggle();
	var Msg = data.Recommendation1_BeforeRet.msgToDisplay;
	console.log(Msg);
	rec1Msg.innerHTML = Msg;

	var Annutiesmsg0 = data.Recommendation2_AnnuityPrincipal.msgToDisplay;
	var Annutiesmsg = (Annutiesmsg0["firstLine"] +  " " + Annutiesmsg0["secondLine"] + " " + Annutiesmsg0["thirdLine"]);
	//var AnnuitiesVal = parseFloat(data.Recommendation2_AnnuityPrincipal.values).toFixed(2);
	document.getElementById('popAnnuity').setAttribute('data-content', Annutiesmsg); //https://stackoverflow.com/questions/33217791/change-data-content-in-a-bootstrap-popover
}
} //end of show function