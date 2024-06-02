# TODO: add waiting cursor
# TODO: programmatically delete and create core; upload files; update solr index
# TODO: add splash to android
# TODO: Hebrew solr search

# TODO: check 'אשכח תמרי' - the link to 'משל עניינו של רבי מאיר' ; and many more links in this page
# TODO: fix new errors in file
# TODO: refactor, split to files, unit tests
# TODO: why "Pashut" is unknown?
# TODO: fix "FOOTNOTE undefined: af7 None  :  homo"

# TODO: TEX: with new version, " looks different (it's curly)

# TODO: TEX: 'tex.full' line 8089 failure (8246) - because of "Vav" in "Otiyot" - need to delete previous line, and re-enter
# TODO: TEX: Mehkarim UVeurim - handle style (w/o numbers...)
# TODO: TEX: add prefixes and appendices
# TODO: TEX: clean milon.tex, handle koma recommendations
# TODO: TEX: make sure that "fake_subject_normal" is correct - currently different between HTML and LyX
# TODO: TEX: make sure there aren't any "Takala" in .tex file
# TODO: TEX: publish my Tex packages?
# TODO: create indexes? (both before and after main text...)

# TODO: Clean 'UNKNOWN's and 'fix_sz_cs'
# TODO: verify that it's running on clean GIT clone

# TODO: change 'is_prev_subject(..)' to correctly handle "Toar Shem Tov" - should be more freely checking
# TODO: otiyot - stam font
# TODO: pagination at end
# TODO: subject_light vs sub-subjet_light - wait for Rav's response

# TODO: subjects size in Mehkarim
# TODO: references numbering
# TODO: search "Natziv" not working
# TODO: Yud and Lamed in Psukim
# TODO: splitted bubject, like "אמר לו הקדוש ברוך הוא (לגבריאל° שבקש להציל את אברהם־אבינו° מכבשן האש) אני יחיד בעולמי והוא יחיד בעולמו, נאה ליחיד להציל את היחיד"

# TODO: circles shouldn't be part of subjects (and what about parentheses?)
# TODO: "Mehkarim" - make links, check styles!
# TODO: Change "opening_abbrev.html" styling
# TODO: handle footnotes' styles
# TODO: "Ayen", "Re'e" - see mail from 22.1.16
# TODO: "all subjects" page

# TODO: make headings to links
# TODO: save current location (and history?, with back and forward?) - use HTML5 local storage
# TODO: search - results page - write first words of definition
# TODO: add letters to TOC
# TODO: make smarter links on circles ('Oneg' with and w/o Vav, 'zohama' with Alef or He, etc.)
# TODO: increase/decrease font size
# TODO: make definition in new line? (without ' - ')

# TODO: replace menu with Bootstrap style menu
# TODO: Make index.html's links clickable, or copyable
# TODO: better icon
# TODO: iphone?
# TODO: GUI

# installation:
# install node, yarn, cordova (android sdk, JDK8, gradle)

# remember:
# http://stackoverflow.com/questions/10752055/cross-origin-requests-are-only-supported-for-http-error-when-loading-a-local


import shutil
import copy

# import search_index
# from misc import replace_in_file
# from search_index import calc_subject_id, clean_name

import htmler
import texer


