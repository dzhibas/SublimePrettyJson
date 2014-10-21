[![Build Status](https://travis-ci.org/dzhibas/SublimePrettyJson.svg)](https://travis-ci.org/dzhibas/SublimePrettyJson)

Prettify/Minify/Query JSON plugin for Sublime Text 2 & 3

## Installation

Install this sublime text 2/3 package via [Package Control](https://sublime.wbond.net) search for package: "[**Pretty JSON**](https://sublime.wbond.net/packages/Pretty%20JSON)"

### or manually install

- `cd <Packages directory>`
- `git clone https://github.com/dzhibas/SublimePrettyJson.git`

## Usage

To prettify JSON, make selection of json (or else it will try to use full view buffer) and press keys:

- Linux: <kbd>ctrl+alt+j</kbd>
- Windows: <kbd>ctrl+alt+j</kbd>
- OS X: <kbd>cmd+ctrl+j</kbd>

or through Command Palette <kbd>Ctrl+Shift+P</kbd> find "Pretty JSON: Format (Pretty Print) JSON" (you can search for part of it like 'pretty format')

If selection is empty and configuration entry **use_entire_file_if_no_selection** is true, tries to prettify whole file

If JSON is not valid it will be displayed in status bar of Sublime Text

### Compress / Minify JSON

Using Command Palette <kbd>Ctrl+Shift+P</kbd> find "Pretty JSON: Minify (compress) JSON" (you can search for part of it like 'json minify') this will make selection or full buffer as single line JSON which later you can use in command lines (curl/httpie) or somewhere else...

To map a key combination like <kbd>Ctrl+Alt+M</kbd> to the Minify command, you can add a setting like this to your .sublime-keymap file (eg: `Packages/User/Default (Windows).sublime-keymap`):

```
  { "keys": [ "ctrl+alt+m" ], "command": "un_pretty_json" }
```

### Convert JSON to XML

Using Command Palette <kbd>Ctrl+Shift+P</kbd> search fo "Pretty JSON: JSON 2 XML" (you can search for part of it like '2XML') this will convert your selected JSON of full buffer to XML and replace syntax and buffer to XML output

## ./jQ query/filter usage

Demo:

[![Demo](http://i.imgur.com/sw7Hrsp.gif?1)](http://i.imgur.com/sw7Hrsp.gif?1)

If on your machine "[./jq](http://stedolan.github.io/jq/)" tool is available with <kdb>ctrl+atl+shift+j</kdb> you can run against your json. output will be opened in new view so you can once again apply jq on new buffer

You can find instructions of tool here:

http://stedolan.github.io/jq/

## Default configuration

**use_entire_file_if_no_selection** - true

**indent** - 2

**sort_keys** - false

**ensure_ascii** - false

## Using tabs for indentation

You can change configuration key **indent** to string value "\t" or any other string

```
"indent" : "\t",
```

Be sure "Indent Using Spaces" is unchecked otherwise you will not see effect and ST2/3 will convert it back to spaces

## Thanks

- @the3rdhbtaylor https://github.com/the3rdhbtaylor
- @crcastle https://github.com/crcastle

## Others

If you YAMLing then maybe you interested in this plugin: https://github.com/aukaost/SublimePrettyYAML
