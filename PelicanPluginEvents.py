import sublime, sublime_plugin
import re
import PelicanPluginTools

class PelicanArticleClose(sublime_plugin.EventListener):
    def on_close(self, view):
        PelicanPluginTools.removePelicanArticle(view)

class PelicanAutogenSlug(sublime_plugin.EventListener):
    def isInTitleLine(self, view):
        if len(view.sel()) > 0:
            current_line = view.line(view.sel()[0].begin())
            if view.find("title:", current_line.begin(), sublime.IGNORECASE):
                return True
        return False

    def on_modified(self, view):
        generate_slug_from_title = PelicanPluginTools.load_setting(view, "generate_slug_from_title", True)
        if generate_slug_from_title != "title_change":
            return

        if not PelicanPluginTools.isPelicanArticle(view):
            return

        if self.isInTitleLine(view):
            view.run_command('pelican_generate_slug')

    def on_pre_save(self, view):
        generate_slug_from_title = PelicanPluginTools.load_setting(view, "generate_slug_from_title", True)
        if generate_slug_from_title != "save":
            return

        if not PelicanPluginTools.isPelicanArticle(view):
            return

        slug_region = view.find(':?slug:\s*.+', 0, sublime.IGNORECASE)
        if slug_region:
            slug_line = view.substr(view.line(slug_region.begin()))
            regex = re.compile(":?slug:(.*)",re.IGNORECASE)
            find_all = regex.findall(slug_line)
            if len(find_all) > 0:
                slug_str = find_all[0].strip()

                force_slug_regeneration = PelicanPluginTools.load_setting(view, "force_slug_regeneration", False)
                if len(slug_str) > 0 and not force_slug_regeneration:
                    return

                edit = view.begin_edit()
                view.replace(edit, view.full_line(slug_region.begin()), "")
                view.end_edit(edit)

        view.run_command('pelican_generate_slug')
