# Sublime Plugin: SublimePelican

A plugin for [Pelican](http://getpelican.com/) integration of [Sublime Text 2](http://www.sublimetext.com/2).

## Usage

* Type `Pelican` in Command Palette to view a list of available commands.
* Right click on a file being edit, and access the related commands under the **Pelican** item.

## Features

* Article metadata generation
  - **Auto generate article date** on metadata creation/insertion
  - **Auto generate article slug** from article title on save

## Configuration

### Article metadata generation

* **auto_generate_slug_on_save** (default: `true`)

  Set to `false` to prevent auto generation of slug on save.

* **force_slug_regeneration_on_save** (default: `false`)

  By default, auto generation of slug does not work if a slug has already defined in the article.
  Set to `true` to force slug regeneration on save.

* **article_filename_filter** (default: `"\\.(md|markdown|mkd|rst)$"`)

  Filename filter for Pelican articles, written in Python regex.

## TODOs

* Build system integration
* Auto completions for categories / tags

## License

SublimePelican is licensed under the MIT license.

Copyright (c) 2013, Jui-Shan Liang &lt;jenny@jsliang.com&gt;

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
