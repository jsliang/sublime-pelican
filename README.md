# SublimePelican: Pelican integration to Sublime Text 2

**SublimePelican** is a plugin for [Pelican](http://getpelican.com/) integration to [Sublime Text 2](http://www.sublimetext.com/2).
It is designed to help people write Pelican articles faster using Sublime Text 2.

The plugin prepares metadata fields for you, with the ability to fill in date, to generate slug, and to list categories and tags you've used.
[More features](https://github.com/jsliang/sublime-pelican/issues?labels=enhancement&page=1&state=open) to be added.

## Installation

You can install the SublimePelican plugin with or without Git.
Support for the [Package Control plugin](http://wbond.net/sublime_packages/package_control) is pending pull request.

### Installation without Git

1.  Download the [latest source from GitHub](https://nodeload.github.com/jsliang/sublime-pelican/zip/master).
2.  Copy the `sublime-pelican-master` folder to your Sublime Text 2 Packages directory.
3.  Rename the `sublime-pelican-master` folder to `Pelican`.

If you're not sure where your Sublime Text 2 Packages directory is, open Sublime Text 2 and select menu item **Preference** > **Browse Packages...**

### Installation with Git

Clone this repository into your Sublime Text 2 Packages directory:

    git clone https://github.com/jsliang/sublime-pelican.git
    mv sublime-pelican Pelican

which is equivalent to:

    git clone https://github.com/jsliang/sublime-pelican.git Pelican

If you're not sure where your Sublime Text 2 Packages directory is, open Sublime Text 2 and select menu item **Preference** > **Browse Packages...**

## Usage

### Access commands from Command Palette

1.  After installation, bring up the Command Palette (OS X: `Command+Shift+P`; Linux/Windows: `Control+Shift+P`).
2.  Type `Pelican` in Command Palette to view a list of available commands.

### Access commands from Context Menu

Right click on a file being edit, and access the commands under the **Pelican** item.

## SublimePelican Commands

*   **Pelican: New Article (Markdown)** and **Pelican: New Article (reStructuredText)**

    These commands open a new article and have metadata fields prepared for you.

    Metadata are generated according to your metadata template.
    Refer to [Settings](#settings) > [Customizable metadata template](#customizable-metadata-template) for instructions on metadata template customization.

*   **Pelican: Insert Metadata**

    This command inserts and reorganizes metadata fields in the current opening article file.
    Metadata fields are listed in the same order as your metadata template definition.

    If the opening article has existing metadata fields, the command preserves these field values.
    Fields not listed in the metadata template are preserved too.

*   **Pelican: Insert Category**

    If you think it's hard to remember what categories you've used when writing articles, then this command is made for you.
    This command lists categories you've used in your Pelican site in the quick panel, allowig you to fuzzily select and insert a previously used category quickly.

*   **Pelican: Insert Tag**

    If you think it's hard to remember what tags you've used when writing articles, then this command is made for you.
    This command lists tags you've used in your Pelican site in the quick panel, allowig you to fuzzily select and insert a previously used tag quickly.

*   **Pelican: Update Article Date**

    This command updates the date metadata field to current date and time.

*   **Pelican: Update Slug using Title**

    This command generates the slug field from article title.

## Settings

For the latest information on what SublimePelican settings are available, select the menu item **Preferences** > **Package Settings** > **Pelican** > **Settings - Default**.

DO NOT edit the settings in "Settings - Default" as changes will be lost when SublimePelican is updated.
Instead, customize your settings in **Preferences** > **Package Settings** > **Pelican** > **Settings - User**.

### Smart metadata fields generation

#### Slug generation

*   **force_slug_regeneration**

    By default, slug is not automatically generated if a slug has been defined in the article.
    Set to `true` to force slug regeneration.

    Default value: `false`

*   **generate_slug_from_title**

    -   Set to `"none"` to disable slug generation

    -   Set to `"title_change"` to generate slug when article title changes

        Note that when set to `"title_change"`, slug will be regenerated everytime you type in the title line, even if `force_slug_regeneration` is set to `false`.

    -   Set to `"save"` to generate slug on save

        By default, slug is not automatically generated if a slug has been defined in the article.
        This is to prevent unwanted slug change.
        If you want to force slug regeneration on each save, you have to set `force_slug_regeneration` to `true`.

    Default value: `"save"`

### Customizable metadata template

*   **article_metadata_template**

    Metadata template for Markdown & reStructuredText articles.

    Default value:

```
{
    // Metadata template for Markdown articles
    "md":
        [
            "title: %(title)s",
            "slug: %(slug)s",
            "date: %(date)s",
            "tags: %(tags)s",
            "category: %(category)s",
            "author: %(author)s",
            "lang: %(lang)s",
            "summary: %(summary)s"
        ],

    // Metadata template for reStructuredText articles
    "rst":
        [
            ":title: %(title)s",
            ":slug: %(slug)s",
            ":date: %(date)s",
            ":tags: %(tags)s",
            ":category: %(category)s",
            ":author: %(author)s",
            ":lang: %(lang)s",
            ":summary: %(summary)s"
        ]
}
```

### File Path Filter for Pelican Articles

To prevent automatic slug generation from annoyly affecting other Markdown/reStrcturedText files that are not Pelican articles, SublimePelican processes only the Markdown/reStructuredText files under the `INPUTDIR` configured in your Pelican Makefile.

*   **use_input_folder_in_makefile**

    When set to `false`, SublimePelican will use the regular expression defined in `filepath_filter` as the file path filter for Pelican articles.

    Default value: `true`

*   **filepath_filter**

    File path filter for Pelican articles, written in a Python regular expression.
    Effective only if `use_input_folder_in_makefile` is set to `false`.

    By default, only Markdown/reStructuredText files under `content/` directory are deemed as Pelican article files.

    Default value: `"content/.*\\.(md|markdown|mkd|rst)$"`


## TODOs

Please refer to [Issues](https://github.com/jsliang/sublime-pelican/issues).
You are also welcomed to propose [enhancements](https://github.com/jsliang/sublime-pelican/issues?labels=enhancement&page=1&state=open) there.

## Thanks

*   [Pelican](http://getpelican.com/)
*   [Sublime Text](http://www.sublimetext.com/)
*   [DocumentUp](http://documentup.com/)

## License

SublimePelican is licensed under the MIT license.

Copyright (c) 2013, Jui-Shan Liang &lt;jenny@jsliang.com&gt;

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
