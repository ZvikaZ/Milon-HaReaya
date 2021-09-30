// called on index.html's BODY
function init() {
    document.addEventListener("deviceready", onDeviceReady, false);
	console.log("Hi");
}

// PhoneGap is loaded and it is now safe to make calls PhoneGap methods
function onDeviceReady() {
	//alert(AppVersion.version);
	//alert(AppVersion.build);
	console.log("device ready");
//	console.log(localStorage.last_build);
//	console.log(AppVersion.build);
//
//	// jump to last location - if it's valid, and user already saw this version of index.html
//	if (localStorage.last_build == AppVersion.build) {
//		//console.log("localStorage.get last_url = " + localStorage.getItem("last_url"))
//		//window.location.replace = localStorage.getItem("last_url");
//
//		//console.log("Going back");
//		// copied from http://stackoverflow.com/questions/16542118/phonegap-navigator-app-backhistory-not-working-on-html-back-button
//		//history.go(-1);
//	    //navigator.app.backHistory();
//
//	};
//	localStorage.last_build = AppVersion.build;

	$(".hidden-on-mobile").hide();


}


function show_failed_search_modal(val) {
  document.getElementById("search_modal").innerHTML = '\
    <div class="modal-dialog">\
        <div class="modal-content">\
            <div class="modal-header">\
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>\
                <h4>חיפוש</h4>\
            </div>\
            <div class="modal-body">\
                הערך "'+ val + '" לא נמצא\
            </div>\
        </div>\
    </div>\
    ';
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


function show_subjects(subjects) {
    console.log("show_subjects: ", subjects);

	var subjects_html = '<div class="container-fluid"><p><ol>';

	subjects_arr = subjects.split(',');
	console.log("show_subjects arr: ", subjects_arr);
	for (index = 0, len = subjects_arr.length; index < len; ++index) {
	    var subject = subjects_arr[index];
	    subjects_html += show_subjects_single(data[subject]);
	};
	
	subjects_html += "</ol></div>"

	document.body.innerHTML = subjects_html;

};

function show_subjects_single(subjects_ptr) {
    console.log("single: ", subjects_ptr);
	var subjects_html = ""

	var index, len;
	for (index = 0, len = subjects_ptr.length; index < len; ++index) {
		var ptr = (subjects_ptr[index]);
		var subject = ptr[0];
		var section = ptr[1];
		var url = ptr[2];
        subjects_html += '<li><a class="search_result" href=' + url + '>' + subject + '  (<small>' + section + '</small>)</a></li> ';
	}
	
	return subjects_html;
}

function actual_searching(method, val) {
    switch(method) {
	    case "exact_expr":
		    if (val in data) {
	            return [val];
		    } else {
			    return [];
			};
			break;
	    case "whold_word":
		    results = [];
			Object.keys(data).forEach(whole_word_search_function, val)
			return results;
			break;
	    case "partial":
		    results = [];
			Object.keys(data).forEach(partial_search_function, val)
			return results;
			break;
		default:
		    // we shouldn't really get here, it's just for the safe side
		    console.log("Received strange searching 'method': ", method);
		    if (val in data) {
	            return [val];
		    } else {
			    return [];
			};
			break;
	};
}


function whole_word_search_function(currentValue, index) {
    // 'this' holds the expression to be searched
	// currentValue is the current iteration from data dict
	
	// JS's regular '\b' doesn't work with Unicode, only with ASCII!
	// this bypass is taken from http://stackoverflow.com/questions/10590098/javascript-regexp-word-boundaries-unicode-characters
	var unicode_word_boundry = "(?:^|$|\\s)"
    if (new RegExp(unicode_word_boundry + this + unicode_word_boundry).test(currentValue)) {
	    console.log("Found ", this, " in ", currentValue);
		   results.push(currentValue);
	}
}

function partial_search_function(currentValue, index) {
    // 'this' holds the expression to be searched
	// currentValue is the current iteration from data dict
    if (currentValue.includes(this)) {
	    console.log("Found ", this, " in ", currentValue);
		   results.push(currentValue);
	}
}

function search() {
    val = document.getElementById("subject_search").value;
	method = document.querySelector('input[name="searchRadio"]:checked').id;
	console.log("search function: ", method, ". ", val);
    if (val) {
	    var clean_val = val.replace(/[\|&;\$%@"'<>\(\)\+,]/g, "");
		
		items = actual_searching(method, clean_val);
        console.log(items);
        if (items.length == 0) {
            show_failed_search_modal(clean_val);
        } else {
            if (items.length > 1 || data[items[0]].length > 1) {
				window.location = "search.html?"+items;
            } else {
                tuple = data[items][0];
                url = tuple[2]
                console.log(url);
                window.location.href = url;
            }
        };
        document.getElementById("subject_search").value = "";
    };
}

function page_loaded(url) {
	if (typeof(Storage) !== "undefined") {
		localStorage.setItem("last_url", url);
	};
}

function goBack() {
	window.history.back();
}

function goForward() {
	window.history.forward();
}

// https://stackoverflow.com/questions/32017791/how-to-find-the-current-location-index-in-the-browser-history
// Onload
{
    if (!history.state  &&  typeof(history.replaceState) == "function")
        history.replaceState({ page: history.length, href: location.href }, "foo");
	// now history.state is the index of the current page in window.history
}

$(window).load(function() {
	if (history.state.page == 1) {
		$("#back_icon_button").prop('disabled', true)
	} else {
		$("#back_icon_button").prop('disabled', false)
	}
	if (history.state.page == window.history.length) {
		$("#forward_icon_button").prop('disabled', true)
	} else {
		$("#forward_icon_button").prop('disabled', false)
	}
})


// https://stackoverflow.com/questions/49178396/autofocus-input-element-on-modal-open-bootstrap-4
$(document).ready(function() {
  $('#searchDialogModal').on('shown.bs.modal', function() {
    $('#subject_search').trigger('focus');
  });
});



//D window.onload = function() {
//D     search_focused(false);
//D }
//D 
//D function tcm_menu_bar_width_change(i, stop, delta) {
//D 	document.getElementById("menu_bar").style.maxWidth = i.toString() + "%";
//D 	if (i != stop) {
//D 		setTimeout(function() {tcm_menu_bar_width_change(i + delta, stop, delta)}, 1);
//D 	}
//D }
//D 
//D function search_focused(focus) {
//D     console.log("got focus?", focus);
//D     var menu_bar_min_width = 40;
//D     var menu_bar_max_width = 96;
//D     if (focus) {
//D 	//	tcm_menu_bar_width_change(menu_bar_min_width, menu_bar_max_width, +2);
//D     } else {
//D 	//	tcm_menu_bar_width_change(menu_bar_max_width, menu_bar_min_width, -2);
//D 	    //-- we want to fade out to be delayed, to allow user clicking in the radio buttons
//D 		//setTimeout(function() {
//D 		//	tcm_menu_bar_width_change(menu_bar_max_width, menu_bar_min_width, -2)
//D 		//}, 5000);
//D 		//console.log("scheduling delayed blurring");
//D 	}
//D //    document.getElementById("menu_bar").style.maxWidth = focus ? "95%" : "";
//D     document.getElementById("search_icon").style.display = focus ? "" : "none";
//D }
