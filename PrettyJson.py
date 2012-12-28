import sublime
import sublime_plugin
import json
import sys
import decimal

if sys.version_info > (2, 7, 0):
    import json
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
                obj = json.loads(self.view.substr(selection),
                    object_pairs_hook=OrderedDict,
                    parse_float=decimal.Decimal)

                self.view.replace(edit, selection, json.dumps(obj,
                    indent=s.get("indent", 2),
                    ensure_ascii=s.get("ensure_ascii", False),
                    sort_keys=s.get("sort_keys", False),
                    separators=(',', ': '),
                    use_decimal=True))

            except Exception, e:
                sublime.status_message(str(e))
