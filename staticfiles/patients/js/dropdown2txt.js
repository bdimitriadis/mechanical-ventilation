$(function(){
	$("a.add-prof-btn").on('click', function(){
		$txtinput = $('<input type="text" maxlength="80">');
		$profselect = $('[name="profession"]');
		// Get all select widget's attributes
		var attributes = $profselect.prop("attributes");

		// Update text input widget with select's attributes
		$.each(attributes, function() {
			$txtinput.attr(this.name, this.value);
		});


		$profselect
		    .replaceWith($txtinput);
		});
});