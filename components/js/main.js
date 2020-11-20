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

function truncateMenuItems(){
	const MAX_LENGTH = 21;
	const items = document.querySelectorAll(".span-wrapper a");
	items.forEach(item => {
		if (item.innerHTML.length > MAX_LENGTH){
			item.innerHTML = item.innerHTML.slice(0, MAX_LENGTH) + "...";
		}
	});
}

function renderSkillsChart(){
	var ctx = document.getElementById('skills-chart').getContext('2d');
	var myChart = new Chart(ctx, {
	    type: 'horizontalBar',
	    data: {
	        labels: Object.keys(skillsData),
	        datasets: [{
	            label: '',
	            data: Object.values(skillsData),
	            backgroundColor: [
	                '#1abc9c',
	                '#16a085',
	                '#2ecc71',
	                '#27ae60',
	                '#3498db',
	                '#2980b9',
	                '#9b59b6',
	                '#8e44ad',
	                '#34495e',
	                '#2c3e50',
	                '#f1c40f',
	                '#f39c12',
	                '#e67e22',
	                '#d35400',
	                '#e74c3c',
	                '#c0392b',
	                '#ecf0f1',
	                '#bdc3c7',
	                '#95a5a6',
	                '#7f8c8d'
	            ],
	            borderColor: [
	                'rgba(75, 192, 192, 1)'
	            ],
	            borderWidth: 1
	        }]
	    },
	    options: {
	        scales: {
	            xAxes: [
            	{
	            	position: 'bottom',
	                ticks: {
	                	mirror: false,
	                	beginAtZero: true,
	                    callback: function(value, index, values) {
	                    	let lan = document.getElementsByTagName('html')[0].getAttribute('lang');
	                    	console.log("lan " + lan);
	                    	if (value == 0) {
	                    		return skillsLevelsStrings["insufficient_" + lan];
	                    	} else if (value == 50){
	                    		return skillsLevelsStrings["sufficient_" + lan];
	                    	} else if (value == 100){
	                    		return skillsLevelsStrings["excellent_" + lan];
	                    	}
	                    },
	                    fontColor: '#fff',
	                    fontSize: 16
	                }
	            }],
	            yAxes: [{
	            	ticks: {
	            		mirror: true,
	                    fontColor: '#fff',
	                    fontStyle: 'normal',
	                    fontSize: 15
	                }
	            }]
	        },
	        animation: {
			    onProgress () {
			      const chartInstance = this.chart;
			      const ctx = chartInstance.ctx;
			      const dataset = this.data.datasets[0];
			      const meta = chartInstance.controller.getDatasetMeta(0);

			      Chart.helpers.each(meta.data.forEach((bar, index) => {
			        const label = this.data.labels[index];
			        const labelPositionX = 50;
			        const labelWidth = ctx.measureText(label).width + labelPositionX;

			        ctx.textBaseline = 'middle';
			        ctx.textAlign = 'left';
			        ctx.font = "normal 15px Helvetica";
			        ctx.fillStyle = '#fff';
			        ctx.fillText(label, labelPositionX, bar._model.y);
			      }));
			    }
		  	},
		  	legend: {
			    display: false,
			      labels: {
			        display: false
			      }
		  	}
	    }
	});
}

function conditionalChartRendering(){
	var charts = document.querySelectorAll('#skills-chart');
	if (charts.length > 0){
		renderSkillsChart();
	}
}

function loadGalleryItem(index){
	$('.carousel').carousel(index);
}

function animateNumbers(){
	const animateCountUp = el => {
		const animationDuration = 1500;
		const frameDuration = 1000 / 60;
		const totalFrames = Math.round(animationDuration / frameDuration);
		const easeOutQuad = t => t * ( 2 - t );
		let frame = 0;
		const countTo = parseInt( el.innerHTML, 10 );
		const counter = setInterval( () => {
			frame++;
			const progress = easeOutQuad(frame / totalFrames );
			const currentCount = Math.round( countTo * progress );
			if (parseInt(el.innerHTML, 10) !== currentCount ) {
				el.innerHTML = currentCount;
			}
			if (frame === totalFrames) {
				clearInterval(counter);
			}
		}, frameDuration);
	};

	const runAnimations = () => {
		const countupEls = document.querySelectorAll('.animateNumber');
		countupEls.forEach(animateCountUp);
	};
	runAnimations();
}

function detectLanguage(){
	let userLang = navigator.language || navigator.userLanguage;
	let enDetected = "We think we have a better version for you! <a href='https://www.mvarona.dev/en/index'>Read this site in English</a>";
	let esDetected = "¡Creemos que tenemos una mejor versión para ti! <a href='https://www.mvarona.dev/en/index'>Lee este sitio en español</a>";
	let deDetected = "Wir denken, wir haben eine bessere Version für dich! <a href='https://www.mvarona.dev/en/index'>Lies diese Seite auf Deutsch</a>";
	let url = window.location.href;
	let warning = document.querySelector('#lan-alert');
	let newElement = document.createElement('span');
		
	if (userLang.includes('es') && !url.includes('es/')){
		newElement.innerHTML = esDetected;
		warning.insertBefore(newElement, warning.firstChild);
		$('#lan-alert').delay(500).slideDown();
	} else if (userLang.includes('de') && !url.includes('de/')){
		newElement.innerHTML = deDetected;
		warning.insertBefore(newElement, warning.firstChild);$('#lan-alert').show();
		$('#lan-alert').delay(500).slideDown();
	} else if (userLang.includes('en') && !url.includes('en/')){
		newElement.innerHTML = enDetected;
		warning.insertBefore(newElement, warning.firstChild);
		$('#lan-alert').delay(500).slideDown();
	}


}

function renderGeneralSettings(){
	printCurrentYear();
	setUpScrollEffect();
	truncateMenuItems();
	conditionalChartRendering();
	animateNumbers();
	detectLanguage();
}

$("#lan-alert").on("click", "button.close", function() {
	$(this).parent().slideUp(500).delay(1000).hide('slow');
});