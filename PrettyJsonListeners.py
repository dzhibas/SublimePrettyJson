import sublime
import sublime_plugin

try:
    # python 3 / Sublime Text 3
    from .PrettyJson import PrettyJsonBaseCommand
except ValueError:
    from PrettyJson import PrettyJsonBaseCommand


class PrettyJsonLintListener(sublime_plugin.EventListener, PrettyJsonBaseCommand):
    def on_post_save(self, view):
        # will work only in json syntax
        if "JSON" in view.settings().get('syntax'):
            self.view = view

            self.view.erase_regions('json_errors')
            self.view.erase_status('json_errors')

            json_content = self.view.substr(sublime.Region(0, view.size()))

            try:
                self.json_loads(json_content)
            except Exception:
                self.show_exception()