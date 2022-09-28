$(function(){
	var checked_section_flds = [];
	var checkbox_to_section = {"overnight_oximetry":"avsao2_oxy", "level_three_rec": "record_duration", "polysomnography": "psg_trt"}
	$('[name="overnight_oximetry"], [name="level_three_rec"], [name="polysomnography"]').each(function () {
		top_level_div = $('[name='+checkbox_to_section[$(this).attr('name')]+']').parent().parent().parent();
		if($(this).is(':checked')) {
			top_level_div.show();
		} else {
			top_level_div.hide();
		}
	});

	$('[name="overnight_oximetry"], [name="level_three_rec"], [name="polysomnography"]').change(showHideSleepTests);
});

function showHideSleepTests() {
	var checkbox_to_section = {"overnight_oximetry":"avsao2_oxy", "level_three_rec": "record_duration", "polysomnography": "psg_trt"};

	if ($(this).attr('name') in checkbox_to_section) {
		top_level_div = $('[name='+checkbox_to_section[$(this).attr('name')]+']').parent().parent().parent();
	}

	if($(this).is(':checked')) {
		top_level_div.show();
	} else {
		top_level_div.hide();
	}

}