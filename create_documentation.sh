pandoc --from=markdown --to=rst --output=README.rst README.md
make -C ./docs clean
make -C ./docs html
