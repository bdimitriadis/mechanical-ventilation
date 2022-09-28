$(function() {
	function refresh_bmi() {
		$('[name="bmi"]').val(function(){
			return ($('[name="weight"]').val()/Math.pow($('[name="height"]').val()/100, 2)).toFixed(1);
		});
	}
	
	refresh_bmi();
	$('[name="weight"], [name="height"]').change(function(){
		console.log('Doyleyei!');
		refresh_bmi();
	});
	
});

	