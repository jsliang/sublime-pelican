import sublime, sublime_plugin
import re

import datetime

pelican_slug_template = {
    "md": "slug: %s\n",
    "rst": ":slug: %s\n",
}

def strDateNow():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from django sources.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value

class PelicanTools():
    _singleton_instance = None

    def __new__(cls):
        if not cls._singleton_instance:
            cls._singleton_instance = super(PelicanTools, cls).__new__()
        return cls._singleton_instance

    def __init__(self):
        self.global_settings = sublime.load_settings(__name__ + '.sublime-settings')

    def load_setting(self, view, setting_name, default_value):
        if len(setting_name) < 1:
            if default_value:
                return default_value
            return None

        return view.settings().get(setting_name, self.global_settings.get(setting_name, default_value))

    def normalize_line_endings(self, view, string):
        string = string.replace('\r\n', '\n').replace('\r', '\n')
        line_endings = self.load_setting(view, 'default_line_ending', 'unix')
        if line_endings == 'windows':
            string = string.replace('\n', '\r\n')
        elif line_endings == 'mac':
            string = string.replace('\n', '\r')
        return string

    def load_article_metadata_template_lines(self, view, meta_type = None):
        if meta_type is None:
            meta_type = self.detect_article_type(view)

        article_metadata_template = self.load_setting(view, "article_metadata_template", {})
        if not article_metadata_template or len(article_metadata_template) < 1:
            return

        return article_metadata_template[meta_type]

    def load_article_metadata_template_str(self, view, meta_type = None):
        if meta_type is None:
            meta_type = self.detect_article_type(view)

        article_metadata_template = self.load_article_metadata_template_lines(view, meta_type)
        return self.normalize_line_endings(view, "\n".join(article_metadata_template))

    def detect_article_type(self, view):
        if view.find("^:\w+:", 0):
            return "rst"
        return "md"

class PelicanUpdateDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print "PelicanUpdateDateCommand"
        date_region = self.view.find(':?date:\s*', 0)
        print date_region
        if not date_region:
            return

        old_datestr_region = sublime.Region(date_region.end(), self.view.line(date_region).end())
        self.view.replace(edit, old_datestr_region, strDateNow())

        new_datestr_region = sublime.Region(date_region.end(), self.view.line(date_region).end())
        self.view.sel().clear()
        self.view.sel().add(new_datestr_region)

        self.view.show(new_datestr_region)

class PelicanGenerateSlugCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        slug_region = self.view.find(':?slug:.+\s*', 0, sublime.IGNORECASE)
        if slug_region:
            self.view.erase(edit, slug_region)

        title_region = self.view.find(':?title:.+\s*', 0, sublime.IGNORECASE)
        if title_region:
            orig_title_str = self.view.substr(title_region).strip()

            regex = re.compile(":?title:(?P<title>.+)\s*",re.IGNORECASE)
            r = regex.search(orig_title_str)
            if not r:
                return

            title_str = r.groupdict()['title'].strip()

            pelican_tools = PelicanTools()

            slug = slugify(title_str)

            meta_type = pelican_tools.detect_article_type(self.view)

            slug_insert_position = title_region.end()
            self.view.insert(edit, slug_insert_position, pelican_slug_template[meta_type] % slug)

class PelicanAutogenSlug(sublime_plugin.EventListener):
    def isInTitleLine(self, view):
        if len(view.sel()) > 0:
            current_line = view.line(view.sel()[0].begin())
            if view.find("title:", current_line.begin(), sublime.IGNORECASE):
                return True
        return False

    def isPelicanArticle(self, view):
        filepath_filter = pelican_tools.load_setting(view, "filepath_filter", '*')
        if re.search(filepath_filter, view.file_name()):
            return True
        return False

    def on_modified(self, view):
        pelican_tools = PelicanTools()

        generate_slug_from_title = pelican_tools.load_setting(view, "generate_slug_from_title", True)
        if generate_slug_from_title != "title_change":
            return

        if not self.isPelicanArticle(view):
            return

        if self.isInTitleLine(view):
            view.run_command('pelican_generate_slug')

    def on_pre_save(self, view):
        pelican_tools = PelicanTools()

        generate_slug_from_title = pelican_tools.load_setting(view, "generate_slug_from_title", True)
        if generate_slug_from_title != "save":
            return

        if not self.isPelicanArticle(view):
            return

        slug_region = view.find(':?slug:\s*.+', 0, sublime.IGNORECASE)
        if slug_region:
            slug_line = view.substr(view.line(slug_region.begin()))
            regex = re.compile(":?slug:(.*)",re.IGNORECASE)
            find_all = regex.findall(slug_line)
            if len(find_all) > 0:
                slug_str = find_all[0].strip()

                force_slug_regeneration = pelican_tools.load_setting(view, "force_slug_regeneration", False)
                if len(slug_str) > 0 and not force_slug_regeneration:
                    return

                edit = view.begin_edit()
                view.replace(edit, view.full_line(slug_region.begin()), "")
                view.end_edit(edit)

        view.run_command('pelican_generate_slug')

