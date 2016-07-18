import sublime
import sublime_plugin

try:
    # python 3 / Sublime Text 3
    from .PrettyJson import PrettyJsonBaseCommand
except ValueError:
    from PrettyJson import PrettyJsonBaseCommand

s = sublime.load_settings("Pretty JSON.sublime-settings")


class PrettyJsonLintListener(sublime_plugin.EventListener, PrettyJsonBaseCommand):
    def on_post_save(self, view):
        # will work only in json syntax and once validate_on_save setting is true
        validate = s.get("validate_on_save", True)
        if validate and "JSON" in view.settings().get('syntax'):
            self.view = view

            self.view.erase_regions('json_errors')
            self.view.erase_status('json_errors')

            json_content = self.view.substr(sublime.Region(0, view.size()))

            try:
                self.json_loads(json_content)
            except Exception:
                self.show_exception()


class PrettyJsonAutoPrettyOnSaveListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        auto_pretty = s.get("pretty_on_save", False)
        if auto_pretty and "JSON" in view.settings().get('syntax'):
            sublime.active_window().run_command('pretty_json')
