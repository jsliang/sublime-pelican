# SublimePelican: Pelican integration to Sublime Text

**SublimePelican** is a [Sublime Text](http://www.sublimetext.com/) plugin that makes writing [Pelican](http://getpelican.com/) articles easier and faster.

The plugin prepares metadata fields for you, with the ability to fill in current date, to generate slug, and to list categories and tags you've used.
[More features](https://github.com/jsliang/sublime-pelican/issues?labels=enhancement&page=1&state=open) to be added.

## Installation

### Installation with Package Control

The easiest way to install SublimePelican is via [Will Bond](http://wbond.net/)'s [Sublime Package Control](http://wbond.net/sublime_packages/package_control).
Package Control automatically updates SublimePelican to the latest version for you.

1.  If you haven't installed Sublime Package Control, follow the steps here: http://wbond.net/sublime_packages/package_control/installation
2.  Open Sublime Text and bring up the Command Palette (OS X: `Command+Shift+P`; Linux/Windows: `Control+Shift+P`).
3.  Select "Package Control: Install Package", and wait for Package Control to fetch the package list.
4.  When the list appears in the quick panel, type `Pelican` to select Pelican.


### Installation without Git

1.  Download the [latest source from GitHub](https://nodeload.github.com/jsliang/sublime-pelican/zip/master).
2.  Copy the `sublime-pelican-master` folder to your Sublime Text Packages directory.
3.  Rename the `sublime-pelican-master` folder to `Pelican`.

If you're not sure where your Sublime Text Packages directory is, open Sublime Text and select menu item **Preference** > **Browse Packages...**

### Installation with Git

Clone this repository into your Sublime Text Packages directory:

    git clone https://github.com/jsliang/sublime-pelican.git
    mv sublime-pelican Pelican

which is equivalent to:

    git clone https://github.com/jsliang/sublime-pelican.git Pelican

If you're not sure where your Sublime Text Packages directory is, open Sublime Text and select menu item **Preference** > **Browse Packages...**

## Usage

### Access commands from Command Palette

1.  After installation, bring up the Command Palette (OS X: `Command+Shift+P`; Linux/Windows: `Control+Shift+P`).
2.  Type `Pelican` in Command Palette to view a list of available commands.

### Access commands from Context Menu

Right click on a file being edit, and access the commands under the **SublimePelican** item.

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

    ![Screenshot of Pelican: Insert Category](http://jsliang.com/sublime-pelican/sublimepelican_insert_category.png)

    If you think it's hard to remember what categories you've used when writing articles, then this command is made for you.
    This command lists categories you've used in your Pelican site in the quick panel, allowing you to fuzzily select and insert a previously used category quickly.

*   **Pelican: Insert Tag**

    ![Screenshot of Pelican: Insert Tag](http://jsliang.com/sublime-pelican/sublimepelican_insert_tag.png)

    If you think it's hard to remember what tags you've used when writing articles, then this command is made for you.
    This command lists tags you've used in your Pelican site in the quick panel, allowing you to fuzzily select and insert a previously used tag quickly.

*   **Pelican: Update Article Date**

    This command updates the date metadata field to current date and time.

*   **Pelican: Update Slug using Title**

    This command generates the slug field from article title.
    *Known issue: Non-ASCII characters are omitted in Sublime Text 2 (see issue [#1](https://github.com/jsliang/sublime-pelican/issues/1)).*

## Settings

For the latest information on what SublimePelican settings are available, select the menu item **Preferences** > **Package Settings** > **SublimePelican** > **Settings - Default**.

DO NOT edit the settings in "Settings - Default" as changes will be lost when SublimePelican is updated.
Instead, customize your settings in **Preferences** > **Package Settings** > **SublimePelican** > **Settings - User**.

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
            "Title: %(title)s",
            "Slug: %(slug)s",
            "Date: %(date)s",
            "Tags: %(tags)s",
            "Category: %(category)s",
            "Author: %(author)s",
            "Lang: %(lang)s",
            "Summary: %(summary)s"
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


## Comments and Bug Reports

If you have any comments, or if you find any bugs, feel free to post them in [issues](https://github.com/jsliang/sublime-pelican/issues).

## Thanks

*   [Pelican](http://getpelican.com/)
*   [Sublime Text](http://www.sublimetext.com/)
*   [Sublime Package Control](http://wbond.net/sublime_packages/package_control)

## License

SublimePelican is licensed under the MIT license.

Copyright (c) 2013, Jui-Shan Liang &lt;jenny@jsliang.com&gt;

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
