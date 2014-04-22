# -*- coding: utf-8 -*-
import datetime
import os
import re
import sublime
import sublime_plugin
import sys
import threading

pelican_slug_template = {
    "md": "Slug: %s\n",
    "rst": ":slug: %s\n",
}

pelican_tags_template = {
    "md": "\nTags: ",
    "rst": "\n:tags: ",
}

pelican_categories_template = {
    "md": "\nCategory: ",
    "rst": "\n:category: ",
}

default_filter = '.*\\.(md|markdown|mkd|rst)$'

pelican_article_views = []


class PelicanUpdateDateCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        date_region = self.view.find(':?date:\s*', 0, sublime.IGNORECASE)
        if not date_region:
            return

        old_datestr_region = sublime.Region(
            date_region.end(), self.view.line(date_region).end())
        self.view.replace(
            edit, old_datestr_region, strDateNow())

        new_datestr_region = sublime.Region(
            date_region.end(), self.view.line(date_region).end())
        self.view.sel().clear()
        self.view.sel().add(new_datestr_region)

        self.view.show(new_datestr_region)


class PelicanGenerateSlugCommand(sublime_plugin.TextCommand):

    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.

        Took from django sources.
        """
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        return value

    def run(self, edit):
        title_region = self.view.find(':?title:.+\s*', 0, sublime.IGNORECASE)
        if title_region:
            orig_title_str = self.view.substr(title_region).strip()

            regex = re.compile(":?title:(?P<title>.+)\s*", re.IGNORECASE)
            r = regex.search(orig_title_str)
            if not r:
                return

            title_str = r.groupdict()['title'].strip()

            slug = self.slugify(title_str)

            meta_type = detect_article_type(self.view)

            pelican_slug_template_result = normalize_line_endings(
                self.view, pelican_slug_template[meta_type])
            slug_region = self.view.find(':?slug:.+\s*', 0, sublime.IGNORECASE)
            if slug_region:
                self.view.replace(
                    edit, slug_region, pelican_slug_template_result % slug)
            else:
                slug_insert_position = title_region.end()
                self.view.insert(
                    edit, slug_insert_position, pelican_slug_template_result % slug)


class PelicanNewMarkdownCommand(sublime_plugin.WindowCommand):

    def run(self):
        new_view = self.window.new_file()
        addPelicanArticle(new_view)
        new_view.run_command('pelican_insert_metadata', {"meta_type": "md"})


class PelicanNewRestructuredtextCommand(sublime_plugin.WindowCommand):

    def run(self):
        new_view = self.window.new_file()
        addPelicanArticle(new_view)
        new_view.run_command('pelican_insert_metadata', {"meta_type": "rst"})


class PelicanSelectMetadataCommand(sublime_plugin.TextCommand):

    def run(self, edit, mode="single"):
        self.view.sel().clear()
        metadata_regions = get_metadata_regions(self.view, mode)
        for region in metadata_regions:
            self.view.sel().add(region)
        self.view.show(self.view.sel())


class PelicanInsertMetadataCommand(sublime_plugin.TextCommand):

    def run(self, edit, meta_type=None):
        if meta_type is None:
            meta_type = detect_article_type(self.view)

        article_metadata_template_keys = []
        article_metadata_template_lines = load_article_metadata_template_lines(
            self.view, meta_type)
        article_metadata_template_lines = normalize_article_metadata_case(
            article_metadata_template_lines)
        if article_metadata_template_lines:
            for article_metadata_template_line in article_metadata_template_lines:
                regex = re.compile(":?(\w+):")
                find_all = regex.findall(article_metadata_template_line)
                if len(find_all) > 0:
                    metadata_key = find_all[0]
                    if not metadata_key in article_metadata_template_keys:
                        article_metadata_template_keys.append(metadata_key)

        metadata = {}
        for article_metadata_template_key in article_metadata_template_keys:
            metadata[article_metadata_template_key] = ""

        metadata_regions = get_metadata_regions(self.view, "multiple")
        if len(metadata_regions) > 0:
            for region in metadata_regions:
                metadata_str = self.view.substr(region)
                metadata_str = normalize_article_metadata_case(metadata_str)[0]
                regex = re.compile(":?(\w+):(.*)")
                find_all = regex.findall(metadata_str)
                if len(find_all) > 0:
                    for (field_name, field_value) in find_all:
                        field_data = (field_name.strip(), field_value.strip())
                        if not field_name in metadata:
                            new_meta = "%s: %s" % field_data
                            if meta_type is "rst":
                                new_meta = ":" + new_meta
                            article_metadata_template_lines.append(new_meta)
                        metadata[field_name] = field_value.strip()

            old_metadata_begin = metadata_regions[0].begin()
            old_metadata_end = metadata_regions[
                len(metadata_regions) - 1].end()
            old_metadata_region = sublime.Region(
                old_metadata_begin, old_metadata_end)

        # initialize date field if it's empty
        metadata_key_date = "Date"
        for key in metadata.keys():
            if key.lower() == "date":
                metadata_key_date = key
        if metadata[metadata_key_date] is "":
            metadata[metadata_key_date] = strDateNow()

        article_metadata_template = normalize_line_endings(
            self.view, "\n".join(article_metadata_template_lines))
        article_metadata_str = article_metadata_template % metadata
        if len(metadata_regions) > 0:
            self.view.replace(edit, old_metadata_region, article_metadata_str)
        else:
            self.view.insert(edit, 0, article_metadata_str)

        # initialize slug field if it's empty
        metadata_key_slug = "Slug"
        for key in metadata.keys():
            if key.lower() == "slug":
                metadata_key_slug = key
        force_slug_regeneration = load_setting(
            self.view, "force_slug_regeneration", False)
        if force_slug_regeneration or len(metadata[metadata_key_slug]) is 0:
            self.view.run_command('pelican_generate_slug')

        # scroll to top
        self.view.show(0)


class PelicanInsertTagCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        articles_paths = get_article_paths(window=self.view.window())
        thread = PelicanInsertTagCategoryThread(self, articles_paths, "tag")
        thread.start()


class PelicanInsertCategoryCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        articles_paths = get_article_paths(window=self.view.window())
        thread = PelicanInsertTagCategoryThread(
            self, articles_paths, "category")
        thread.start()


class PelicanInsertTagCategoryThread(threading.Thread):

    def __init__(self, txtcmd, article_paths, mode):
        self.window = txtcmd.view.window()
        self.view = txtcmd.view
        self.article_paths = article_paths
        self.mode = mode
        threading.Thread.__init__(self)

    def get_content_region(self):
        meta_type = detect_article_type(self.view)

        if self.mode == "tag":
            region = self.view.find('tags:', 0, sublime.IGNORECASE)
            template = normalize_line_endings(
                self.view, pelican_tags_template[meta_type])
        else:
            region = self.view.find('category:', 0, sublime.IGNORECASE)
            template = normalize_line_endings(
                self.view, pelican_categories_template[meta_type])

        if not region:
            self.view.run_command(
                'pelican_select_metadata', {'mode': 'single'})

            insert_position = self.view.sel()[0].end()
            self.view.insert(edit, insert_position, template)

            if self.mode == "tag":
                region = self.view.find('tags:', 0, sublime.IGNORECASE)
            else:
                region = self.view.find('category:', 0, sublime.IGNORECASE)

        content_start = region.end()
        content_end = self.view.line(region).end()
        content_region = sublime.Region(content_start, content_end)

        return content_region

    def on_done(self, picked):
        if picked == -1:
            return

        picked_str = self.results[picked]

        old_content_region = self.get_content_region()
        old_content_str = self.view.substr(old_content_region)

        self.view.sel().clear()
        self.view.sel().add(old_content_region)

        if len(old_content_str) > 0 and self.mode == "tag":
            current_entries = [x.strip() for x in old_content_str.split(',')]

            if not picked_str in current_entries:
                current_entries.append(picked_str)

            if '' in current_entries:
                current_entries.remove('')

            new_content_str = ", ".join(current_entries)
        else:
            new_content_str = picked_str

        new_content_str = " " + new_content_str

        self.view.replace(edit, self.view.sel()[0], new_content_str)

        content_line = self.view.line(self.view.sel()[0])

        self.view.sel().clear()
        self.view.sel().add(content_line)
        self.view.show(content_line)

    def run(self):
        self.results = get_categories_tags(self.article_paths, mode=self.mode)

        def show_quick_panel():
            if not self.results:
                sublime.error_message(
                    ('%s: There is no %s found.') % (__name__, self.mode))
                return
            self.window.show_quick_panel(self.results, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)


class PelicanArticleClose(sublime_plugin.EventListener):

    def on_close(self, view):
        removePelicanArticle(view)


class PelicanAutogenSlug(sublime_plugin.EventListener):

    def isInTitleLine(self, view):
        if len(view.sel()) > 0:
            current_line = view.line(view.sel()[0].begin())
            if view.find("title:", current_line.begin(), sublime.IGNORECASE):
                return True
        return False

    def on_modified(self, view):
        generate_slug_from_title = load_setting(
            view, "generate_slug_from_title", True)
        if generate_slug_from_title != "title_change":
            return

        if not isPelicanArticle(view):
            return

        if self.isInTitleLine(view):
            view.run_command('pelican_generate_slug')

    def on_pre_save(self, view):
        generate_slug_from_title = load_setting(
            view, "generate_slug_from_title", True)
        if generate_slug_from_title != "save":
            return

        if not isPelicanArticle(view):
            return

        slug_region = view.find(':?slug:\s*.+', 0, sublime.IGNORECASE)
        if slug_region:
            slug_line = view.substr(view.line(slug_region.begin()))
            regex = re.compile(":?slug:(.*)", re.IGNORECASE)
            find_all = regex.findall(slug_line)
            if len(find_all) > 0:
                slug_str = find_all[0].strip()

                if len(slug_str) > 0:
                    force_slug_regeneration = load_setting(
                        view, "force_slug_regeneration", False)
                    if not force_slug_regeneration:
                        return

        view.run_command('pelican_generate_slug')

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


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
        filepath_filter = load_setting(view, "filepath_filter", default_filter)

        use_input_folder_in_makefile = load_setting(
            view, "use_input_folder_in_makefile", True)
        if use_input_folder_in_makefile:
            makefile_params = parse_makefile(view.window())
            if makefile_params and "INPUTDIR" in makefile_params:
                filepath_filter = makefile_params[
                    'INPUTDIR'] + "/" + default_filter

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

    global_settings = sublime.load_settings("Pelican.sublime-settings")

    return view.settings().get(setting_name, global_settings.get(setting_name, default_value))


def normalize_line_endings(view, string):
    string = string.replace('\r\n', '\n').replace('\r', '\n')
    line_endings = load_setting(view, 'default_line_ending', 'unix')
    if line_endings == 'windows':
        string = string.replace('\n', '\r\n')
    elif line_endings == 'mac':
        string = string.replace('\n', '\r')
    return string


def load_article_metadata_template_lines(view, meta_type=None):
    if meta_type is None:
        meta_type = detect_article_type(view)

    article_metadata_template = load_setting(
        view, "article_metadata_template", {})
    if not article_metadata_template or len(article_metadata_template) < 1:
        return

    return article_metadata_template[meta_type]


def load_article_metadata_template_str(view, meta_type=None):
    if meta_type is None:
        meta_type = detect_article_type(view)

    article_metadata_template = load_article_metadata_template_lines(
        view, meta_type)
    return normalize_line_endings(view, "\n".join(article_metadata_template))


def detect_article_type(view):
    if isPelicanArticle(view) and view.file_name():
        if re.search("rst", view.file_name()):
            return "rst"
        return "md"

    if view.find("^:\w+:", 0):
        return "rst"
    return "md"


def parse_makefile(window):
    makefile_path = None
    current_filename = window.active_view().file_name()
    current_folder = os.path.dirname(current_filename)
    current_folders = window.folders()
    for folder in current_folders:
        if folder in current_folder:
            break
    makefile_dir = folder
    makefile_path = os.path.join(makefile_dir, "Makefile")
    if not os.path.exists(makefile_path):
        return None

    # parse parameters in Makefile
    regex = re.compile("(\S+)=(.*)")
    makefile_content = ""
    with open(makefile_path, 'r') as f:
        makefile_content = f.read()

    if len(makefile_content) > 0:
        origin_makefile_params = []
        origin_makefile_params = regex.findall(makefile_content)

        if len(origin_makefile_params) > 0:

            makefile_params = {"CURDIR": makefile_dir}

            for (key, value) in origin_makefile_params:
                if not key in makefile_params:
                    # replace "$(var)" to "%(var)s"
                    value = re.sub(r"\$\((\S+)\)", r"%(\1)s", value)

                    makefile_params[key] = value % makefile_params

            return makefile_params
    return None


def get_article_paths(window):
    article_paths = []

    # load INPUTDIR
    inputdir = None
    makefile_params = parse_makefile(window)
    if makefile_params and "INPUTDIR" in makefile_params:
        inputdir = makefile_params['INPUTDIR']
    else:
        return []

    # get paths of all articles in INPUTDIR
    inputdir_structure = os.walk(inputdir)
    if inputdir_structure:
        for (dirpath, dirnames, filenames) in inputdir_structure:
            for filename in filenames:
                article_path = os.path.join(dirpath, filename)
                if re.search(default_filter, article_path):
                    article_paths.append(article_path)
    else:
        return []

    return article_paths


def get_categories_tags(articles_paths, mode="tag"):
    # retrieve categories or tags
    results = []
    for article_path in articles_paths:
        if mode == "category":
            regex = re.compile("category:(.*)", re.IGNORECASE)
        else:
            regex = re.compile("tags:(.*)", re.IGNORECASE)

        with open(article_path) as f:
            content_str = f.read()

        regex_results = regex.findall(content_str)
        if len(regex_results) > 0:
            for result in regex_results:
                results.extend([x.strip() for x in result.split(",")])

    if len(results) == 0:
        return None

    list_results = sorted(list(set(results)))
    if '' in list_results:
        list_results.remove('')

    return list_results


def get_metadata_regions(view, mode):
    metadata_regions = view.find_all(':?\w+:', 0)

    regions = []
    for i in range(0, len(metadata_regions)):
        region = metadata_regions[i]

        # select consecutive metadata lines at the beginning of the file
        if i > 0:
            prev_region = metadata_regions[i - 1]
            prev_line_no, __ = view.rowcol(prev_region.begin())
            this_line_no, __ = view.rowcol(region.begin())

            if this_line_no - prev_line_no > 1:
                break

        line_regions = view.lines(region)
        for line_region in line_regions:
            if (not line_region.empty()) and (not line_region in regions):
                regions.append(line_region)

    result_region_list = []
    if mode == "single":
        if len(regions) > 0:
            region_begin = regions[0].begin()
            region_end = regions[len(regions) - 1].end()
            result_region_list.append(sublime.Region(region_begin, region_end))
    elif mode == "multiple":
        for region in regions:
            result_region_list.append(region)
    elif mode == "at_the_end":
        if len(regions) > 0:
            region_end = regions[len(regions) - 1].end()
            result_region_list.append(sublime.Region(region_end, region_end))

    return result_region_list


def normalize_article_metadata_case(template_str, normalize_template_var=True):
    '''
    Markdown

    >>> template_str = "title: %(title)s"
    >>> print normalize_article_metadata_case(template_str)
    ['Title: %(Title)s']
    >>> print normalize_article_metadata_case(template_str, False)
    ['Title: %(title)s']

    >>> template_str = """
    ... title: %(title)s
    ... date: %(date)s
    ... slug: %(slug)s
    ... """
    >>> print normalize_article_metadata_case(template_str)
    ['Title: %(Title)s', 'Date: %(Date)s', 'Slug: %(Slug)s']
    >>> print normalize_article_metadata_case(template_str, False)
    ['Title: %(title)s', 'Date: %(date)s', 'Slug: %(slug)s']

    reStructuredText

    >>> template_str = ":TITLE: %(TITLE)s"
    >>> print normalize_article_metadata_case(template_str)
    [':title: %(title)s']
    >>> print normalize_article_metadata_case(template_str, False)
    [':title: %(TITLE)s']

    >>> template_str = """
    ... :TITLE: %(TITLE)s
    ... :DATE: %(DATE)s
    ... :SLUG: %(SLUG)s
    ... """
    >>> print normalize_article_metadata_case(template_str)
    [':title: %(title)s', ':date: %(date)s', ':slug: %(slug)s']
    >>> print normalize_article_metadata_case(template_str, False)
    [':title: %(TITLE)s', ':date: %(DATE)s', ':slug: %(SLUG)s']
    '''

    new_str_lines = []
    if not isinstance(template_str, list):
        template_str = template_str.replace(
            '\r\n', '\n').replace('\r', '\n').split('\n')
    regex_key = re.compile(":?(\w+):")
    regex_var = re.compile("%\((\w+)\)s")

    for line in template_str:
        isMD = True
        regex = re.compile("^:\w+:")
        if len(regex.findall(line)) > 0:
            isMD = False

        find_all = regex_key.findall(line)
        if len(find_all) > 0:
            template_key = find_all[0]
            if isMD:
                new_template_key = template_key.strip().capitalize()
            else:
                new_template_key = template_key.strip().lower()
            new_line = line.replace(
                "%s:" % template_key, "%s:" % new_template_key)

            if normalize_template_var:
                find_all = regex_var.findall(line)
                if len(find_all) > 0:
                    template_var = find_all[0]
                    if isMD:
                        new_template_var = template_var.strip().capitalize()
                    else:
                        new_template_var = template_var.strip().lower()
                    new_line = new_line.replace(
                        "%(" + template_var + ")s", "%(" + new_template_var + ")s")

            new_str_lines.append(new_line)
    return new_str_lines
