$(function(){
	showHideInvasiveFld();
	$('[name="ventilation_type"]').change(showHideInvasiveFld);
});

function showHideInvasiveFld() {
	var invasive_sel = $('[name="invasive_ventilation"]').parent().parent();
	var value = $('[name="ventilation_type"]:checked').parent('label').text().trim();
	if(value === "Επεμβατικός") {
		invasive_sel.show();
	} else {
		invasive_sel.hide();
		
		/* If there was a validation error on submission
    	and pat_status changed value, also hide previous error */
    	prev = invasive_sel.prev();
    	
    	if (prev.attr('class')==="section-errors"){
    		prev.hide();
    	}
	}	
}