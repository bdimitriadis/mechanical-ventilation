$(function(){
	showHideMaskTypeFld();
	$('[name="ma_type"]').change(showHideMaskTypeFld);
});

function showHideMaskTypeFld() {
	var mask_type_sel = $('[name="mask_type"]').parent().parent();
	var value = $('[name="ma_type"]').find(":selected").text();;
	if(value === "ΕΜΑ") {
		mask_type_sel.hide();

	} else {
		mask_type_sel.show();
	}
}