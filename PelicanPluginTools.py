import sublime, sublime_plugin
import datetime

global_settings = sublime.load_settings("Pelican.sublime-settings")

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
    if view.find("^:\w+:", 0):
        return "rst"
    return "md"