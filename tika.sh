#!/bin/bash

. venv/bin/activate

tika-python parse all part1.pdf
cat part1.pdf_meta.json | jq -r '.[0].["X-TIKA:content"]' > part1_meta.html
tika-python parse all part2.pdf
cat part2.pdf_meta.json | jq -r '.[0].["X-TIKA:content"]' > part2_meta.html
