$(function(){
	$(".dropdown-menu a").click(function(){

	     var selection = $(this).text();
	     $("#dropdownVisitMenuButton:first-child").text(selection);
	     if (selection!="Νέα Επίσκεψη"){ 
	    	// trim everything before first and after last parenthesis
	    	 vdate = selection.replace(/^[^(]*\(/, "")
	    			 .replace(/\)[^(]*$/, "").replace(/-/g, "/");
	    	 $("#visitDateBox #id_visit_date").val(vdate);
		     $("#visitDateBox").submit();
	     }
	  });
});