def open_html_doc(name, letter=None):
    html_doc = dominate.document(title="מילון הראיה")
    html_doc['dir'] = 'rtl'
    with html_doc.head:
        with tags.meta():
            tags.attr(charset="utf-8")
        with tags.meta():
            tags.attr(name="viewport", content="width=device-width, initial-scale=1")

        tags.script(src="jquery/dist/jquery.min.js")
        tags.link(rel='stylesheet', href='bootstrap-3.3.6-dist/css/bootstrap.min.css')
        tags.link(rel='stylesheet', href='style.css')
        tags.script(src="bootstrap-3.3.6-dist/js/bootstrap.min.js")
        tags.link(rel='stylesheet', href="bootstrap-rtl-3.3.4/dist/css/bootstrap-rtl.css")
        tags.link(rel='stylesheet', href='html_demos-gh-pages/footnotes.css')
        tags.script(src="milon.js")
        tags.script(src="html_demos-gh-pages/footnotes.js")
        tags.link(rel='shortcut icon', href='favicon.ico')

    html_doc.footnote_ids_of_this_html_doc = []
    html_doc.name = name
    if letter:
        html_doc.letter = letter
        html_doc.section = html_docs_l[-1].section
    else:
        html_doc.section = name

    html_doc.index = len(html_docs_l) + 1
    with html_doc.body:
        with tags.div():
            tags.attr(cls="container-fluid")
            # TODO: call page_loaded to update saved URL also in other links
            tags.script("page_loaded('%s.html')" % html_doc.index)

            with tags.div():
                tags.attr(cls="fixed_top_left", id="menu_bar")
                with tags.div():
                    with tags.button('הקודם', type="button"):
                        tags.attr(id="back_icon_button", type="button", cls="btn btn-default", onclick="goBack()")
                        # with tags.span():
                        #     tags.attr(cls="glyphicon glyphicon-arrow-left")
                    with tags.button('הבא', type="button"):
                        tags.attr(id="forward_icon_button", type="button", cls="btn btn-default", onclick="goForward()")
                        # with tags.span():
                        #     tags.attr(cls="glyphicon glyphicon-arrow-right")
                    with tags.button(type="button"):
                        tags.attr(id="search_icon_button", type="button", cls="btn btn-default")
                        with tags.span():
                            tags.attr(cls="glyphicon glyphicon-search")
                    with tags.span():
                        tags.attr(cls="dropdown")
                        with tags.button(type="button", cls="btn btn-primary") as b:
                            tags.attr(href="#")  # , cls="dropdown-toggle")
                            with tags.span():
                                tags.attr(cls="glyphicon glyphicon-menu-hamburger")
                                # b['data-toggle'] = "dropdown"
                        with tags.ul():
                            tags.attr(cls="dropdown-menu dropdown-menu-left scrollable-menu")

    return html_doc


def close_html_doc(html_doc):
    with html_doc.body.children[-1]:
        assert html_doc.body.children[-1]['class'] == 'container-fluid'
        with tags.div(id="search_modal"):
            tags.attr(cls="modal fade")

    with html_doc:
        # add footnotes content of this section:
        with tags.ol(id="footnotes"):
            for (id) in html_doc.footnote_ids_of_this_html_doc:
                footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
                assert footnote.id == id
                htmler.add_footnote_to_output(id, footnote.paragraphs)
                search_index.learn_footnote(footnote.paragraphs, html_doc.index)

        # add placeholder for searching
        tags.comment("search_placeholder")

    search_index.close_html_doc()

    place_holder = "<!--search_placeholder-->"
    with open("input_web/stub_search.html", 'r', encoding='utf-8') as file:
        search_html = file.read()

    html_doc_name = html_doc.index
    name = "debug_%s.html" % html_doc_name
    with open("output/www/" + name, 'w', encoding='utf-8') as f:
        f.write(html_doc.render(pretty=True))
    replace_in_file("output/www/" + name, place_holder, search_html)

    name = "%s.html" % html_doc_name
    with open("output/www/" + name, 'w', encoding='utf-8') as f:
        f.write(html_doc.render(pretty=False))
        print("Created ", name)
    replace_in_file("output/www/" + name, place_holder, search_html)


html_docs_l = []


def get_active_html_doc(para):
    try:
        prev_name = html_docs_l[-1].name
    except:
        prev_name = None
    name = is_need_new_section(para, prev_name)
    if name:
        if isinstance(name, tuple):
            op, new = name
            if op == 'NEW_LETTER':
                html_docs_l.append(open_html_doc(op, letter=new))
            else:
                assert op == 'UPDATE_NAME'
                print("Updating ", new)
                html_docs_l[-1].name = new
                html_docs_l[-1].section = new
        else:
            fixed_name = fix_section_name(name)
            html_docs_l.append(open_html_doc(fixed_name))
    return html_docs_l[-1]


try:
    shutil.rmtree("output")
except FileNotFoundError:
    pass

try:
    shutil.rmtree("tex")
except FileNotFoundError:
    pass

os.mkdir("output")
os.mkdir("tex")

os.chdir("../input_tex")
for (f) in (
        "milon.tex",
        "polythumbs.sty",
        "hebcolumnbal.sty",
        #  "hebrew-gymatria-fix.sty",     # Rav Kalner asked not to do it. Leaving it here for future reference...
):
    shutil.copyfile(f, os.path.join("../tex", f))
