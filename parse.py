from pdf2image import convert_from_path

convert_from_path('part1.pdf', dpi=200, output_folder='images', fmt='png', use_pdftocairo=True, output_file='part1')