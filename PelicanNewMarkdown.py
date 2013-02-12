import sublime, sublime_plugin

class PelicanNewMarkdownCommand(sublime_plugin.TextCommand):
    template = (
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
    )

    def run(self, edit):
        self.view.insert(edit, 0, self.template)

