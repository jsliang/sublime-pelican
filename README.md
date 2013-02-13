# Sublime Plugin: SublimePelican

A plugin for [Pelican](http://getpelican.com/) integration to [Sublime Text 2](http://www.sublimetext.com/2).

## Usage

*   Type `Pelican` in Command Palette to view a list of available commands.
*   Right click on a file being edit, and access the related commands under the **Pelican** item.

## Features

*   Smart article metadata generation

    -   Prepare metadata fields for you when you create a new article

        Commands available from the Command Palette as **Pelican: New Article (Markdown)** and **Pelican: New Article (reStructuredText)**

        Metadata are generated according to your metadata template.
        Refer to [Settings](#settings) for instructions on metadata template customization.

    -   Insert metadata field to current article

        Command available from the Command Palette as  **Pelican: Insert Metadata**

        Metadata fields are inserted in the same order as your metadata template.
        Fields not listed in the metadata template are preserved too.

    -   **Automatically generate article date** on metadata creation/insertion
        -   Command available from the Command Palette as **Pelican: Update Article Date**

    -   **Automatically generate article slug** from article title on save or on title change
        -   also available from the Command Palette as **Pelican: Update Slug using Title**

*   Customizable metadata template

## Settings

For the latest information on what SublimePelican settings are available, select the menu item Preferences > Package Settings > Pelican > Settings - Default.

Please do NOT edit the settings in "Settings - Default" as changes will be lost when SublimePelican is updated.
Instead, customize your settings in Preferences > Package Settings > Pelican > Settings - User.

### Smart article metadata generation

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

#### Others

*   **filepath_filter**

    Filename filter for Pelican articles, written in a Python regular expression.
    By default, only Markdown/reStructuredText files under `content/` directory are deemed as Pelican article files.

    Default value: `"content/.*\\.(md|markdown|mkd|rst)$"`

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


## TODOs

* Build system integration
* Auto-completions for categories / tags
* More flexible **filepath_filter**: automatically retrieve the value of `INPUTDIR` variable from Pelican directory's `Makefile`
* Slug generation for non-ascii characters (unidecode?)

## License

SublimePelican is licensed under the MIT license.

Copyright (c) 2013, Jui-Shan Liang &lt;jenny@jsliang.com&gt;

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
