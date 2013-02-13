# Sublime Plugin: SublimePelican

A plugin for [Pelican](http://getpelican.com/) integration to [Sublime Text 2](http://www.sublimetext.com/2).

## Usage

*   Type `Pelican` in Command Palette to view a list of available commands.
*   Right click on a file being edit, and access the related commands under the **Pelican** item.

## Features

*   Smart article metadata generation
    -   **Automatically generate article date** on metadata creation/insertion
    -   **Automatically generate article slug** from article title on save or on title change
    -   Customizable metadata template

## Settings

### Smart article metadata generation

#### Slug generation

*   **generate_slug_from_title**
    -   Set to "title_change" to generate slug when article title changes
    -   Set to "save" to generate slug on save
    -   Set to "none" to disable slug generation

    Default value: `save`

*   **force_slug_regeneration**

    By default, slug is not automatically generated if a slug has been defined in the article.
    Set to `true` to force slug regeneration.

    Default value: `false`

#### Others

*   **filepath_filter**

    Filename filter for Pelican articles, written in Python regex.
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
