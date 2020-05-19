import decimal
import os
import re
import subprocess
import shutil
from xml.etree import ElementTree as et

import sublime
import sublime_plugin

from .lib import simplejson as json
from .lib.simplejson import OrderedDict


PREVIOUS_CONTENT = [str(), str()]
PREVIOUS_QUERY_LEN = int()

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
    def json_loads(selection: str, object_pairs_hook=OrderedDict) -> dict:
        return json.loads(
            selection, object_pairs_hook=object_pairs_hook, parse_float=decimal.Decimal
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

        if s.get('keep_arrays_single_line', False):
            matches = re.findall(r'(\[[^\[\]]+?\])', output_json)
            matches.sort(key=len, reverse=True)
            join_separator = line_separator.ljust(2)
            for m in matches:
                content = m[1:-1]
                items = [a.strip() for a in content.split(line_separator.strip())]

                replacement = f'[{join_separator.join(items)}]'
                if len(replacement) <= s.get('max_arrays_line_length', 120):
                    output_json = output_json.replace(m, replacement, 1)
        elif s.get("bracket_newline", True):
            output_json = PrettyJsonBaseCommand.bracket_newline.sub(r'\1\n\2\3', output_json)

        if s.get("brace_newline", True):
            output_json = PrettyJsonBaseCommand.brace_newline.sub(r'\1\n\2\3', output_json)

        return output_json

    @staticmethod
    def get_selection_from_region(
        region: sublime.Region, regions_length: int, view: sublime.View
    ) -> sublime.Region:
        entire_file = False
        if region.empty() and regions_length > 1:
            return None, None
        elif region.empty() and s.get("use_entire_file_if_no_selection", True):
            region = sublime.Region(0, view.size())
            entire_file = True

        return region, entire_file

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
        sublime.message_dialog(f'[Error]: {msg}')
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
        self.view.show(region)
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
        syntax = os.path.splitext(os.path.basename(self.view.settings().get('syntax')))[0]
        as_json = [i.lower() for i in s.get('as_json', ['JSON'])]
        if syntax.lower() not in as_json:
            self.view.set_syntax_file(json_syntax)


class PrettyJsonValidate(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        self.clear_phantoms()
        regions = self.view.sel()
        for region in regions:
            region, _ = self.get_selection_from_region(
                region=region,
                regions_length=len(region),
                view=self.view)
            if region is None:
                continue

            try:
                self.json_loads(self.view.substr(region), self.duplicate_key_hook)
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
        self.clear_phantoms()
        regions = self.view.sel()
        for region in regions:
            region, entire_file = self.get_selection_from_region(
                region=region,
                regions_length=len(region),
                view=self.view)
            if region is None:
                continue

            try:
                selection_text = self.view.substr(region)
                obj = self.json_loads(selection_text)

                json_text = self.json_dumps(obj=obj, minified=False)
                if not entire_file and s.get('reindent_block', False):
                    json_text = self.reindent(json_text, region)

                self.view.replace(edit, region, json_text)

                if entire_file:
                    self.syntax_to_json()

            except Exception as ex:
                try:
                    count_single_quotes = re.findall(
                        r"(\'[^\']+\'?)", selection_text
                    )
                    amount_of_double_quotes = re.findall(
                        r"(\"[^\"]+\"?)", selection_text
                    )

                    if len(count_single_quotes) >= len(amount_of_double_quotes):
                        modified_text = re.sub(
                            r"(?:\'([^\']+)\'?)", r'"\1"', selection_text
                        )
                        obj = self.json_loads(modified_text)
                        json_text = self.json_dumps(obj=obj, minified=False)

                        if not entire_file and s.get('reindent_block', False):
                            json_text = self.reindent(json_text, region)

                        self.view.replace(edit, region, json_text)
                        if entire_file:
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
        self.force_sorting = True
        PrettyJsonCommand.run(self, edit)
        self.force_sorting = False


class UnPrettyJsonCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    '''
    Description: Compress/minify JSON - it makes json as one-liner
    '''

    def run(self, edit):
        self.clear_phantoms()
        regions = self.view.sel()
        for region in regions:
            region, entire_file = self.get_selection_from_region(
                region=region,
                regions_length=len(region),
                view=self.view)
            if region is None:
                continue

            try:
                obj = self.json_loads(self.view.substr(region))
                self.view.replace(
                    edit, region, self.json_dumps(obj=obj, minified=True)
                )

                if entire_file:
                    self.syntax_to_json()

            except Exception as ex:
                self.show_exception(region=region, msg=ex)


class JqInsertPrettyJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit, string):
        self.view.replace(edit, sublime.Region(0, self.view.size()), string)


class JqPrettyJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        original_view = self.view
        syntax_file = original_view.settings().get("syntax")

        total_region = sublime.Region(0, original_view.size())
        content = original_view.substr(total_region)

        sublime.run_command("new_window")
        preview_window = sublime.active_window()

        preview_window.run_command(
            "set_layout",
            {
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            },
        )

        preview_window.focus_group(1)
        preview_view = preview_window.new_file()
        preview_view.set_scratch(True)
        preview_view.set_name("Preview")
        preview_view.sel().clear()

        preview_window.focus_group(0)
        jq_view = preview_window.new_file()
        jq_view.run_command("jq_insert_pretty_json", {"string": content})
        jq_view.set_read_only(True)
        jq_view.set_scratch(True)
        jq_view.sel().clear()

        jq_view.set_syntax_file(syntax_file)
        preview_view.set_syntax_file(json_syntax)


class JqQueryPrettyJson(sublime_plugin.WindowCommand):
    """
    Description: ./jq integration
    """

    def run(self):
        check_jq()
        if jq_exists:
            preview_view = self.window.active_view()
            preview_view.run_command("jq_pretty_json")
            sublime.active_window().show_input_panel(
                "Enter ./jq filter expression", ".", self.done, self.send_query, None,
            )
        else:
            sublime.status_message(
                "./jq tool is not available on your system. http://stedolan.github.io/jq"
            )

    def get_content(self):
        """ returns content of active view or selected region """
        view = self.window.active_view_in_group(0)
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

    def send_query(self, query: str):
        global PREVIOUS_CONTENT, PREVIOUS_QUERY_LEN
        try:
            p = subprocess.Popen(
                [jq_path, query],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            QUERY_LEN = len(query)
            raw_json = self.get_content()
            if PREVIOUS_CONTENT[0] == "":
                PREVIOUS_CONTENT[0] = raw_json
            if PREVIOUS_CONTENT[1] == "":
                PREVIOUS_CONTENT[1] = raw_json

            out, err = p.communicate(bytes(raw_json, "UTF-8"))
            output = out.decode("UTF-8").replace(os.linesep, "\n").strip()
            errors = err.decode("UTF-8").replace(os.linesep, "\n").strip()
            jq_view = sublime.active_window().active_view_in_group(1)
            if output and output != "null":
                if QUERY_LEN > PREVIOUS_QUERY_LEN:
                    PREVIOUS_CONTENT[0] = PREVIOUS_CONTENT[1]
                    PREVIOUS_CONTENT[1] = output
                elif QUERY_LEN < PREVIOUS_QUERY_LEN:
                    PREVIOUS_CONTENT[1] = PREVIOUS_CONTENT[0]
                    PREVIOUS_CONTENT[0] = output
                PREVIOUS_QUERY_LEN = len(query)
            elif s.get("jq_errors", False) and errors:
                output = errors        
            else:
                if PREVIOUS_QUERY_LEN <= QUERY_LEN:
                    output = PREVIOUS_CONTENT[1]
                else:
                    output = PREVIOUS_CONTENT[0]
            jq_view.run_command("jq_insert_pretty_json", {"string": output})

        except OSError as ex:
            sublime.status_message(str(ex))

    def done(self):
        global PREVIOUS_CONTENT
        PREVIOUS_CONTENT = list()


class JsonToXml(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    '''
    Description: converts Json to XML
    '''

    def run(self, edit):
        self.clear_phantoms()
        regions = self.view.sel()
        for region in regions:
            region, entire_file = self.get_selection_from_region(
                region=region,
                regions_length=len(region),
                view=self.view)
            if region is None:
                continue

            try:
                h = json.loads(self.view.substr(region))
                root = et.Element('root')
                root = self.traverse(root, h)

                xml_string = '<?xml version=\'1.0\' encoding=\'UTF-8\' ?>\n'

                rtn = et.tostring(root, 'utf-8')
                if type(rtn) is bytes:
                    rtn = rtn.decode('utf-8')

                xml_string += rtn
                if type(xml_string) is bytes:
                    xml_string = xml_string.decode('utf-8')

                if not entire_file and s.get('reindent_block', False):
                    xml_string = self.reindent(xml_string, region)

                self.view.replace(edit, region, xml_string)

                if entire_file:
                    self.syntax_to_xml()

            except Exception as ex:
                self.show_exception(region=region, msg=ex)

    def traverse(self, element, json_dict):
        ''' recursive traverse through dict and build xml tree '''
        if type(json_dict) is dict and json_dict.keys():
            for i in json_dict.keys():
                e = et.Element(i)
                element.append(self.traverse(e, json_dict[i]))
        elif type(json_dict) is list:
            e_items = et.Element('items')
            for i in json_dict:
                e_items.append(self.traverse(et.Element('item'), i))
            element.append(e_items)
        else:
            element.set('value', str(json_dict))

        return element

    def syntax_to_xml(self):
        self.view.set_syntax_file(xml_syntax)


class PrettyJsonGotoSymbolCommand(PrettyJsonBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        self.items = list()
        self.goto_items = list()

        content = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            json_data = self.json_loads(content)
            self.generate_items(json_data, '')
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
