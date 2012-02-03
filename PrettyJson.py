import sublime
import sublime_plugin
import json


class PrettyjsonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            selection = self.view.substr(region)

            try:
                obj = json.loads(selection)
                self.view.replace(edit, region, json.dumps(obj, indent=4, ensure_ascii=False, sort_keys=True))
            except Exception, e:
                sublime.status_message(str(e))
