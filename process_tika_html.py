from markdownify import markdownify as md
import re
import json
import sys

def process_part(part):
    file = open(f'part{part}_meta.html')
    html = file.read()
    mdown = md(html)
    mdown = mdown.replace('\r', '')
    mdown = mdown.replace('\n\n\n\n', '\n')
    mdown = re.sub(r'\n\n\nRK3399 TRM \nCopyright 2016 @ FuZhou Rockchip Electronics Co., Ltd. [0-9]+ \n', '\n', mdown)
    mdown = mdown.replace('Bit Attr Reset Value Description \nBit Attr Reset Value Description \n', 'Bit Attr Reset Value Description\n')
    with open(f'part{part}.md', 'w') as f:
        f.write(mdown.replace('\n\n\n\n', '\n'))

    lines = open(f'part{part}.md').readlines()
    lines = [line for line in lines if line.strip()]
    descriptions = []
    for i, line in enumerate(lines):
        if line.startswith('Bit Attr Reset Value Description'):
            j = i - 1
            while not lines[j].startswith('Address:'):
                if lines[j].startswith('Bit Attr Reset Value Description'):
                    break
                j -= 1
            if lines[j].startswith('Bit Attr Reset Value Description'):
                continue
            descriptions.append('\n'.join(x.strip().replace('\n\n', '\n').replace('\\', '') for x in lines[j-1:i]))
    json.dump(descriptions, open(f'part{part}_descriptions.json', 'w'), indent=2)

if __name__ == '__main__':
    process_part(sys.argv[1])
