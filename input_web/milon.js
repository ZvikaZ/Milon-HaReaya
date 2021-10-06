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


////////////////////////////////////////////////////////////////////////


function show_failed_search_modal(val) {
    document.getElementById("search_modal").innerHTML = '\
    <div class="modal-dialog">\
        <div class="modal-content">\
            <div class="modal-header">\
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>\
                <h4>חיפוש</h4>\
            </div>\
            <div class="modal-body">\
                הביטוי "' + val + '" לא נמצא\
            </div>\
        </div>\
    </div>\
    ';
    $("#search_modal").modal('show');

}

$(function () {
    $('#search_modal').on('show.bs.modal', function () {
        var myModal = $(this);
        clearTimeout(myModal.data('hideInterval'));
        myModal.data('hideInterval', setTimeout(function () {
            myModal.modal('hide');
        }, 2000));
    });
});

////

$(document).ready(function () {
    $("#search_icon_button").click(function () {
        initSearchDialog();
        $("#searchDialogModal").modal();
    });
});

function initSearchDialog() {
    let key = 'searchMethod'
    if (sessionStorage[key]) {
        document.getElementById(sessionStorage[key]).checked = true;
    } else if (localStorage[key]) {
        document.getElementById(localStorage[key]).checked = true;
    } else
        document.getElementById("everywhere").checked = true;
}

function show_search_result(subjects, method, term) {
    console.time("show_search_result");

    let subjects_html;

    let key = "show_" + method + "&&&" + term;
    if (sessionStorage[key]) {
        console.log("show_search_result: using cache");
        subjects_html = sessionStorage[key];
    } else {
        console.log("show_search_result: not using cache")

        subjects_html = '<div class="container-fluid"><p>';

        subjects_html += "<h5>" + term + "</h5>"

        subjects_html += '<ol>';

        function highlight(s, term) {
			if (typeof s === 'string') {
				for (let word of term.split(" ")) {
					//var re = new RegExp("\\b" + word, "gu");  //TODO JS doesn't really support 'word-boundry' in Unicode regex
					var re = new RegExp(word, "g")
					s = s.replace(re, '<span class="highlight">' + word + '</span>')
				}
				return s
			} else {
				return "";
			}
        }

        for (var item of subjects) {
            subjects_html += '<li><a class="search_result" href=' + item.doc.url + '>' +
                highlight(item.doc.subject, term) +
                '  (<small>' + item.doc.section + '</small>)</a> ' +
                '<em>' + ', התאמה: ' + Math.ceil(item.score * 10) + "</em><br>" +		// ceil - to avoid zero score
                '<small>' + highlight(item.doc.data, term) + "</small>"

            let highlight_footnotes = highlight(item.doc.footnotes, term)
            if (highlight_footnotes != item.doc.footnotes)
                subjects_html += '<em><small>' + '<br>' + highlight_footnotes + '</small></em>'
            highlight_footnotes += "</li>";

        }

        subjects_html += "</ol></div>";

        sessionStorage[key] = subjects_html;
    }
    console.timeEnd("show_search_result");
    document.body.innerHTML = subjects_html;
}

function actual_searching(method, val) {
    let key = "raw_" + method + "&&&" + val;
    if (sessionStorage[key]) {
        return JSON.parse(sessionStorage[key])
    }

    let results;
    console.time("search index load")
    let searchIndex = elasticlunr.Index.load(indexDump);
    console.timeEnd("search index load")
    console.time("search")
    switch (method) {
        case "exact_subject":
            results = searchIndex.search(val, {
                fields: {
                    subject: {boost: 2},
                },
                bool: "AND",
                expand: false
            });
            break;
        case "subjects_only":
            results = searchIndex.search(val, {
                fields: {
                    subject: {boost: 2},
                },
                bool: "AND",
                expand: true
            });
            break;
        case "everywhere":
            results = searchIndex.search(val, {
                fields: {
                    subject: {boost: 2},
                    data: {boost: 1},
                    footnotes: {boost: 0.8},
                },
                bool: "AND",
                expand: true
            });
            break;
        default:
            console.log("Received strange searching 'method': ", method);
            break;
    }
    console.timeEnd("search")
    sessionStorage[key] = JSON.stringify(results)
    return results;
}


function search() {
    let val = document.getElementById("subject_search").value;
    let method = document.querySelector('input[name="searchRadio"]:checked').id;
    // storing to both of them because of https://github.com/electron-userland/electron-builder/issues/3885
    sessionStorage['searchMethod'] = method
    localStorage['searchMethod'] = method
    console.log("search function: ", method, ". ", val);

    if (val) {
        let clean_val = val.replace(/[\|&;\$%@"'<>\(\)\+,]/g, "");

        let items = actual_searching(method, clean_val);
        if (items.length == 0) {
            show_failed_search_modal(clean_val);
        } else {
            // show_search_result(items)
            if (items.length > 1 || !items[0].doc.subject.includes(clean_val)) {
                window.location = "search.html?method=" + method + "&term=" + clean_val;
            } else {
                let url = items[0].doc.url;
                console.log(url);
                window.location.href = url;
            }
        }
        document.getElementById("subject_search").value = "";
    }
}


////////////////////////////////////////////////////////////////////////


function page_loaded(url) {
    if (typeof (Storage) !== "undefined") {
        localStorage.setItem("last_url", url);
    }
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
    if (!history.state && typeof (history.replaceState) == "function")
        history.replaceState({page: history.length, href: location.href}, "foo");
    // now history.state is the index of the current page in window.history
}

$(window).load(function () {
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
$(document).ready(function () {
    $('#searchDialogModal').on('shown.bs.modal', function () {
        $('#subject_search').trigger('focus');
    });
});

// //TODO do it once and for all? this code gets executed on every page, every refresh
// $(document).ready(function() {
// 	searchIndex = elasticlunr.Index.load(indexDump);
// 	sessionStorage.setItem('searchIndex', searchIndex);
// });


