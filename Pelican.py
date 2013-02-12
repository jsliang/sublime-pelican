
import sublime, sublime_plugin
import re

import unicodedata

pelican_meta_template = {
    "md":
        (
        "title: \n"
        "date: \n"
        "tags: \n"
        "category: \n"
        "author: \n"
        "lang: en\n"
        "summary: \n"
        "\n"
        ),
    "rst":
        (
        ":title: \n"
        ":date: \n"
        ":tags: \n"
        ":category: \n"
        ":author: \n"
        ":lang: en\n"
        ":summary: \n"
        "\n"
        )
}

pelican_slug_template = {
    "md": "slug: %s\n",
    "rst": ":slug: %s\n",
}

class PelicanGenerateSlugCommand(sublime_plugin.TextCommand):
    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.

        Took from django sources.
        """
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        # we want only ASCII chars
        value = value.encode('ascii', 'ignore')
        # but Pelican should generally use only unicode
        return value.decode('ascii')

    def run(self, edit):
        title_region = self.view.find(':?title:.+\s*', 0, sublime.IGNORECASE)
        if title_region > -1:
            title_str = self.view.substr(title_region).strip()

            regex = re.compile(":?title:(?P<title>.+)\s*",re.IGNORECASE)
            r = regex.search(title_str)
            title_str = r.groupdict()['title'].strip()

            slug = self.slugify(title_str)

            if re.search("rst", self.view.file_name()):
                meta_type = "rst"
            else:
                meta_type = "md"

            slug_insert_position = title_region.end()
            self.view.insert(edit, slug_insert_position, pelican_slug_template[meta_type] % slug)


class PelicanAutogenSlug(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        global_settings = sublime.load_settings(__name__ + '.sublime-settings')

        auto_generate_slug = view.settings().get('auto_generate_slug', global_settings.get('auto_generate_slug', '*'))
        if not auto_generate_slug is 1:
            return

        filename_filter = view.settings().get('filename_filter', global_settings.get('filename_filter', '*'))
        if not re.search(filename_filter, view.file_name()):
            return

        if view.find(':?slug:\s*\w+', 0, sublime.IGNORECASE) > -1:
            return

        view.run_command('pelican_generate_slug' )

class PelicanNewMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["md"])


class PelicanNewRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["rst"])

class PelicanInsertMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_meta_template["md"])


class PelicanInsertRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_meta_template["rst"])
