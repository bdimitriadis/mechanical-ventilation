$(function(){
	showHideΕmergingFld();
	$('[name="doc_awareness"]').change(showHideΕmergingFld);
});

function showHideΕmergingFld() {
	var emerging_sel = $('[name="emerging_awareness"]').parent().parent();
	var value = $('[name="doc_awareness"] option:selected').text();
	console.log(value);
	if(value === "Έκτακτη Ενημέρωση") {
		emerging_sel.show();
	} else {
		emerging_sel.hide();
		
		/* If there was a validation error on submission
    	and doc_awareness changed value, also hide previous error */
    	prev = emerging_sel.prev();
    	
    	if (prev.attr('class')==="section-errors"){
    		prev.hide();
    	}
	}	
}