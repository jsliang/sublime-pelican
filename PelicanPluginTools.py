import sublime, sublime_plugin
import datetime
import re

pelican_slug_template = {
    "md": "slug: %s\n",
    "rst": ":slug: %s\n",
}

global_settings = sublime.load_settings("Pelican.sublime-settings")

pelican_article_views = []

def addPelicanArticle(view):
    view_id = view.id()
    if not view_id in pelican_article_views:
        pelican_article_views.append(view_id)

def removePelicanArticle(view):
    view_id = view.id()
    if view_id in pelican_article_views:
        pelican_article_views.remove(view_id)

def isPelicanArticle(view):
    if view.id() in pelican_article_views:
        return True

    if view.file_name():
        filepath_filter = load_setting(view, "filepath_filter", '*')
        if re.search(filepath_filter, view.file_name()):
            return True

    return False

def strDateNow():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")

def load_setting(view, setting_name, default_value):
    if len(setting_name) < 1:
        if default_value:
            return default_value
        return None

    return view.settings().get(setting_name, global_settings.get(setting_name, default_value))

def normalize_line_endings(view, string):
    string = string.replace('\r\n', '\n').replace('\r', '\n')
    line_endings = load_setting(view, 'default_line_ending', 'unix')
    if line_endings == 'windows':
        string = string.replace('\n', '\r\n')
    elif line_endings == 'mac':
        string = string.replace('\n', '\r')
    return string

def load_article_metadata_template_lines(view, meta_type = None):
    if meta_type is None:
        meta_type = detect_article_type(view)

    article_metadata_template = load_setting(view, "article_metadata_template", {})
    if not article_metadata_template or len(article_metadata_template) < 1:
        return

    return article_metadata_template[meta_type]

def load_article_metadata_template_str(view, meta_type = None):
    if meta_type is None:
        meta_type = detect_article_type(view)

    article_metadata_template = load_article_metadata_template_lines(view, meta_type)
    return normalize_line_endings(view, "\n".join(article_metadata_template))

def detect_article_type(view):
    if isPelicanArticle(view) and view.file_name():
        if re.search("rst", view.file_name()):
            return "rst"
        return "md"

    if view.find("^:\w+:", 0):
        return "rst"
    return "md"