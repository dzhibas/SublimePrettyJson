import sublime
import sublime_plugin
import json
import sys

if sys.version_info > (2, 7, 0):
    from collections import OrderedDict
else:
    import simplejson as json
    from simplejson import OrderedDict


s = sublime.load_settings("Pretty JSON.sublime-settings")


class PrettyjsonCommand(sublime_plugin.TextCommand):
    """ Pretty Print JSON
    """
    def run(self, edit):
        for region in self.view.sel():
            # If no selection, use the entire file as the selection
            if region.empty() and s.get("use_entire_file_if_no_selection"):
                selection = sublime.Region(0, self.view.size())
            else:
                selection = region

            try:
                obj = json.loads(self.view.substr(selection), object_pairs_hook=OrderedDict)
                self.view.replace(edit, selection, json.dumps(obj, indent=s.get("indent_size", 4), ensure_ascii=False, sort_keys=s.get("sort_keys", False), separators=(',', ': ')))
            except Exception, e:
                sublime.status_message(str(e))

    def is_enabled(self):
        view = self.view
        if view is None:
            view = sublime.active_window().active_view()
        return 'source.json' in view.scope_name(0) or 'source.javascript' in view.scope_name(0)
