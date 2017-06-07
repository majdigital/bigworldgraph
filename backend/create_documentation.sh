#!/usr/bin/env bash
pandoc --from=markdown --to=rst --output=../README.rst ../README.md
cp -R ../img/* ./docs/source/img
make -C ./docs clean
make -C ./docs html
