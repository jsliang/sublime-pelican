import sublime, sublime_plugin

class PelicanInsertMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
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
        self.view.insert(edit, 0, template)


class PelicanInsertRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        template = (
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
        self.view.insert(edit, 0, template)

