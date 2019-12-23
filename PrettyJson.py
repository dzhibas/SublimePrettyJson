import sublime
import sublime_plugin
import decimal
import sys
import os
import re
from xml.etree import ElementTree
from xml.dom import minidom

try:
  basestring
except NameError:
  basestring = str

try:
    # python 3 / Sublime Text 3
    from . import simplejson as json
    from .simplejson import OrderedDict
except ValueError:
    # python 2 / Sublime Text 2
    import simplejson as json
    from simplejson import OrderedDict

SUBLIME_MAJOR_VERSION = int(sublime.version()) / 1000

jq_exits = False
jq_init = False

import subprocess

""" for OSX we need to manually add brew bin path so jq can be found """
if sys.platform != 'win32' and '/usr/local/bin' not in os.environ['PATH']:
    os.environ["PATH"] += os.pathsep + '/usr/local/bin'

""" defer jq presence check until the user tries to use it, include Package "Fix Mac Path" to resolve
    all homebrew issues (https://github.com/int3h/SublimeFixMacPath) """
def check_jq():
    global jq_exits
    global jq_init

    if not jq_init:
        jq_init = True
        try:
            # checking if ./jq tool is available so we can use it
            s = subprocess.Popen(["jq", "--version"],
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            out, err = s.communicate()
            jq_exits = True
        except OSError:
            os_exception = sys.exc_info()[1]
            print(str(os_exception))
            jq_exits = False


s = sublime.load_settings("Pretty JSON.sublime-settings")


class PrettyJsonBaseCommand:
    json_error_matcher = re.compile(r"line (\d+)")
    force_sorting = False

    @staticmethod
    def json_loads(selection):
        return json.loads(selection,
                          object_pairs_hook=OrderedDict,
                          parse_float=decimal.Decimal)

    @staticmethod
    def json_dumps(obj):

        sort_keys = s.get("sort_keys", False)
        if PrettyJsonBaseCommand.force_sorting:
            sort_keys = True

        line_separator = s.get("line_separator", ",")
        value_separator = s.get("value_separator", ": ")

        output_json = json.dumps(obj,
                                 indent=s.get("indent", 2),
                                 ensure_ascii=s.get("ensure_ascii", False),
                                 sort_keys=sort_keys,
                                 separators=(line_separator, value_separator),
                                 use_decimal=True)

        # do we need try and shuffle things around ?
        post_process = s.get("keep_arrays_single_line", False)

        if post_process:
            # find all array matches
            matches = re.findall(r"\[([^\[\]]+?)\]", output_json)
            join_separator = line_separator.ljust(2)
            for m in matches:
                items = [a.strip() for a in m.split(line_separator.strip())]
                replacement = join_separator.join(items)
                # if line not gets too long, replace with single line
                if len(replacement) <= s.get("max_arrays_line_length", 120):
                    output_json = output_json.replace(m, replacement, 1)

        return output_json

    @staticmethod
    def json_dumps_minified(obj):
        line_separator = s.get("line_separator", ",")
        """:type : str"""
        value_separator = s.get("value_separator", ": ")
        """:type : str"""

        sort_keys = s.get("sort_keys", False)
        if PrettyJsonBaseCommand.force_sorting:
            sort_keys = True

        return json.dumps(obj,
                          ensure_ascii=s.get("ensure_ascii", False),
                          sort_keys=sort_keys,
                          separators=(line_separator.strip(), value_separator.strip()),
                          use_decimal=True)

    def highlight_error(self, message):

        self.view.erase_regions('json_errors')
        self.view.erase_status('json_errors')

        m = self.json_error_matcher.search(message)
        if m:
            line = int(m.group(1)) - 1

            # sometime we need to highlight one line above
            if "','" in message and "delimiter" in message:
                line_content = self.view.substr(self.view.full_line(self.view.text_point(line - 1, 0)))
                if line_content.strip()[-1] != ',' and line_content.strip() != '{' and line_content.strip() != '}':
                    line -= 1

            if "control character '\\n'" in message:
                line_content = self.view.substr(self.view.full_line(self.view.text_point(line - 1, 0)))
                quotes = re.findall(r"\"", line_content)
                if len(quotes) % 2 != 0 and len(quotes) != 0:
                    line -= 1

            regions = [self.view.full_line(self.view.text_point(line, 0)), ]

            self.view.add_regions('json_errors', regions, 'invalid', 'dot',
                                  sublime.DRAW_OUTLINED)
            self.view.show(regions[0])
            self.view.set_status('json_errors', message)

    def show_exception(self):
        exc = sys.exc_info()[1]
        sublime.status_message(str(exc))
        self.highlight_error(str(exc))

    def change_syntax(self):
        """ Changes syntax to JSON if its in plain text """
        if "Plain text" in self.view.settings().get('syntax'):
            self.view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")


class PrettyJsonValidate(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_regions('json_errors')
        for region in self.view.sel():
            # If no selection, use the entire file as the selection
            if region.empty() and s.get("use_entire_file_if_no_selection", True):
                selection = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                obj = self.json_loads(self.view.substr(selection))
                sublime.message_dialog("JSON is Valid")
            except Exception:
                self.show_exception()
                sublime.message_dialog("Invalid JSON")


class PrettyJsonCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):

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
                selection_text = self.view.substr(selection)
                obj = self.json_loads(selection_text)
                self.view.replace(edit, selection, self.json_dumps(obj))

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
                amount_of_single_quotes = re.findall(r"(\'[^\']+\'?)", selection_text)
                amount_of_double_quotes = re.findall(r"(\"[^\"]+\"?)", selection_text)

                if len(amount_of_single_quotes) >= len(amount_of_double_quotes):
                    selection_text_modified = re.sub(r"(?:\'([^\']+)\'?)", r'"\1"', selection_text)
                    obj = self.json_loads(selection_text_modified)
                    self.view.replace(edit, selection, self.json_dumps(obj))

                    if selected_entire_file:
                        self.change_syntax()
                else:
                    self.show_exception()


class PrettyJsonAndSortCommand(PrettyJsonCommand, sublime_plugin.TextCommand):

    """ Pretty print json with forced sorting """
    def run(self, edit):
        PrettyJsonBaseCommand.force_sorting = True
        PrettyJsonCommand.run(self, edit)
        PrettyJsonBaseCommand.force_sorting = False


class UnPrettyJsonCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):

    """ Compress/minify JSON - it makes json as one-liner """
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
                obj = self.json_loads(self.view.substr(selection))
                self.view.replace(edit, selection, self.json_dumps_minified(obj))

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
                self.show_exception()


