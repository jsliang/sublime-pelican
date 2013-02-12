import sublime, sublime_plugin

pelican_template = {
    "md":
        (
        "title: \n"
        "date: \n"
        "tags: \n"
        "category: \n"
        "slug: \n"
        "author: \n"
        "lang: en\n"
        "summary: \n"
        "\n"
        "This is the content of my super blog post.\n\n"
        ),
    "rst":
        (
        ":title: \n"
        ":date: \n"
        ":tags: \n"
        ":category: \n"
        ":slug: \n"
        ":author: \n"
        ":lang: en\n"
        ":summary: \n"
        "\n"
        "This is the content of my super blog post.\n\n"
        )
}

class PelicanNewMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_template["md"])


class PelicanNewRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_template["rst"])

class PelicanInsertMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_template["md"])


class PelicanInsertRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, pelican_template["rst"])
