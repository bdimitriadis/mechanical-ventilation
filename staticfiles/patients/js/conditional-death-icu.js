$(function(){
	showHideICUExitTransferFld();
	$('[name="icu_outcome"]').change(showHideICUExitTransferFld);
});

function showHideICUExitTransferFld() {
	var exit_transfer_div = $('[name="icu_exit_transfer"]').parent().parent();
	var death_date_div = $('[name="death_date"]').parent().parent()
	var death_cause_div = $('[name="death_cause"]').parent().parent();
	var value = $('[name="icu_outcome"]').find(":selected").text();
	console.log(value);
	exit_transfer_div.hide();
	death_date_div.hide();
	death_cause_div.hide();

	if (value === "Θάνατος") {
		exit_transfer_div.hide();
		death_date_div.show();
		death_cause_div.show();
	} else if (value === "Έξοδος")  {
		exit_transfer_div.show();
		death_date_div.hide();
		death_cause_div.hide();
	}
}