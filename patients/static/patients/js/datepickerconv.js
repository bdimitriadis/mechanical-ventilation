$(function() {
	$(".datepicker").each(function() {
		$(this).datepicker({
			format: "dd/mm/yyyy",
			startDate: $(this).attr('min'),
			endDate: $(this).attr('max'),
			autoclose: true,
			language: "el"
			});
	});
});
	    