$(function() {
	var init_val = $('[name="total_hospitalizations"]').val();
	$('[name="cur_year_hospitalizations"]').change(function(){
		$('[name="total_hospitalizations"]').val(+init_val + +$('[name="cur_year_hospitalizations"]').val());
	});
});

	