os.chdir("../")

texer.open_latex()


# Here starts the action!


def add_menu_to_apriory_htmls(html_docs_l):
    # add menus to index.html and search.html
    menu_bar = copy.deepcopy(html_docs_l[0].body.children[0].children[1])
    assert menu_bar['id'] == 'menu_bar'
    content = menu_bar.children[0].children[-1].children[1].children
    del (content[6].attributes['class'])

    place_holder = "<!--menu_bar-->"

    menu_bar_html = menu_bar.render(pretty=False)

    with open("input_web/stub_search.html", 'r', encoding='utf-8') as file:
        menu_bar_html += file.read()

    replace_in_file('output/www/search.html', place_holder, menu_bar_html)

    for index, filename in enumerate((
            'index.html',
            "opening_intros.html",
            "opening_haskamot.html",
            "opening_abbrev.html",
            "opening_signs.html",
    )):
        content[index].attributes['class'] = 'active'
        menu_bar_html = menu_bar.render(pretty=False)
        with open("input_web/stub_search.html", 'r', encoding='utf-8') as file:
            menu_bar_html += file.read()

        replace_in_file('output/www/%s' % filename, place_holder, menu_bar_html)
        del content[index].attributes['class']


if create_html:
    html_docs_l = fix_links(html_docs_l)
    add_menu_to_apriory_htmls(html_docs_l)

    for (html_doc) in html_docs_l:
        close_html_doc(html_doc)

if create_latex:
    texer.close_latex()

search_index.create_index()


# # TODO remove this
# # dictionary mapping subjects to list of pointers
# # each pointer is a tuple of (subject, html_doc's section name, url)
# subjects_db = {}
#
#
# def subject(html_doc, type, text):
#     result = tags.span()
#     with result:
#         clean_text = clean_name(text.strip())
#         new_subject_l = subjects_db.get(clean_text, [])
#         subject_id = calc_subject_id(text.strip(), len(new_subject_l))
#         new_subject_l.append((text.strip(), html_doc.section, "%s.html#%s" % (html_doc.index, subject_id)))
#         subjects_db[clean_text] = new_subject_l
#
#         with tags.span(text, id=subject_id):
#             tags.attr(cls=type)
#
#         # with tags.span(tags.a(text, href="#%s" % text.strip(), id=text.strip())):
#         #     tags.attr(cls=type)
#     return result


# def regular(type, text):
#     result = tags.span()
#     with result:
#         if type in ['footnote', 'footnote_recurrence']:
#             with tags.a("(%s)" % text.strip()):
#                 tags.attr(cls="ptr", text=text)
#         else:
#             if "\n" in text:
#                 print("New:", text)
#             if "°" in text:
#                 href = re.sub("°", "", text)
#                 href = re.sub("־", " ", href)
#                 with tags.span(tags.a(text, href="#" + href)):
#                     tags.attr(cls=type)
#             else:
#                 with tags.span(text):
#                     tags.attr(cls=type)
#     return result

# return True if updated
# def update_values_for_href(child, href):
#     values = subjects_db.get(href)
#     # TODO: support showing more than 1 result
#     if values is None:
#         return False
#     if len(values) == 1:
#         _, _, url = values[0]
#         child.children[0]['href'] = url
#         return True
#     elif len(values) > 1:
#         # # tuple of (subject, html_doc's section name, url)
#         # subject, section, url = values[]
#         child.children[0]['href'] = "search.html?method=exact_subject&term=" + href
#         return True
#     else:
#         assert False


# def update_href_no_link(child):
#     assert len(child.children[0].children) == 1
#     text = html.unescape(child.children[0].children[0])
#     child.children[0] = tags.span(text)


