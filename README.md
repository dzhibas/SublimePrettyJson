Prettify JSON plugin for Sublime Text 2

## Installation
Install this repository via [Package Control](http://wbond.net/sublime_packages/package_control)

## Usage
To prettify JSON, make selection of json and press keys:

- Linux: `ctrl+alt+j`
- Windows: `ctrl+alt+j`
- OS X: `cmd+ctrl+j`

If selection is empty and configuration entry **use_entire_file_if_no_selection** is true, tries to prettify whole file.

If JSON is not valid it will be displayed in status bar of sublime.

## Default configuration

**use_entire_file_if_no_selection** - true

**indent** - 4

**sort_keys** - false

**ensure_ascii** - false

## Using tabs for indentation

You can change configuration key **indent** to string value "\t" or any other string.

```
"indent_size" : "\t",
```

Be sure "Indent Using Spaces" is unchecked otherwise you will not see effect and ST2 will convert it back to spaces.

## Thanks
https://github.com/the3rdhbtaylor
