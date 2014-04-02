import sublime
import sublime_plugin
import decimal
import sys

try:
    # python 3 / Sublime Text 3
    from . import simplejson as json
    from .simplejson import OrderedDict
except (ValueError):
    # python 2 / Sublime Text 2
    import simplejson as json
    from simplejson import OrderedDict

s = sublime.load_settings("Pretty JSON.sublime-settings")

jq_exits = False
jq_version = None

import subprocess

try:
    # checking if jq tool is available in PATH so we can use it
    s = subprocess.Popen(["jq", "--version"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = s.communicate()
    jq_version = err.decode("utf-8").replace("jq version ", "").strip()
    jq_exits = True
except OSError:
    jq_exits = False


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

                self.view.replace(edit, selection, json.dumps(obj,
                                  indent=s.get("indent", 2),
                                  ensure_ascii=s.get("ensure_ascii", False),
                                  sort_keys=s.get("sort_keys", False),
                                  separators=(',', ': '),
                                  use_decimal=True))

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
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
                exc = sys.exc_info()[1]
                sublime.status_message(str(exc))


class JqPrettyJson(sublime_plugin.WindowCommand):
    """
    Allows work with jq
    """
    def run(self):
        self.window.show_input_panel("Enter JQ query", ".", on_done=self.done, on_change=None, on_cancel=None)

    def get_content(self):
        view = self.window.active_view()
        selection = ""
        for region in view.sel():
            # If no selection, use the entire file as the selection
            if region.empty():
                selection = sublime.Region(0, view.size())
            else:
                selection = region
        return view.substr(selection)

    def done(self, query):
        try:
            p = subprocess.Popen(["jq", query], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            raw_json = self.get_content()
            out, err = p.communicate(bytes(raw_json, "utf-8"))
            output = out.decode("UTF-8").strip()

            if output:
                view = self.window.new_file()
                view.run_command("jq_pretty_json_out", {"jq_output": output})
                view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")

        except OSError:
            exc = sys.exc_info()[1]
            sublime.status_message(str(exc))


class JqPrettyJsonOut(sublime_plugin.TextCommand):
    def run(self, edit, jq_output=''):
        self.view.insert(edit, 0, jq_output)


def plugin_loaded():
    global s
    s = sublime.load_settings("Pretty JSON.sublime-settings")