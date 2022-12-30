$(function () {
	$('[data-toggle="popover"]').popover()
})

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

	personOKmsg1.innerHTML = data.personIsOk.msgToDisplay.firstLine;
	personOKmsg2.innerHTML = data.personIsOk.msgToDisplay.secondLine;
	personOKmsg3.innerHTML = data.personIsOk.msgToDisplay.thirdLine;
	personOKmsg4.innerHTML = data.personIsOk.msgToDisplay.fourthLine;

	var Msg = data.Recommendation1_BeforeRet.msgToDisplay;
	console.log(Msg);
	rec1Msg.innerHTML = Msg;

	var Annutiesmsg0 = data.Recommendation2_AnnuityPrincipal.msgToDisplay;
	var Annutiesmsg = (Annutiesmsg0["firstLine"] +  " " + Annutiesmsg0["secondLine"] + " " + Annutiesmsg0["thirdLine"]);
	//var AnnuitiesVal = parseFloat(data.Recommendation2_AnnuityPrincipal.values).toFixed(2);
	document.getElementById('pop').setAttribute('data-content', Annutiesmsg); //https://stackoverflow.com/questions/33217791/change-data-content-in-a-bootstrap-popover

} //end of show function
