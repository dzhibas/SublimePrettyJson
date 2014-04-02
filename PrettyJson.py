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


class PrettyJsonCommand(sublime_plugin.TextCommand):
    """ Pretty Print JSON """
    def run(self, edit):
        for region in self.view.sel():

            selected_entire_file = False

            # If no selection, use the entire file as the selection
            if region.empty() and s.get("use_entire_file_if_no_selection", True):
                selection = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                obj = json.loads(self.view.substr(selection),
                                 object_pairs_hook=OrderedDict,
                                 parse_float=decimal.Decimal)

                text = self.view.substr(selection)

                if len(text.split("\n")) == 1:
                    self.view.replace(edit, selection, json.dumps(obj,
                                  indent=s.get("indent", 2),
                                  ensure_ascii=s.get("ensure_ascii", False),
                                  sort_keys=s.get("sort_keys", False),
                                  separators=(',', ': '),
                                  use_decimal=True))
                else:
                    self.view.replace(edit, selection, json.dumps(obj,
                                  ensure_ascii=s.get("ensure_ascii", False),
                                  sort_keys=s.get("sort_keys", False),
                                  separators=(',', ': '),
                                  use_decimal=True))

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
                import sys
                exc = sys.exc_info()[1]
                sublime.status_message(str(exc))

    def change_syntax(self):
        """ Changes syntax to JSON if its in plain text """
        if "Plain text" in self.view.settings().get('syntax'):
            self.view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")


class UnPrettyJsonCommand(PrettyJsonCommand):
    """
    Compress/minify JSON
    it makes json as one-liner
    """
    def run(self, edit):
        """ overwriting base class run function to remove intent """
        for region in self.view.sel():

            selected_entire_file = False

            # If no selection, use the entire file as the selection
            if region.empty() and s.get("use_entire_file_if_no_selection", True):
                selection = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                obj = json.loads(self.view.substr(selection),
                                 object_pairs_hook=OrderedDict,
                                 parse_float=decimal.Decimal)

                self.view.replace(edit, selection, json.dumps(obj,
                                  ensure_ascii=s.get("ensure_ascii", False),
                                  sort_keys=s.get("sort_keys", False),
                                  separators=(',', ':'),
                                  use_decimal=True))

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
                import sys
                exc = sys.exc_info()[1]
                sublime.status_message(str(exc))

def plugin_loaded():
    global s
    s = sublime.load_settings("Pretty JSON.sublime-settings")
