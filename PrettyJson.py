import sublime
import sublime_plugin
import decimal

try:
    # python 3 / Sublime Text 3
    from . import simplejson as json
    from .simplejson import OrderedDict
except (ValueError):
    # python 2 / Sublime Text 2
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
                obj = json.loads(self.view.substr(selection),
                    object_pairs_hook=OrderedDict,
                    parse_float=decimal.Decimal)

                self.view.replace(edit, selection, json.dumps(obj,
                    indent=s.get("indent", 2),
                    ensure_ascii=s.get("ensure_ascii", False),
                    sort_keys=s.get("sort_keys", False),
                    separators=(',', ': '),
                    use_decimal=True))

            except Exception:
                import sys
                exc = sys.exc_info()[1]
                sublime.status_message(str(exc))


def plugin_loaded():
    global s
    s = sublime.load_settings("Pretty JSON.sublime-settings")