class PelicanNewMarkdownCommand(sublime_plugin.WindowCommand):
    def run(self):
        new_view = self.window.new_file()
        new_view.run_command('pelican_insert_metadata', {"select_metadata": False, "meta_type": "md"})

class PelicanNewRestructuredtextCommand(sublime_plugin.WindowCommand):
    def run(self):
        new_view = self.window.new_file()
        new_view.run_command('pelican_insert_metadata', {"select_metadata": False, "meta_type": "rst"})

class PelicanSelectMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().clear()

        metadata_regions = self.view.find_all(':?\w+:', 0)

        for i in range(0, len(metadata_regions)):
            region = metadata_regions[i]

            # select consecutive metadata lines at the beginning of the file
            if i > 0:
                prev_region = metadata_regions[i-1]
                prev_line_no, __ = self.view.rowcol(prev_region.begin())
                this_line_no, __ = self.view.rowcol(region.begin())

                if this_line_no - prev_line_no > 1:
                    break

            line_regions = self.view.lines(region)
            for line_region in line_regions:
                if not line_region.empty():
                    self.view.sel().add(line_region)

        self.view.show(self.view.sel())

class PelicanInsertMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_metadata = True, meta_type = None):
        pelican_tools = PelicanTools()

        if meta_type is None:
            if self.view.find("^:\w+:", 0):
                meta_type = "rst"
            else: # "title: ..."
                meta_type = "md"

        article_metadata_template_keys = []
        article_metadata_template_lines = pelican_tools.load_article_metadata_template_lines(self.view)
        for article_metadata_template_line in article_metadata_template_lines:
            regex = re.compile(":?(\w+):")
            find_all = regex.findall(article_metadata_template_line)
            if len(find_all) > 0:
                metadata_key = regex.findall(article_metadata_template_line)[0]
                if not metadata_key in article_metadata_template_keys:
                    article_metadata_template_keys.append(metadata_key)

        metadata = {}
        for article_metadata_template_key in article_metadata_template_keys:
            metadata[article_metadata_template_key] = ""

        self.view.run_command('pelican_select_metadata')
        if len(self.view.sel()) > 0:
            for sel in self.view.sel():
                metadata_str = self.view.substr(sel)
                regex = re.compile(":?(\w+):(.*)")
                find_all = regex.findall(metadata_str)
                if len(find_all) > 0:
                    (key, value) = find_all[0]
                    key = key.strip()
                    value = value.strip()
                    if not key in metadata:
                        new_meta = "%s: %s" % (key, value)
                        if meta_type is "rst":
                            new_meta = ":" + new_meta
                        article_metadata_template_lines.append(new_meta)
                    metadata[key] = value.strip()

            old_metadata_begin = self.view.sel()[0].begin()
            old_metadata_end = self.view.sel()[len(self.view.sel()) - 1].end()
            old_metadata_region = sublime.Region(old_metadata_begin, old_metadata_end)

        if metadata["date"] is "":
            metadata["date"] = strDateNow()

        article_metadata_template = pelican_tools.normalize_line_endings(self.view, "\n".join(article_metadata_template_lines))
        article_metadata_str = article_metadata_template % metadata
        if len(self.view.sel()) > 0:
            self.view.replace(edit, old_metadata_region, article_metadata_str)
        else:
            self.view.insert(edit, 0, article_metadata_str)

        force_slug_regeneration = pelican_tools.load_setting(self.view, "force_slug_regeneration", False)
        if force_slug_regeneration or len(metadata["slug"]) is 0:
            self.view.run_command('pelican_generate_slug')

        if select_metadata:
            self.view.run_command('pelican_select_metadata')
