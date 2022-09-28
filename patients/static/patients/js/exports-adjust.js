$(function(){
	$(".collapse .form-group>label").hide();
	$(".card-header>h5>input[type='checkbox']").change(function() {
		// Children checkboxes with same name
		var children_checkboxes=$("input[class='form-check-input'][type='checkbox'][name='"+this.name.replace("-check","")+"']" );
		children_checkboxes.prop("checked", this.checked);
	});
	
	// All Children checkboxes
	var child_cbs = $("input[class='form-check-input'][type='checkbox']");
	child_cbs.change(function(){
		var parent_checkbox = $(".card-header>h5>input[type='checkbox'][name='"+this.name+"-check']");
		
		// If all children checkboxes select for a specific parent with same name, then check parent else uncheck
	    if (child_cbs.filter("[name='"+this.name+"']:checked").length == child_cbs.filter("[name='"+this.name+"']").length) {
	    	parent_checkbox.prop("checked", this.checked)
	    } else {
	    	parent_checkbox.prop("checked", false)
	    }
	});

	$('.card-header .accordion-toggle').on("click",function(){
		$('> i', this).toggleClass("fas fa-angle-down");
		$('> i', this).toggleClass("fas fa-angle-up");
	});
});