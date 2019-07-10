var CALENDAR = function () { 
	    var wrap, label,  
	            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]; 
 
	    function init(newWrap) { 
			wrap     = $(newWrap || "#cal"); 
			label    = wrap.find("#label"); 
			wrap.find("#prev").bind("click.calendar", function () { switchMonth(false); }); 
			wrap.find("#next").bind("click.calendar", function () { switchMonth(true);  }); 
			label.bind("click", function () { switchMonth(null, new Date().getMonth(), new Date().getFullYear()); });        
			label.click();	
	    } 
 
	    function switchMonth(next, month, year) { 
			var curr = label.text().trim().split(" "), calendar, tempYear =  parseInt(curr[1], 10); 
			month = month || ((next) ? ( (curr[0] === "December") ? 0 : months.indexOf(curr[0]) + 1 ) : ( (curr[0] === "January") ? 11 : months.indexOf(curr[0]) - 1 )); 
			year = year || ((next && month === 0) ? tempYear + 1 : (!next && month === 11)	
	    } 
 
	    function createCal(year, month) { 
 
	    } 
	    createCal.cache = {}; 
	    return { 
	        init : init, 
	        switchMonth : switchMonth, 
	        createCal   : createCal 
	    }; 
	};

var cal = CALENDAR(); 
 
cal.init();