# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import re
import threading
import PelicanPluginTools

class PelicanUpdateDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        date_region = self.view.find(':?date:\s*', 0, sublime.IGNORECASE)
        if not date_region:
            return

        old_datestr_region = sublime.Region(date_region.end(), self.view.line(date_region).end())
        self.view.replace(edit, old_datestr_region, PelicanPluginTools.strDateNow())

        new_datestr_region = sublime.Region(date_region.end(), self.view.line(date_region).end())
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

            regex = re.compile(":?title:(?P<title>.+)\s*",re.IGNORECASE)
            r = regex.search(orig_title_str)
            if not r:
                return

            title_str = r.groupdict()['title'].strip()

            slug = self.slugify(title_str)

            meta_type = PelicanPluginTools.detect_article_type(self.view)

            pelican_slug_template = PelicanPluginTools.normalize_line_endings(self.view, PelicanPluginTools.pelican_slug_template[meta_type])
            slug_region = self.view.find(':?slug:.+\s*', 0, sublime.IGNORECASE)
            if slug_region:
                self.view.replace(edit, slug_region, pelican_slug_template % slug)
            else:
                slug_insert_position = title_region.end()
                self.view.insert(edit, slug_insert_position, pelican_slug_template % slug)


class PelicanNewMarkdownCommand(sublime_plugin.WindowCommand):
    def run(self):
        new_view = self.window.new_file()
        PelicanPluginTools.addPelicanArticle(new_view)
        new_view.run_command('pelican_insert_metadata', {"meta_type": "md"})

class PelicanNewRestructuredtextCommand(sublime_plugin.WindowCommand):
    def run(self):
        new_view = self.window.new_file()
        PelicanPluginTools.addPelicanArticle(new_view)
        new_view.run_command('pelican_insert_metadata', {"meta_type": "rst"})

class PelicanSelectMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode = "single"):
        self.view.sel().clear()
        metadata_regions = PelicanPluginTools.get_metadata_regions(self.view, mode)
        for region in metadata_regions:
            self.view.sel().add(region)
        self.view.show(self.view.sel())

class PelicanInsertMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, meta_type = None):
        if meta_type is None:
            meta_type = PelicanPluginTools.detect_article_type(self.view)

        article_metadata_template_keys = []
        article_metadata_template_lines = PelicanPluginTools.load_article_metadata_template_lines(self.view, meta_type)
        article_metadata_template_lines = PelicanPluginTools.normalize_article_metadata_case(article_metadata_template_lines)
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

        metadata_regions = PelicanPluginTools.get_metadata_regions(self.view, "multiple")
        if len(metadata_regions) > 0:
            for region in metadata_regions:
                metadata_str = self.view.substr(region)
                metadata_str = PelicanPluginTools.normalize_article_metadata_case(metadata_str)[0]
                regex = re.compile(":?(\w+):(.*)")
                find_all = regex.findall(metadata_str)
                if len(find_all) > 0:
                    for (field_name, field_value) in find_all:
                        field_data = ( field_name.strip(), field_value.strip() )
                        if not field_name in metadata:
                            new_meta = "%s: %s" % field_data
                            if meta_type is "rst":
                                new_meta = ":" + new_meta
                            article_metadata_template_lines.append(new_meta)
                        metadata[field_name] = field_value.strip()

            old_metadata_begin = metadata_regions[0].begin()
            old_metadata_end = metadata_regions[len(metadata_regions) - 1].end()
            old_metadata_region = sublime.Region(old_metadata_begin, old_metadata_end)

        # initialize date field if it's empty
        metadata_key_date = "Date"
        for key in metadata.keys():
            if key.lower() == "date":
                metadata_key_date = key
        if metadata[metadata_key_date] is "":
            metadata[metadata_key_date] = PelicanPluginTools.strDateNow()

        e = self.view.begin_edit()
        article_metadata_template = PelicanPluginTools.normalize_line_endings(self.view, "\n".join(article_metadata_template_lines))
        article_metadata_str = article_metadata_template % metadata
        if len(metadata_regions) > 0:
            self.view.replace(e, old_metadata_region, article_metadata_str)
        else:
            self.view.insert(e, 0, article_metadata_str)
        self.view.end_edit(e)

        # initialize slug field if it's empty
        metadata_key_slug = "Slug"
        for key in metadata.keys():
            if key.lower() == "slug":
                metadata_key_slug = key
        force_slug_regeneration = PelicanPluginTools.load_setting(self.view, "force_slug_regeneration", False)
        if force_slug_regeneration or len(metadata[metadata_key_slug]) is 0:
            self.view.run_command('pelican_generate_slug')

        # scroll to top
        self.view.show(0)

class PelicanInsertTagCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        articles_paths = PelicanPluginTools.get_article_paths(window=self.view.window())
        thread = PelicanInsertTagCategoryThread(self, articles_paths, "tag")
        thread.start()

class PelicanInsertCategoryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        articles_paths = PelicanPluginTools.get_article_paths(window=self.view.window())
        thread = PelicanInsertTagCategoryThread(self, articles_paths, "category")
        thread.start()

class PelicanInsertTagCategoryThread(threading.Thread):
    def __init__(self, txtcmd, article_paths, mode):
        self.window = txtcmd.view.window()
        self.view = txtcmd.view
        self.article_paths = article_paths
        self.mode = mode
        threading.Thread.__init__(self)

    def get_content_region(self):
        meta_type = PelicanPluginTools.detect_article_type(self.view)

        if self.mode == "tag":
            region = self.view.find('tags:', 0, sublime.IGNORECASE)
            template = PelicanPluginTools.normalize_line_endings(self.view, PelicanPluginTools.pelican_tags_template[meta_type])
        else:
            region = self.view.find('category:', 0, sublime.IGNORECASE)
            template = PelicanPluginTools.normalize_line_endings(self.view, PelicanPluginTools.pelican_categories_template[meta_type])

        if not region:
            self.view.run_command('pelican_select_metadata', {'mode': 'single'})

            insert_position = self.view.sel()[0].end()
            edit = self.view.begin_edit()
            self.view.insert(edit, insert_position, template)
            self.view.end_edit(edit)

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
            current_entries = [ x.strip() for x in old_content_str.split(',') ]

            if not picked_str in current_entries:
                current_entries.append(picked_str)

            if '' in current_entries:
                current_entries.remove('')

            new_content_str = ", ".join(current_entries)
        else:
            new_content_str = picked_str

        new_content_str = " " + new_content_str

        edit = self.view.begin_edit()
        self.view.replace(edit, self.view.sel()[0], new_content_str)
        self.view.end_edit(edit)

        content_line = self.view.line(self.view.sel()[0])

        self.view.sel().clear()
        self.view.sel().add(content_line)
        self.view.show(content_line)

    def run(self):
        self.results = PelicanPluginTools.get_categories_tags(self.article_paths, mode = self.mode)

        def show_quick_panel():
            if not self.results:
                sublime.error_message(('%s: There is no %s found.') % (__name__, self.mode))
                return
            self.window.show_quick_panel(self.results, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)
