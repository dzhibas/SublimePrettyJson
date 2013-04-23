Prettify JSON plugin for Sublime Text 2 & 3

## Installation
Install this sublime text package via [Package Control](http://wbond.net/sublime_packages/package_control)

## Usage
To prettify JSON, make selection of json and press keys:

- Linux: <kbd>ctrl+alt+j</kbd>
- Windows: <kbd>ctrl+alt+j</kbd>
- OS X: <kbd>cmd+ctrl+j</kbd>

If selection is empty and configuration entry **use_entire_file_if_no_selection** is true, tries to prettify whole file.

If JSON is not valid it will be displayed in status bar of sublime.

## Default configuration

**use_entire_file_if_no_selection** - true

**indent** - 2

**sort_keys** - false

**ensure_ascii** - false

## Using tabs for indentation

You can change configuration key **indent** to string value "\t" or any other string.

```
"indent_size" : "\t",
```

Be sure "Indent Using Spaces" is unchecked otherwise you will not see effect and ST2 will convert it back to spaces.

## Thanks

- @the3rdhbtaylor https://github.com/the3rdhbtaylor
- @crcastle https://github.com/crcastle
