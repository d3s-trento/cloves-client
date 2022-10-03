#!/bin/sh

# assumes that there is the dist subdirectory

pandoc --standalone --css gh-style.css --from gfm --to html4 ../doc/user-manual.md > dist/user-manual.html
