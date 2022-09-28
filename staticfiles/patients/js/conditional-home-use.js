$(function(){
	var home_guide = $( "h2:contains('Οδηγίες για Χρήση στο σπίτι')" ).parent();
	conditional_home_guide();
	// var icu_section = $( "h2:contains('ΜΕΘ')" ).parent();
	// icu_section.hide();

	$('[name="treatment_provider"]').change(conditional_home_guide);

	function conditional_home_guide() {
	    if ($("[name='treatment_provider']:radio[value='1']").is(':checked')) {
	    	home_guide.hide();
	    	// icu_section.show();
	    }
	    else {
	    	home_guide.show();
	    	// icu_section.hide();
	    }
	  }
	
});