class JqPrettyJson(sublime_plugin.WindowCommand):
    """
    Allows work with ./jq
    """
    def run(self):
        check_jq()
        if jq_exits:
            self.window.show_input_panel("Enter ./jq filter expression", ".",
                                         self.done, None, None)
        else:
            sublime.status_message('./jq tool is not available on your system. http://stedolan.github.io/jq')

    def get_content(self):
        """ returns content of active view or selected region """
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
            p = subprocess.Popen(["jq", query],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)

            raw_json = self.get_content()

            if SUBLIME_MAJOR_VERSION < 3:
                if sys.platform != 'win32':
                    out, err = p.communicate(bytes(raw_json))
                else:
                    out, err = p.communicate(unicode(raw_json).encode('utf-8'))
            else:
                out, err = p.communicate(bytes(raw_json, "utf-8"))
            output = out.decode("UTF-8").strip()
            if output:
                view = self.window.new_file()
                view.run_command("jq_pretty_json_out", {"jq_output": output})
                view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")

        except OSError:
            exc = sys.exc_info()[1]
            sublime.status_message(str(exc))


class JsonToXml(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    """
    converts Json to XML
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
                h = json.loads(self.view.substr(selection))
                root = ElementTree.Element("root")
                root = self.traverse(root, h)

                xml_string = "<?xml version='1.0' encoding='UTF-8' ?>\n"

                if SUBLIME_MAJOR_VERSION < 3:
                    self.indent_for_26(root)

                rtn = ElementTree.tostring(root, "utf-8")

                if type(rtn) is bytes:
                    rtn = rtn.decode("utf-8")

                xml_string += rtn

                # for some reason python 2.6 shipped with ST2
                # does not have pyexpat
                if SUBLIME_MAJOR_VERSION >= 3:
                    xml_string = minidom.parseString(xml_string).toprettyxml(encoding="UTF-8")

                if type(xml_string) is bytes:
                    xml_string = xml_string.decode("utf-8")

                self.view.replace(edit, selection, xml_string)

                if selected_entire_file:
                    self.change_syntax()

            except Exception:
                self.show_exception()

    def indent_for_26(self, elem, level=0):
        """ intent of ElementTree in case it's py26 without minidom/pyexpat """
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent_for_26(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def traverse(self, element, json_dict):
        """ recursive traverse through dict and build xml tree """
        if type(json_dict) is dict and json_dict.keys():
            for i in json_dict.keys():
                e = ElementTree.Element(i)
                element.append(self.traverse(e, json_dict[i]))
        elif type(json_dict) is list:
            e_items = ElementTree.Element('items')
            for i in json_dict:
                e_items.append(self.traverse(ElementTree.Element('item'), i))
            element.append(e_items)
        else:
            element.set('value', str(json_dict))

        return element

    def change_syntax(self):
        """ change syntax to xml """
        self.view.set_syntax_file("Packages/XML/XML.tmLanguage")


class JqPrettyJsonOut(sublime_plugin.TextCommand):
    def run(self, edit, jq_output=''):
        self.view.insert(edit, 0, jq_output)


class PrettyJsonGotoSymbolCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        self.items = []
        self.goto_items = []

        content = self.view.substr(sublime.Region(0, self.view.size()))

        try:
            json_data = self.json_loads(content)
            self.generate_items(json_data, '')
            sublime.active_window().show_quick_panel(self.items, self.goto)
        except Exception:
            self.show_exception()

    def generate_items(self, json_data, root_key):
        if isinstance(json_data, OrderedDict):
            for key in json_data:
                new_key_name = root_key + '.' + key
                self.items.append('%s' % new_key_name)
                self.goto_items.append('"%s"' % key)
                self.generate_items(json_data[key], new_key_name)
        elif isinstance(json_data, list):
            for index, item in enumerate(json_data):
                if isinstance(item, basestring):
                    self.items.append('%s' % root_key + '.' + item)
                    self.goto_items.append('"%s"' % item)

    def goto(self, pos):
        string_to_search = self.goto_items[pos]

        found = 0
        for index, item in enumerate(self.goto_items):
            if index >= pos:
                break
            if item == string_to_search:
                found += 1

        regions = self.view.find_all(string_to_search, sublime.LITERAL)
        for i, r in enumerate(regions):
            line = self.view.substr(self.view.full_line(r))
            if ":" in line:
                split = line.split(":")
                val = split[1].strip()
                if string_to_search in val:
                    del regions[i]

        region = regions[found]
        self.view.sel().clear()
        self.view.sel().add(region)
        self.view.show(region)


def plugin_loaded():
    global s
    s = sublime.load_settings("Pretty JSON.sublime-settings")
