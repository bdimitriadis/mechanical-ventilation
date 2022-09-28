$(function(){
	showHideDeathDateFld();
	$('[name="pat_status"]').change(showHideDeathDateFld);
});

function showHideDeathDateFld() {
	var death_divs = [$('[name=date_of_death]').parent().parent(), $('[name=cause_of_death]').parent().parent()];
	var value = $('[name="pat_status"]').find(":selected").text();
	for(var i=0; i<death_divs.length; i++) {
		if (value === "Θάνατος") {
			death_divs[i].show();
	    } else {
	    	death_divs[i].hide();
	    	
	    	/* If there was a validation error on submission
	    	and pat_status changed value, also hide previous error */
	    	prev = death_divs[i].prev();
	    	if (prev.attr('class')==="errorlist"){
	    		prev.hide();
	    	}
	    }
	}
	
}