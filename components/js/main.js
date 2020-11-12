function printCurrentYear() {
	document.querySelector(".current-year").innerHTML = "© " + new Date().getFullYear();
}

function updateBgc(){
	var velocity = 0.3;
	// var pos = $(window).scrollTop(); 
	// $('section').each(function() { 
	// 	var $element = $(this);
	// 	var height = $element.height()-18;
	// 	$(this).css('backgroundPosition', '50% ' + Math.round((height - pos) * velocity) + 'px'); 
	// });
}

function setUpScrollEffect(){
	$(window).bind('scroll', updateBgc);

	var movementStrength = 25;
	var height = movementStrength / $(window).height();
	var width = movementStrength / $(window).width();
	$("*").mousemove(function(e){
		var pageX = e.pageX - ($(window).width() / 2);
		var pageY = e.pageY - ($(window).height() / 2);
		var newvalueX = width * pageX * -1 - 25;
		var newvalueY = height * pageY * -1 - 50;
		$('section').css("background-position", newvalueX+"px     "+newvalueY+"px");
	});
}

function renderGeneralSettings(){
	printCurrentYear();
	setUpScrollEffect();
}

function loadGalleryItem(index){
	$('.carousel').carousel(index);
}