import sublime, sublime_plugin
import re
import PelicanPluginTools

class PelicanUpdateDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        date_region = self.view.find(':?date:\s*', 0)
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
        new_view.run_command('pelican_insert_metadata', {"select_metadata": False, "meta_type": "md"})

class PelicanNewRestructuredtextCommand(sublime_plugin.WindowCommand):
    def run(self):
        new_view = self.window.new_file()
        PelicanPluginTools.addPelicanArticle(new_view)
        new_view.run_command('pelican_insert_metadata', {"select_metadata": False, "meta_type": "rst"})

class PelicanSelectMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode = "single"):
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

        if mode == "single":
            if len(self.view.sel()) > 0:
                region_begin = self.view.sel()[0].begin()
                region_end = self.view.sel()[len(self.view.sel())-1].end()
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(region_begin, region_end))
        elif mode == "multiple":
            pass # already selected
        elif mode == "at_the_end":
            if len(self.view.sel()) > 0:
                region_end = self.view.sel()[len(self.view.sel())-1].end()
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(region_end, region_end))

        self.view.show(self.view.sel())

class PelicanInsertMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_metadata = True, meta_type = None):
        if meta_type is None:
            meta_type = PelicanPluginTools.detect_article_type(self.view)

        article_metadata_template_keys = []
        article_metadata_template_lines = PelicanPluginTools.load_article_metadata_template_lines(self.view, meta_type)
        if article_metadata_template_lines:
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
            metadata["date"] = PelicanPluginTools.strDateNow()

        article_metadata_template = PelicanPluginTools.normalize_line_endings(self.view, "\n".join(article_metadata_template_lines))
        article_metadata_str = article_metadata_template % metadata
        if len(self.view.sel()) > 0:
            self.view.replace(edit, old_metadata_region, article_metadata_str)
        else:
            self.view.insert(edit, 0, article_metadata_str)

        force_slug_regeneration = PelicanPluginTools.load_setting(self.view, "force_slug_regeneration", False)
        if force_slug_regeneration or len(metadata["slug"]) is 0:
            self.view.run_command('pelican_generate_slug')

        if select_metadata:
            self.view.run_command('pelican_select_metadata')
