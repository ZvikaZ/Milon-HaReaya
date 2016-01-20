function search() {
    val = document.getElementById("subject_search").value;
	var clean_val = val.replace(/[\|&;\$%@"'<>\(\)\+,]/g, "");
	document.getElementById("subject_search").value = ""
	document.getElementById("subject_search").placeholder = "ערך לחיפוש"

	item = data[clean_val];
	console.log(val);
	console.log(clean_val);
	if (item == undefined) {
		document.getElementById("subject_search").value = ""
		document.getElementById("subject_search").placeholder = ("לא נמצא" )
	} else {
	    tuple = item[0];
		url = tuple[0]+".html#"+tuple[1]
		console.log(url);
		window.location = url;
	};
}
