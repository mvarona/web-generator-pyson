function printCurrentYear() {
	document.querySelector(".current-year").innerHTML = "© " + new Date().getFullYear();
}

function updateBgc(){
	var velocity = 0.3;
	var pos = $(window).scrollTop(); 
	$('section').each(function() { 
		var $element = $(this);
		var height = $element.height()-18;
		$(this).css('backgroundPosition', '50% ' + Math.round((height - pos) * velocity) + 'px'); 
	});
}

function setUpScrollEffect(){
	$(window).bind('scroll', updateBgc);
}

function renderGeneralSettings(){
	printCurrentYear();
	setUpScrollEffect();
}

function loadGalleryItem(index){
	$('.carousel').carousel(index);
}