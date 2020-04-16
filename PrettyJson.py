import decimal
import os
import re
import subprocess
import shutil
import sys
from xml.etree import ElementTree

import sublime
import sublime_plugin

from .lib import simplejson as json
from .lib.simplejson import OrderedDict

SUBLIME_MAJOR_VERSION = int(sublime.version()) / 1000

s = sublime.load_settings('Pretty JSON.sublime-settings')

xml_syntax = 'Packages/XML/XML.tmLanguage'
json_syntax = 'Packages/JSON/JSON.tmLanguage'

jq_exists = bool()
jq_init = bool()
jq_path = str()


def check_jq():
    global jq_init, jq_exists, jq_path

    if jq_init:
        return

    jq_init = True
    jq_test = s.get('jq_binary', 'jq')
    try:
        jq_path = shutil.which(jq_test)
        jq_exists = True
    except OSError as ex:
        print(str(ex))
        jq_exists = False


class PrettyJsonBaseCommand:
    phantom_set = sublime.PhantomSet
    phantoms = list()
    force_sorting = False
    json_char_matcher = re.compile(r'char (\d+)')
    brace_newline = re.compile(r'^((\s*)".*?":)\s*([{])', re.MULTILINE)
    bracket_newline = re.compile(r'^((\s*)".*?":)\s*([\[])', re.MULTILINE)

    @staticmethod
    def json_loads(selection: str) -> dict:
        return json.loads(
            selection, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal
        )

    @staticmethod
    def json_dumps(obj, minified: bool = False) -> str:
        sort_keys = s.get('sort_keys', False)
        if PrettyJsonBaseCommand.force_sorting:
            sort_keys = True

        line_separator = s.get('line_separator', ',')
        value_separator = s.get('value_separator', ': ')
        if minified:
            line_separator = line_separator.strip()
            value_separator = value_separator.strip()

        output_json = json.dumps(
            obj,
            indent=None if minified else s.get('indent', 2),
            ensure_ascii=s.get('ensure_ascii', False),
            sort_keys=sort_keys,
            separators=(line_separator, value_separator),
            use_decimal=True,
        )
        if minified:
            return output_json

        post_process = s.get('keep_arrays_single_line', False)
        if post_process:
            matches = re.findall(r'(\[[^\[\]]+?\])', output_json)
            matches.sort(key=len, reverse=True)
            join_separator = line_separator.ljust(2)
            for m in matches:
                content = m[1:-1]
                items = [a.strip() for a in content.split(line_separator.strip())]

                replacement = '[' + join_separator.join(items) + ']'
                if len(replacement) <= s.get('max_arrays_line_length', 120):
                    output_json = output_json.replace(m, replacement, 1)
        if s.get("brace_newline", True):
            output_json = PrettyJsonBaseCommand.brace_newline.sub(r'\1\n\2\3', output_json)

        if (
            s.get("bracket_newline", True)
            and s.get('keep_arrays_single_line', False) is False
            ):
            output_json = PrettyJsonBaseCommand.bracket_newline.sub(r'\1\n\2\3', output_json)

        return output_json

    def brace_bracket_newline(json_data: str) -> str:
        better_json =  PrettyJsonBaseCommand.brace_bracket_newline.sub(r'\1\n\2\3', json_data)
        return better_json

    def reindent(self, text: str, selection: str):
        current_line = self.view.line(selection.begin())
        text_before_sel = sublime.Region(current_line.begin(), selection.begin())

        reindent_mode = s.get('reindent_block', False)
        if reindent_mode == 'start':
            space_number = text_before_sel.size()
            indent_space = ' ' * space_number
        elif reindent_mode == 'minimal':
            indent_space = re.search(r'^\s*', self.view.substr(text_before_sel)).group(0)

        lines = text.split('\n')

        i = 1
        while i < len(lines):
            lines[i] = f'{indent_space}{lines[i]}'
            i += 1

        return '\n'.join(lines)

    def show_exception(self, region: sublime.Region = None, msg=str()):
        sublime.status_message(f'[Error]: {msg}')
        if region is None:
            sublime.message_dialog(f'[Error]: {msg}')
            return
        self.highlight_error(region=region, message=f'{msg}')

    def highlight_error(self, region: sublime.Region, message: str):
        self.phantom_set = sublime.PhantomSet(self.view, 'json_errors')

        char_match = self.json_char_matcher.search(message)
        if char_match:
            if region.a > region.b:
                region.b += int(char_match.group(1))
                region.a = region.b + 1
            else:
                region.a += int(char_match.group(1))
                region.b = region.a + 1

        self.phantoms.append(
            sublime.Phantom(
                region,
                self.create_phantom_html(message, 'error'),
                sublime.LAYOUT_BELOW,
                self.navigation,
            )
        )
        self.phantom_set.update(self.phantoms)
        self.view.set_status('json_errors', message)

    # Description: Taken from 
    # - https://github.com/sublimelsp/LSP/blob/master/plugin/diagnostics.py
    # - Thanks to the LSP Team
    def create_phantom_html(self, content: str, severity: str) -> str:
        stylesheet = sublime.load_resource('Packages/Pretty JSON/phantom.css')
        return f'''<body id=inline-error>
                    <style>{stylesheet}</style>
                    <div class="{severity}-arrow"></div>
                    <div class="{severity} container">
                        <div class="toolbar">
                            <a href="hide">×</a>
                        </div>
                        <div class="content">{content}</div>
                    </div>
                </body>'''

    def navigation(self, href: str):
        self.clear_phantoms()

    def clear_phantoms(self):
        if isinstance(self.phantom_set, type):
            self.phantom_set = sublime.PhantomSet(self.view, 'json_errors')

        self.phantoms = list()
        self.phantom_set.update(self.phantoms)

    def syntax_to_json(self):
        self.view.set_syntax_file(json_syntax)


