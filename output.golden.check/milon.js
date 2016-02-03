function show_subjects(subjects_ptr) {
    //alert(subjects_ptr);
//    var opened = window.open("", _self);
	var subjects_html = "";

	var index, len;
	for (index = 0, len = subjects_ptr.length; index < len; ++index) {
		var ptr = (subjects_ptr[index]);
		var subject = ptr[0];
		var section = ptr[1];
		var url = ptr[2];
        subjects_html += '<a class="search_result" href=' + url + '>' + subject + '  (' + section + ')</a>  <p>';
	}

	document.body.innerHTML = subjects_html;

//	opened.document.write('<html dir="rtl"><head><meta charset="utf-8"><link href="fixed_bar.css" rel="stylesheet"><title>תוצאות חיפוש</title></head><body>' + subjects_html + '</body></html>');
}

function search() {
    val = document.getElementById("subject_search").value;
	var clean_val = val.replace(/[\|&;\$%@"'<>\(\)\+,]/g, "");
	document.getElementById("subject_search").value = "";
	document.getElementById("subject_search").placeholder = ("מחפש...");

	item = data[clean_val];
	console.log(val);
	console.log(clean_val);
	if (item == undefined) {
		document.getElementById("subject_search").placeholder = ("לא נמצא" );
	} else {
	    if (item.length > 1) {
	    	window.location = "search.html?"+clean_val;
//			var w = window.open('search.html')
//			w.addEventListener('load', w.doSomething, true);
//	    	show_subjects(item)
	    } else {
			tuple = item[0];
			url = tuple[2]
			console.log(url);
			window.location = url;
	    }
		document.getElementById("subject_search").placeholder = ("ערך לחיפוש");
	};
}

function page_loaded(url) {
	if (typeof(Storage) !== "undefined") {
		localStorage.setItem("last_url", url);
	};
}
