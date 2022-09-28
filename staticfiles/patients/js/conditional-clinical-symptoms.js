$(function(){
	setHasSymptoms();
	toggleClinicalSymptoms();
	$("input[name='clinical_symptoms']").on('change', setHasSymptoms);
	$("input[name='has_symptoms']").on('change', toggleClinicalSymptoms);
});

function toggleClinicalSymptoms() {
	var has_symptoms = $("input[name='has_symptoms']:checked").val();
	var symptoms_div = $("input[name='clinical_symptoms']").closest($("div"), ".form-group").parent().parent().parent();

	if(has_symptoms === 'True') {
		// Show clinical symptoms field
		symptoms_div.show()
	} else {
		// Hide clinical symptoms and possible existant error message
		$("input[name='clinical_symptoms']").prop("checked", false);
		symptoms_div.hide()
		next = symptoms_div.next();

		if (next.hasClass("field-error")){
			next.hide();
		}
	}

}

function setHasSymptoms() {
	var any_symptoms = $("input[name='clinical_symptoms']:checked");
	var symptoms_div = $("input[name='clinical_symptoms']").closest($("div"), ".form-group").parent().parent();

	// If there are symptoms checked, or error from previous effort to check yes, then have Yes checked else check No
	if (any_symptoms.length || symptoms_div.parent().hasClass("border-error")) {
		$("input[name='has_symptoms'][value='True']").prop("checked", true);

	} else {
		$("input[name='has_symptoms'][value='False']").prop("checked", true);
		toggleClinicalSymptoms();
	}
}