function show_search_modal(val) {
  document.getElementById("search_modal").innerHTML = `
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>
                <h4>חיפוש</h4>
            </div>
            <div class="modal-body">
                הערך '`+ val + `' לא נמצא
            </div>
        </div>
    </div>
    `;
 $("#search_modal").modal('show');

};

$(function(){
    $('#search_modal').on('show.bs.modal', function(){
        var myModal = $(this);
        clearTimeout(myModal.data('hideInterval'));
        myModal.data('hideInterval', setTimeout(function(){
            myModal.modal('hide');
        }, 2000));
    });
});


function show_subjects(subjects_ptr) {
    //alert(subjects_ptr);
//    var opened = window.open("", _self);
	var subjects_html = '<div class="container-fluid"><p><ol>';

	var index, len;
	for (index = 0, len = subjects_ptr.length; index < len; ++index) {
		var ptr = (subjects_ptr[index]);
		var subject = ptr[0];
		var section = ptr[1];
		var url = ptr[2];
        subjects_html += '<li><a class="search_result" href=' + url + '>' + subject + '  (<small>' + section + '</small>)</a></li> ';
	}
	subjects_html += "</ol></div>"

	document.body.innerHTML = subjects_html;

//	opened.document.write('<html dir="rtl"><head><meta charset="utf-8"><link href="fixed_bar.css" rel="stylesheet"><title>תוצאות חיפוש</title></head><body>' + subjects_html + '</body></html>');
}

function search() {
    console.log("search function")
    val = document.getElementById("subject_search").value;
    if (val) {
	var clean_val = val.replace(/[\|&;\$%@"'<>\(\)\+,]/g, "");
    //	document.getElementById("subject_search").placeholder = ("מחפש...");

        item = data[clean_val];
        console.log(val);
        console.log(clean_val);
        if (item == undefined) {
            show_search_modal(clean_val);
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
                window.location.href = url;
            }
    //		document.getElementById("subject_search").placeholder = ("ערך לחיפוש");
        };
        document.getElementById("subject_search").value = "";
    };
}

function page_loaded(url) {
	if (typeof(Storage) !== "undefined") {
		localStorage.setItem("last_url", url);
	};
}

window.onload = function() {
    search_focused(false);
}

function search_focused(focus) {
    console.log("got focus?", focus);
    document.getElementById("menu_bar").style.maxWidth = focus ? "95%" : "";
    console.log(document.getElementById("search_icon").style.display);
    document.getElementById("search_icon").style.display = focus ? "" : "none";
//    document.getElementById("search_icon").style.fontSize = focus ? "20" : "0";
}
