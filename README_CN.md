![Pretty Json Tests](https://github.com/dzhibas/SublimePrettyJson/workflows/Pretty%20Json%20Tests/badge.svg?branch=master)

Sublime Text 3 & 4 的 JSON 美化/压缩/查询/跳转/验证/检查 插件

## 更新说明

为了让用户能够配置自己的特定快捷键绑定，所有快捷键绑定已被移除，改为使用命令面板。

这也避免了与其他插件冲突的快捷键覆盖问题。关于快捷键绑定的详细文档，建议查看[官方文档][Offical Docs]或[社区文档][Community Docs]

## 安装

### Package Control（推荐）

通过 [Package Control][] 安装此 Sublime Text 3 / 4 插件
搜索插件："[**Pretty JSON**][]"

### 手动安装

**Sublime Text 4**

- `cd <Packages directory>` (MacOS: `~/Library/Application\ Support/Sublime\ Text/Packages`)
- `git clone https://github.com/dzhibas/SublimePrettyJson.git "Pretty JSON"`

**Sublime Text 3**

- `cd <Packages directory>`    (MacOS: `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`)
- `git clone https://github.com/dzhibas/SublimePrettyJson.git "Pretty JSON"`
- `cd Pretty JSON`
- `git checkout st3`

**Sublime Text 2**
不再支持

## 使用方法

要美化 JSON，先选中 JSON 内容
（否则将尝试使用整个视图缓冲区），然后通过命令面板 <kbd>Ctrl+Shift+P</kbd>
查找 "Pretty JSON: Format JSON"
（你可以搜索部分内容，如 'pretty format'）

如果没有选中任何内容，且配置项
**use_entire_file_if_no_selection** 为 true，
则会尝试美化整个文件

如果 JSON 无效，会在 Sublime Text 的状态栏中显示

### 验证 JSON

使用命令面板 <kbd>Ctrl+Shift+P</kbd> 查找 "Pretty JSON: Validate"
（你可以搜索部分字符串 'validate'）
这将验证选中的内容或整个文件
并在对话框中显示是否有效。
如果发现错误，视图会跳转到错误位置并高亮显示

### 压缩 / 最小化 JSON

使用命令面板 <kbd>Ctrl+Shift+P</kbd>
查找 "Pretty JSON: Minify JSON"
（你可以搜索部分内容，如 'json minify'）
这将把选中的内容或整个缓冲区转换为单行
JSON，之后你可以在命令行（curl/httpie）或其他地方使用...

要将 <kbd>Ctrl+Alt+M</kbd> 这样的组合键映射到 Minify 命令，
你可以在 .sublime-keymap 文件中添加如下设置
（例如：`Packages/User/Default (Windows).sublime-keymap`）：

```json
  { "keys": [ "ctrl+alt+m" ], "command": "un_pretty_json" }
```

#### 可以映射到快捷键的命令列表
- `pretty_json`
- `un_pretty_json`
- `pretty_json_goto_symbol`
- `escape_json`
- `unescape_json`

### 转义 JSON

使用命令面板 <kbd>Ctrl+Shift+P</kbd> 搜索
"Pretty JSON: Escape JSON"（你可以搜索部分内容，如 'escape'）
这将把选中的 JSON 或整个缓冲区转义为字符串格式，
可以用于在代码中作为字符串值使用（例如：在配置文件、API 请求体等场景）

### 反转义 JSON

使用命令面板 <kbd>Ctrl+Shift+P</kbd> 搜索
"Pretty JSON: Unescape JSON"（你可以搜索部分内容，如 'unescape'）
这将把转义的 JSON 字符串还原为正常的 JSON 格式，
并自动格式化输出

### 将 JSON 转换为 XML

使用命令面板 <kbd>Ctrl+Shift+P</kbd> 搜索
"Pretty JSON: json2xml"（你可以搜索部分内容，如 '2XML'）
这将把你选中的 JSON 或整个缓冲区转换为 XML，并
将语法和缓冲区替换为 XML 输出

## ./jQ 查询/过滤器使用

演示：

[![Demo](http://i.imgur.com/sw7Hrsp.gif?1)](http://i.imgur.com/sw7Hrsp.gif?1)

如果你的机器上安装了 "[./jq][]" 工具，按 <kdb>ctrl+atl+shift+j</kdb>
就可以对你的 JSON 执行查询。
输出将在新视图中打开，你可以再次对新缓冲区应用 jq

你可以在这里找到该工具的使用说明：

http://stedolan.github.io/jq/

## 配置

通过命令面板 <kbd>Ctrl+Shift+P</kbd> 搜索 `Preferences: Pretty JSON Settings` 来查看所有可用的配置键及其默认值。在那里你也可以配置自己的值。

以下是现有参数的详细说明、含义以及如何配置它们：

- `use_entire_file_if_no_selection`：布尔值，指示当没有选中文本时是否应使用整个文件。
- `indent`：整数，表示要使用的空格数。要使用制表符缩进，请使用 `\t`。
- `sort_keys`：布尔值，指示是否应按字母顺序排序 JSON 键。
- `ensure_ascii`：布尔值，指示是否应验证所有字符都是 ASCII 字符。
- `line_separator`：字符串，表示行之间使用的分隔符。通常不应修改此项，以确保生成的 JSON 有效。
- `value_separator`：字符串，表示 JSON 键和值之间使用的分隔符。如果你需要去掉冒号后的额外空格，可以使用此参数配置。
- `keep_arrays_single_line`：布尔值，指示是否需要重构数组并使其为单行。
- `max_arrays_line_length`：整数，确定单行值的最大长度。当行超过此最大长度时，将以多行方式格式化。
- `pretty_on_save`：布尔值，指示是否应在每次保存文件时自动美化 JSON 文件。
- `validate_on_save`：布尔值，指示是否应在每次保存文件时自动验证 JSON 文件。
- `brace_newline`：布尔值，指示大括号后是否应有换行符。
- `bracket_newline`：布尔值，指示中括号后是否应有换行符。此处为 `true` 表示生成的 JSON 将类似于 Allman 缩进风格，而 `false` 将产生 OTBS 缩进风格。
- `reindent_block`：如果我们正在格式化选中的内容，如果需要重新缩进生成的块以遵循源文档的流程，可能的值为 `minimal` 和 `start`。

    使用 `minimal` 时，生成的 JSON 行缩进的空格数与选择开始的行相同。例如：

    ```yaml
    yaml_container:
    yaml_key: { "json": "value" }
    ```

    格式化为：

    ```yaml
    yaml_container:
        yaml_key: {
          "json": "value"
        }
    ```

    使用 `start` 时，生成的 JSON 行缩进的空格数等于选择开始的列号。
    使用 `start` 时，上面的示例格式化为：

    ```yaml
    yaml_container:
        yaml_key: {
                    "json": "value"
                  }
    ```

    如果你不希望格式化器重新缩进块，请使用 `false`。
- `jq_binary`：jq 二进制文件的路径，例如 `/usr/bin/local/jq`。

## 使用制表符缩进

你可以将配置键 **indent** 更改为字符串值 `"\t"` 或任何其他字符串

```json
"indent" : "\t",
```

确保取消选中 `"Indent Using Spaces"`，否则你将看不到
效果，ST3/4 会将其转换回空格

## 贡献者

<a href="https://github.com/dzhibas/SublimePrettyJson/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=dzhibas/SublimePrettyJson" />
</a>

## 其他

如果你使用 YAML，可能会对这个插件感兴趣：[PrettyYAML][]


[Package Control]: https://packagecontrol.io
[**Pretty JSON**]: https://packagecontrol.io/packages/Pretty%20JSON
[PrettyYAML]: https://github.com/aukaost/SublimePrettyYAML
[./jq]: http://stedolan.github.io/jq/
[Offical Docs]: https://www.sublimetext.com/docs/key_bindings.html
[Community Docs]: https://docs.sublimetext.io/guide/customization/key_bindings.html

