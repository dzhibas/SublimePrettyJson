[![Build Status](https://travis-ci.org/dzhibas/SublimePrettyJson.svg)](https://travis-ci.org/dzhibas/SublimePrettyJson)

Prettify/Minify/Query JSON plugin for Sublime Text 2 & 3

## Installation

Install this sublime text package via [Package Control](https://sublime.wbond.net)

### or manual installation

- `cd <Packages directory>`
- `git clone https://github.com/dzhibas/SublimePrettyJson.git`

## Usage

To prettify JSON, make selection of json and press keys:

- Linux: <kbd>ctrl+alt+j</kbd>
- Windows: <kbd>ctrl+alt+j</kbd>
- OS X: <kbd>cmd+ctrl+j</kbd>

or through Command Palette <kbd>Ctrl+Shift+P</kbd> find "Pretty JSON: Format (Pretty Print) JSON"

If selection is empty and configuration entry **use_entire_file_if_no_selection** is true, tries to prettify whole file

If JSON is not valid it will be displayed in status bar of Sublime Text

### Compress / Minify JSON

Using Command Palette <kbd>Ctrl+Shift+P</kbd> find "Pretty JSON: Minify (compress) JSON" this will make selection or full buffer as single line JSON which later you can use in command lines (curl/httpie) or somewhere else...

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
