
import sublime, sublime_plugin
import re

import datetime

pelican_meta_template = {
    "md":
        (
        "title: \n"
        "date: %(date)s\n"
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
        ":date: %(date)s\n"
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

def strDateNow():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")


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
        slug_region = self.view.find(':?slug:.+\s*', 0, sublime.IGNORECASE)
        if slug_region > -1:
            self.view.erase(edit, slug_region)

        title_region = self.view.find(':?title:.+\s*', 0, sublime.IGNORECASE)
        if title_region > -1:
            orig_title_str = self.view.substr(title_region).strip()

            regex = re.compile(":?title:(?P<title>.+)\s*",re.IGNORECASE)
            r = regex.search(orig_title_str)
            if not r:
                return

            title_str = r.groupdict()['title'].strip()

            slug = self.slugify(title_str)

            if re.search(":title:", orig_title_str, re.IGNORECASE):
                meta_type = "rst"
            else: # "title: ..."
                meta_type = "md"

            slug_insert_position = title_region.end()
            self.view.insert(edit, slug_insert_position, pelican_slug_template[meta_type] % slug)


class PelicanAutogenSlug(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        global_settings = sublime.load_settings(__name__ + '.sublime-settings')

        auto_generate_slug_on_save = view.settings().get('auto_generate_slug_on_save', global_settings.get('auto_generate_slug_on_save', '*'))
        if not auto_generate_slug_on_save:
            return

        article_filename_filter = view.settings().get('article_filename_filter', global_settings.get('article_filename_filter', '*'))
        if not re.search(article_filename_filter, view.file_name()):
            return

        if view.find(':?slug:\s*\w+', 0, sublime.IGNORECASE) > -1:
            force_slug_regeneration_on_save = view.settings().get('force_slug_regeneration_on_save', global_settings.get('force_slug_regeneration_on_save', '*'))
            if not force_slug_regeneration_on_save:
                return

        view.run_command('pelican_generate_slug' )

class PelicanNewMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["md"] % {"date": strDateNow()})

class PelicanNewRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["rst"] % {"date": strDateNow()})

class PelicanInsertMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_meta_template["md"] % {"date": strDateNow()})


class PelicanInsertRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_meta_template["rst"] % {"date": strDateNow()})