# def fix_links(html_docs_l):
#     # fix outbound links
#     print("Fixing links")
#     for (doc) in html_docs_l:
#         for (parent) in doc.body.children[0].children:
#             for middle in parent.children:
#                 try:
#                     for child in middle.children:
#                         if 'definition' in child.attributes.get('class', ()):
#                             href = ""
#                             try:
#                                 href = child.children[0].attributes.get("href")
#                             except AttributeError as e:
#                                 pass
#
#                             # it's a link - try to update it
#                             if href:
#                                 # first, strip it of weird chars
#                                 try:
#                                     href = clean_name(href)
#
#                                     updated = False
#                                     if update_values_for_href(child, href):
#                                         updated = True
#                                     else:
#                                         if href[0] in ("ה", "ו", "ש", "ב", "כ", "ל", "מ"):
#                                             updated = update_values_for_href(child, href[1:])
#                                     if not updated:
#                                         # failed to update - it's not a real link...
#                                         update_href_no_link(child)
#
#                                 except Exception as e:
#                                     pass
#                                     print(e, "Exception of HREF update", href)
#                                     # TODO - investigate why it happens? (it's a single corner case, I think)
#                 except AttributeError:
#                     pass
#
#     def sorter(html_doc):
#         if html_doc.name in ["ערכים כלליים", ]:
#             return "FIRST"
#         if html_doc.name in ["נספחות", ]:
#             return "תתתתתתתתתת"  # last
#         else:
#             return html_doc.name
#
#     # update sections menu
#     for (doc) in html_docs_l:
#         letters_l = []
#
#         content_menu = doc.body.children[0].children[1].children[0].children[-1].children[-1]
#         assert content_menu['class'] == 'dropdown-menu dropdown-menu-left scrollable-menu'
#
#         with content_menu:
#             with tags.li():
#                 tags.a("אודות", href="index.html")
#             with tags.li():
#                 tags.a("הקדמות", href="opening_intros.html")
#             with tags.li():
#                 tags.a("הסכמות", href="opening_haskamot.html")
#             with tags.li():
#                 tags.a("קיצורים", href="opening_abbrev.html")
#             with tags.li():
#                 tags.a("סימנים", href="opening_signs.html")
#             # if you add more entries here, please update add_menu_to_apriory_htmls(..)
#             with tags.li():
#                 tags.attr(cls="divider")
#
#             sorted_html_docs_l = sorted(html_docs_l, key=sorter)
#
#             for (html_doc) in sorted_html_docs_l:
#                 # Only if this a 'high' heading, and not just a letter - include it in the TOC
#                 if html_doc.name != "NEW_LETTER":
#                     with tags.li():
#                         tags.a(html_doc.name, href=str(html_doc.index) + ".html")
#                         if doc.section == html_doc.section:
#                             tags.attr(cls="active")
#                 else:
#                     # it's a letter - if it's related to me, save it
#                     if doc.section == html_doc.section:
#                         letters_l.append(html_doc)
#
#         with doc.body.children[-1]:
#             assert doc.body.children[-1]['class'] == 'container-fluid'
#             with tags.ul():
#                 tags.attr(cls="pagination")
#                 for (html_doc) in letters_l:
#                     tags.li(tags.a(html_doc.letter, href=str(html_doc.index) + ".html"))
#
#     return html_docs_l


# new_lines_in_raw = 0


# def add_running_tag(body, running_tag):
#     if str(running_tag) != "<span></span>":
#         search_index.learn(running_tag, html_doc)
#         body += running_tag
#     return (body, tags.span())


# def add_to_output(html_doc, para):
#     global new_lines_in_raw
#     global running_tag
#     # we shouldn't accept empty paragraph (?)
#     assert len(para) > 0
#
#     body = html_doc.body.children[-1]
#     assert body['class'] == 'container-fluid';
#     for (i, (type, text)) in enumerate(para):
#         if 'heading' in type and text.strip():
#             # tags.p()
#             # tags.p()
#             body, running_tag = add_running_tag(body, running_tag)
#             heading = sizes.get_heading_type(type)
#             print(type, text)
#             body += heading(text)
#         elif type == "new_line":
#             new_lines_in_raw += 1
#             if new_lines_in_raw == 1:
#                 running_tag += tags.br()
#             elif new_lines_in_raw == 2:
#                 body, running_tag = add_running_tag(body, running_tag)
#                 body += tags.p()
#             else:
#                 pass
#         elif is_subject(para, i):
#             if not is_prev_subject(para, i):
#                 # tags.p()
#                 # tags.br()
#                 pass
#
#             body, running_tag = add_running_tag(body, running_tag)
#             running_tag = subject(html_doc, type, text)
#         else:
#             running_tag += regular(type, text)
#
#         if type != "new_line":
#             new_lines_in_raw = 0
#
#     # tags.br()
#     # body, running_tag = add_running_tag(body, running_tag)	#TODO make sure it's not missing...
