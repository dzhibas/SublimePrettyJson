import sublime
import sublime_plugin
import decimal
import sys
import re

try:
    # python 3 / Sublime Text 3
    from . import simplejson as json
    from .simplejson import OrderedDict
except (ValueError):
    # python 2 / Sublime Text 2
    import simplejson as json
    from simplejson import OrderedDict

jq_exits = False
jq_version = None

import subprocess

try:
    # checking if ./jq tool is available so we can use it
    s = subprocess.Popen(["jq", "--version"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = s.communicate()
    jq_version = err.decode("utf-8").replace("jq version ", "").strip()
    jq_exits = True
except OSError:
    jq_exits = False


s = sublime.load_settings("Pretty JSON.sublime-settings")


class PrettyJsonCommand(sublime_plugin.TextCommand):
    json_error_matcher = re.compile(r"line (\d+) column (\d+) \(char (\d+)\)")

    """ Pretty Print JSON """
    def run(self, edit):
        self.view.erase_regions('json_errors')
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
                self.highlight_error(str(exc))

    def highlight_error(self, message):
        m = self.json_error_matcher.search(message)
        if m:
            line = int(m.group(1)) - 1
            regions = [self.view.full_line(self.view.text_point(line, 0)), ]
            self.view.add_regions('json_errors', regions, 'invalid', 'dot', sublime.DRAW_OUTLINED)
            self.view.set_status('json_errors', message)

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
        self.view.erase_regions('json_errors')
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
                self.highlight_error(str(exc))
                sublime.status_message(str(exc))


class JqPrettyJson(sublime_plugin.WindowCommand):
    """
    Allows work with ./jq
    """
    def run(self):
        if jq_exits:
            self.window.show_input_panel("Enter ./jq filter expression", ".", on_done=self.done, on_change=None, on_cancel=None)
        else:
            sublime.status_message("./jq tool is not available on your system. http://stedolan.github.io/jq")

    def get_content(self):
        """
        returns content of active view or selected region
        """
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