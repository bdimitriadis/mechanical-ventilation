$(function(){
	showHideCheckFields();
	$('[name="technical_check"]').change(showHideCheckFields);
});

function showHideCheckFields() {
	// var technical_check = $('[name="technical_check"]').val();
	var check_cause = $('[name="check_cause"]').parent().parent();
	var checked_by = $('[name="checked_by"]').parent().parent();
	// console.log(technical_check);
	if($('[name="technical_check"]').is(':checked')) {
		check_cause.show();
		checked_by.show();
	} else {
		check_cause.hide();
		checked_by.hide();
	}
}