![Pretty Json Tests](https://github.com/dzhibas/SublimePrettyJson/workflows/Pretty%20Json%20Tests/badge.svg?branch=master)

Prettify/Minify/Query/Goto/Validate/Lint JSON plugin for Sublime Text 3 & 4

## Updates

All keybindings have been removed in favor of the Command Palette. And to allow
for users to configure their own specific key bindings.

This also prevents key binding overrides which conflict with other packages. For
good documentation on key bindings I recommend you review the [Offical Docs][] or
[Community Docs][]

## Installation

### Package Control (Recommended)

Install this sublime text 3 / 4 package via [Package Control][]
search for package: "[**Pretty JSON**][]"

### Manual Installation

**Sublime Text 4**

- `cd <Packages directory>` (MacOS: `~/Library/Application\ Support/Sublime\ Text/Packages`)
- `git clone https://github.com/dzhibas/SublimePrettyJson.git "Pretty JSON"`

**Sublime Text 3**

- `cd <Packages directory>`    (MacOS: `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`)
- `git clone https://github.com/dzhibas/SublimePrettyJson.git "Pretty JSON"`
- `cd Pretty JSON`
- `git checkout st3`

**Sublime Text 2**
No longer supported

## Usage

To prettify JSON, make selection of json 
(or else it will try to use full view buffer) and through Command Palette <kbd>Ctrl+Shift+P</kbd>
find "Pretty JSON: Format JSON" 
(you can search for part of it like 'pretty format')

If selection is empty and configuration entry 
**use_entire_file_if_no_selection** is true, 
tries to prettify whole file

If JSON is not valid it will be displayed in status bar of Sublime Text

### Validate JSON

Using Command Palette <kbd>Ctrl+Shift+P</kbd> find "Pretty JSON: Validate" 
(you can search for partial string 'validate') 
this will validate selection or full file 
and will show in dialog if it's valid or invalid. 
In case of found errors view will jump to error and will highlight it

### Compress / Minify JSON

Using Command Palette <kbd>Ctrl+Shift+P</kbd> 
find "Pretty JSON: Minify JSON" 
(you can search for part of it like 'json minify') 
this will make selection or full buffer as single line 
JSON which later you can use in command lines (curl/httpie) or somewhere else...

To map a key combination like <kbd>Ctrl+Alt+M</kbd> to the Minify command, 
you can add a setting like this to your .sublime-keymap file 
(eg: `Packages/User/Default (Windows).sublime-keymap`):

```json
  { "keys": [ "ctrl+alt+m" ], "command": "un_pretty_json" }
```

#### List of commands that can be mapped to shortcuts
- `pretty_json`
- `un_pretty_json`
- `pretty_json_goto_symbol`

### Convert JSON to XML

Using Command Palette <kbd>Ctrl+Shift+P</kbd> search for 
"Pretty JSON: json2xml" (you can search for part of it like '2XML') 
this will convert your selected JSON of full buffer to XML and 
replace syntax and buffer to XML output

## ./jQ query/filter usage

Demo:

[![Demo](http://i.imgur.com/sw7Hrsp.gif?1)](http://i.imgur.com/sw7Hrsp.gif?1)

If on your machine "[./jq][]" tool is available with <kdb>ctrl+atl+shift+j</kdb>
you can run against your json. 
output will be opened in new view so you can once again apply jq on new buffer

You can find instructions of tool here:

http://stedolan.github.io/jq/

## Configuration

Check all the available configuration keys and their default values by using the Command Palette <kbd>Ctrl+Shift+P</kbd> and searching for `Preferences: Pretty JSON Settings`. From there you can also configure your own values.

Here's a run down of the existing parameters, their meaning, and how you can configure each of them:

- `use_entire_file_if_no_selection`: boolean that indicates whether the entire file should be used when there is no text selected.
- `indent`: integer that represents the number of spaces to be used. To use tab indentation, use `\t` instead.
- `sort_keys`: boolean that indicates whether the JSON keys should be sorted alphabetically.
- `ensure_ascii`: boolean that indicaes whether it should validate that all characters are ASCII characters.
- `line_separator`: string that represents the separator that will be used between lines. Usually this shouldn't be modified, to make sure the resulting JSON is valid.
- `value_separator`: string that represents the separator that will be used between JSON keys and values. If you need to get rid of extra space after the collon, you can configure that using this parameter.
- `keep_arrays_single_line`: boolean that indicates whether we need to re-structure arrays and make them single-line.
- `max_arrays_line_length`: integer that determines the max length of single-line values. When the line exceeds this max length, it will be formatted in a multi-line fashion.
- `pretty_on_save`: boolean that indicates whether JSON files should be automatically prettified on each file save.
- `validate_on_save`: boolean that indicates whether JSON files should be automatically validated on each file save.
- `brace_newline`: boolean that indicates whether there should be a newline after braces.
- `bracket_newline`: boolean that indicates whether there should be a newline after brackets. `true` here means the resulting JSON will look like the Allman indentation style, while `false` will result in an OTBS indentation style.
- `reindent_block`: if we are formatting a selection, if we need to reindent the resulting block to follow the flow of the source document the posible values are `minimal` and `start`.
      
    Using `minimal` the resulting json lines are indented as much spaces as theline where the selection starts. E.g.:

    ```yaml
    yaml_container:
    yaml_key: { "json": "value" }
    ```
    
    Gets formatted as:
    
    ```yaml
    yaml_container:
        yaml_key: {
          "json": "value"
        }
    ```
    
    Using `start`, the resulting json lines are indented a number of spaces equal to the column number of the start of the selection.
    With `start` the previous example gets formatted as:
    
    ```yaml
    yaml_container:
        yaml_key: {
                    "json": "value"
                  }
    ```
    
    Use `false` if you wouldn't like the formatter to reindent the block at all.
- `jq_binary`: path to the jq binary, e.g. `/usr/bin/local/jq`.

## Using tabs for indentation

You can change configuration key **indent** to string value `"\t"` or any other string

```json
"indent" : "\t",
```

Be sure `"Indent Using Spaces"` is unchecked otherwise you will not see 
effect and ST3/4 will convert it back to spaces

## Contributors

<a href="https://github.com/dzhibas/SublimePrettyJson/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=dzhibas/SublimePrettyJson" />
</a>

## Others

If you YAMLing then maybe you interested in this plugin: [PrettyYAML][]


[Package Control]: https://packagecontrol.io
[**Pretty JSON**]: https://packagecontrol.io/packages/Pretty%20JSON
[PrettyYAML]: https://github.com/aukaost/SublimePrettyYAML
[./jq]: http://stedolan.github.io/jq/
[Offical Docs]: https://www.sublimetext.com/docs/key_bindings.html
[Community Docs]: https://docs.sublimetext.io/guide/customization/key_bindings.html

