page_bounds = ((125, 125), (1535, 125), (125, 2200), (1535, 2200))

from PIL import Image
from pathlib import Path
import pytesseract
import json
from tqdm.contrib.concurrent import process_map

def process_image(name):
    path = f'images/{name}.png'
    image = Image.open(path)

    new_image = image.crop((125, 125, 1535, 2200))

    for x in range(0, (1535 - 125)):
        is_black = 0
        for y in range(0, (2200 - 125)):
            pixel = new_image.getpixel((x, y))
            if pixel[0] > 180 and pixel[1] > 180 and pixel[2] > 180:
                new_image.putpixel((x, y), (255, 255, 255))

    new_image.save('images/whitened.png')

    hline_coords = []
    for y in range(0, (2200 - 125)):
        is_black = 0
        for x in range(0, (1535 - 125)):
            pixel = new_image.getpixel((x, y))
            if pixel[0] < 100 and pixel[1] < 100 and pixel[2] < 100:
                is_black += 1
        if is_black > 75 / 100 * (1535 - 125):
            hline_coords.append(y)
            for x in range(0, (1535 - 125)):
                new_image.putpixel((x, y), (255, 0, 0))

    new_hline_coords = []
    for i in range(0, len(hline_coords) - 1):
        if hline_coords[i + 1] - hline_coords[i] > 5:
            new_hline_coords.append(hline_coords[i])
    if len(hline_coords) > 0:
        new_hline_coords.append(hline_coords[-1])

    new_hline_coords = [0, *new_hline_coords, 2200 - 125]
    page_structure = []
    for i in range(1, len(new_hline_coords)):
        y_start = new_hline_coords[i - 1]
        y_end = new_hline_coords[i]
        cols = []
        for x in range(0, (1535 - 125)):
            is_black = 0
            for y in range(y_start, y_end):
                pixel = new_image.getpixel((x, y))
                if pixel[0] < 100 and pixel[1] < 100 and pixel[2] < 100:
                    is_black += 1
            if is_black > 90 / 100 * (y_end - y_start):
                cols.append(x)
                for y in range(y_start, y_end):
                    new_image.putpixel((x, y), (0, 0, 255))
        new_cols = []
        for i in range(len(cols) - 1):
            if cols[i + 1] - cols[i] > 5:
                new_cols.append(cols[i])
        if len(cols) > 0:
            new_cols.append(cols[-1])
        if len(new_cols) < 2:
            page_structure.append({
                'type': 'text',
                'x0': 0,
                'y0': y_start,
                'x1': 1535 - 125,
                'y1': y_end
            })
        else:
            page_structure.append({
                'type': 'row',
                'cols': new_cols,
                'y0': y_start,
                'y1': y_end
            })
    content_structure = []
    for i in range(len(page_structure)):
        if page_structure[i]['type'] == 'text':
            content_structure.append(page_structure[i])
            continue
        if i == 0 or page_structure[i - 1]['type'] == 'text':
            content_structure.append({
                'type': 'table',
                'x0': page_structure[i]['cols'][0],
                'x1': page_structure[i]['cols'][-1],
                'y0': page_structure[i]['y0'],
                'y1': page_structure[i]['y1'],
                'rows': [page_structure[i]]
            })
            continue
        if page_structure[i - 1]['type'] == 'row':
            content_structure[-1]['y1'] = page_structure[i]['y1']
            content_structure[-1]['rows'].append(page_structure[i])

    def add_border(image, width=2, color=(0, 0, 0)):
        image = image.convert('L')
        if image.width < 3 * width or image.height < 3 * width:
            return image
        new_image = image.crop((width, width, image.width - width, image.height - width))
        return new_image

    tesseract_config = '--psm 6 -c load_system_dawg=false -c load_freq_dawg=false'
    Path(f'content/{name}').mkdir(parents=True, exist_ok=True)
    for s, structure in enumerate(content_structure):
        if structure['type'] == 'text':
            tile = add_border(new_image.crop((structure['x0'], structure['y0'], structure['x1'], structure['y1'])))
            tile.save(f'content/{name}/{s}_text.png')
            structure['text'] = pytesseract.image_to_string(tile, lang='eng+equ', config=tesseract_config).strip()
            structure['image_path'] = f'content/{name}/{s}_text.png'
        else:
            tile = add_border(new_image.crop((structure['x0'], structure['y0'], structure['x1'], structure['y1'])))
            tile.save(f'content/{name}/{s}_table.png')
            structure['image_path'] = f'content/{name}/{s}_table.png'
            rows = structure['rows']
            for r in range(len(rows)):
                rows[r]['cells'] = []
                cols = rows[r]['cols']
                y0 = rows[r]['y0']
                y1 = rows[r]['y1']
                for c in range(len(cols) - 1):
                    tile = add_border(new_image.crop((cols[c], y0, cols[c + 1], y1)))
                    tile.save(f'content/{name}/{s}_table_cell_{r}_{c}.png')
                    rows[r]['cells'].append({
                        'text': pytesseract.image_to_string(tile, lang='eng+equ', config=tesseract_config).strip(),
                        'image_path': f'content/{name}/{s}_table_cell_{r}_{c}.png'
                    })

    json.dump(content_structure, open(f'content/{name}/structure.json', 'w'), indent=2)
    new_image.save(f'content/{name}/structure.png')

if __name__ == '__main__':
    names = range(10, 1015)
    names = [f'part20001-{str(i).zfill(4)}' for i in names]
    process_map(process_image, names, max_workers=4)