class PrettyJsonValidate(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        PrettyJsonBaseCommand.clear_phantoms(self)
        regions = self.view.sel()
        for region in regions:
            if region.empty() and len(regions) > 1:
                continue
            elif region.empty() and s.get('use_entire_file_if_no_selection', True):
                selection = sublime.Region(0, self.view.size())
                region = sublime.Region(0, self.view.size())
            else:
                selection = region

            try:
                self.json_loads(self.view.substr(selection))
            except Exception as ex:
                self.show_exception(region=region, msg=ex)
                return

            try:
                decoder = json.JSONDecoder(object_pairs_hook=self.duplicate_key_hook)
                decoder.decode(self.view.substr(selection))
            except Exception as ex:
                self.show_exception(region=region, msg=ex)
                return

            sublime.status_message("JSON Valid")

    def duplicate_key_hook(self, pairs):
        result = dict()
        for key, val in pairs:
            if key in result:
                raise KeyError(f"Duplicate key specified: {key}")
            result[key] = val
        return result



class PrettyJsonCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    '''
    Description: Pretty Print JSON
    '''

    def run(self, edit):
        PrettyJsonBaseCommand.clear_phantoms(self)
        regions = self.view.sel()
        for region in regions:
            selected_entire_file = False
            if region.empty() and len(regions) > 1:
                continue
            elif region.empty() and s.get('use_entire_file_if_no_selection', True):
                selection = sublime.Region(0, self.view.size())
                region = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                selection_text = self.view.substr(selection)
                obj = self.json_loads(selection_text)

                json_text = self.json_dumps(obj=obj, minified=False)
                if not selected_entire_file and s.get('reindent_block', False):
                    json_text = self.reindent(json_text, selection)

                self.view.replace(edit, selection, json_text)

                if selected_entire_file:
                    self.syntax_to_json()

            except Exception as ex:
                try:
                    amount_of_single_quotes = re.findall(
                        r"(\'[^\']+\'?)", selection_text
                    )
                    amount_of_double_quotes = re.findall(
                        r"(\"[^\"]+\"?)", selection_text
                    )

                    if len(amount_of_single_quotes) >= len(amount_of_double_quotes):
                        selection_text_modified = re.sub(
                            r"(?:\'([^\']+)\'?)", r'"\1"', selection_text
                        )
                        obj = self.json_loads(selection_text_modified)
                        json_text = self.json_dumps(obj=obj, minified=False)

                        if not selected_entire_file and s.get('reindent_block', False):
                            json_text = self.reindent(json_text, selection)

                        self.view.replace(edit, selection, json_text)
                        if selected_entire_file:
                            self.syntax_to_json()
                    else:
                        self.show_exception(region=region, msg=ex)
                except Exception as ex:
                    self.show_exception(region=region, msg=ex)


class PrettyJsonAndSortCommand(PrettyJsonCommand, sublime_plugin.TextCommand):
    ''' 
    Description: Pretty print json with forced sorting
    '''

    def run(self, edit):
        PrettyJsonBaseCommand.force_sorting = True
        PrettyJsonCommand.run(self, edit)
        PrettyJsonBaseCommand.force_sorting = False


class UnPrettyJsonCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    '''
    Description: Compress/minify JSON - it makes json as one-liner
    '''

    def run(self, edit):
        PrettyJsonBaseCommand.clear_phantoms(self)
        regions = self.view.sel()
        for region in regions:
            selected_entire_file = False
            if region.empty() and len(regions) > 1:
                continue
            elif region.empty() and s.get('use_entire_file_if_no_selection', True):
                selection = sublime.Region(0, self.view.size())
                region = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                obj = self.json_loads(self.view.substr(selection))
                self.view.replace(
                    edit, selection, self.json_dumps(obj=obj, minified=True)
                )

                if selected_entire_file:
                    self.syntax_to_json()

            except Exception as ex:
                self.show_exception(region=region, msg=ex)


class JqPrettyJson(sublime_plugin.WindowCommand):
    '''
    Description: Allows work with ./jq
    '''

    def run(self):
        check_jq()
        if jq_exists:
            self.window.show_input_panel(
                "Enter ./jq filter expression", ".", self.done, None, None
            )
        else:
            sublime.status_message(
                "./jq tool is not available on your system. http://stedolan.github.io/jq"
            )

    def get_content(self):
        ''' returns content of active view or selected region '''
        view = self.window.active_view()
        selection = str()
        regions = view.sel()
        for region in regions:
            if region.empty() and len(regions) > 1:
                continue
            elif region.empty():
                selection = sublime.Region(0, view.size())
            else:
                selection = region
        return view.substr(selection)

    def done(self, query: str):
        try:
            p = subprocess.Popen(
                [jq_path, query],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            raw_json = self.get_content()
            out, err = p.communicate(bytes(raw_json, "utf-8"))
            output = out.decode("UTF-8").replace(os.linesep, "\n").strip()
            if output:
                view = self.window.new_file()
                view.run_command("jq_pretty_json_out", {"jq_output": output})
                view.set_syntax_file(json_syntax)

        except OSError:
            exc = sys.exc_info()[1]
            sublime.status_message(str(exc))


class JsonToXml(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    '''
    Description: converts Json to XML
    '''

    def run(self, edit):
        self.view.erase_regions('json_errors')
        regions = self.view.sel()
        for region in regions:
            selected_entire_file = False
            if region.empty() and len(regions) > 1:
                continue
            elif region.empty() and s.get('use_entire_file_if_no_selection', True):
                selection = sublime.Region(0, self.view.size())
                region = sublime.Region(0, self.view.size())
                selected_entire_file = True
            else:
                selection = region

            try:
                h = json.loads(self.view.substr(selection))
                root = ElementTree.Element('root')
                root = self.traverse(root, h)

                xml_string = '<?xml version=\'1.0\' encoding=\'UTF-8\' ?>\n'

                rtn = ElementTree.tostring(root, 'utf-8')
                if type(rtn) is bytes:
                    rtn = rtn.decode('utf-8')

                xml_string += rtn
                if type(xml_string) is bytes:
                    xml_string = xml_string.decode('utf-8')

                if not selected_entire_file and s.get('reindent_block', False):
                    xml_string = self.reindent(xml_string, selection)

                self.view.replace(edit, selection, xml_string)

                if selected_entire_file:
                    self.syntax_to_xml()

            except Exception as ex:
                self.show_exception(region=region, msg=ex)

    def traverse(self, element, json_dict):
        ''' recursive traverse through dict and build xml tree '''
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

    def syntax_to_xml(self):
        self.view.set_syntax_file(xml_syntax)


class JqPrettyJsonOut(sublime_plugin.TextCommand):
    def run(self, edit, jq_output: str = str()):
        self.view.insert(edit, 0, jq_output)


class PrettyJsonGotoSymbolCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        self.items = list()
        self.goto_items = list()

        content = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            json_data = self.json_loads(content)
            self.generate_items(json_data, "")
            sublime.active_window().show_quick_panel(self.items, self.goto)
        except Exception as ex:
            self.show_exception(region=None, msg=ex)

    def generate_items(self, json_data, root_key):
        if isinstance(json_data, OrderedDict):
            for key in json_data:
                new_key_name = f'{root_key}.{key}'
                self.items.append(f'"{new_key_name}"')
                self.goto_items.append(f'"{key}"')
                self.generate_items(json_data[key], new_key_name)
        elif isinstance(json_data, list):
            for index, item in enumerate(json_data):
                if isinstance(item, str):
                    self.items.append(f'{root_key}.{item}')
                    self.goto_items.append(f'"{item}"')

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
            if ':' in line:
                split = line.split(':')
                val = split[1].strip()
                if string_to_search in val:
                    del regions[i]

        region = regions[found]
        self.view.sel().clear()
        self.view.sel().add(region)
        self.view.show(region)


def plugin_loaded():
    global s
    s = sublime.load_settings('Pretty JSON.sublime-settings')
