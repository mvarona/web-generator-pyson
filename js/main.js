function printCurrentYear() {
	document.querySelector(".current-year").innerHTML = "© " + new Date().getFullYear();
}

function renderGeneralSettings(){
	printCurrentYear();
}
