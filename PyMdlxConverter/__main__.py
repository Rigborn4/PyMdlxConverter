from Converter import convert
from pathlib import Path
import os
import argparse


def main():
    arg_parser = argparse.ArgumentParser(description='Convert mdl to mdx or mdx to mdl.')
    arg_parser.add_argument('--convert',  dest='arglist', action='store', nargs=3, type=str,
                            help='''Allows you to convert files with specified path and with specified file_format eg.
                              --convert "abc.mdl" "xyz.mdx" "MDL"''',)
    arg_parser.add_argument('--batchedinstance', help='''Allows you to convert all files inside the folder and dumbs
     them into an output folder eg. --batchedinstance "model_directory" "output_directory", "MDX"''',
                            dest='batch_arglist', action='store', nargs=3, type=str)
    args = arg_parser.parse_args()
    batch_arglist = args.batch_arglist
    arglist = args.arglist
    if arglist:
        suffix = Path(arglist[0]).suffix
        if suffix == '.mdl':
            with open(arglist[0], 'r') as f:
                buffer = f.read()
        elif suffix == '.mdx':
            with open(arglist[0], 'rb') as f:
                buffer = f.read()
        else:
            raise ValueError('Unsupported file format. Supported formats: .mdl, .mdx')
        if arglist[2] == 'MDL':
            output = convert(buffer, 'MDL')
            with open(arglist[1], 'w') as f:
                f.write(output)
            print(f'File successfully saved as mdl in {arglist[1]}')
        elif arglist[2] == 'MDX':
            output = convert(buffer, 'MDX')
            with open(arglist[1], 'wb') as f:
                f.write(output)
            print(f'File successfully saved as mdx in {arglist[1]}')
        else:
            raise ValueError('Unsupported file format. Supported formats: .mdl, .mdx')
    elif batch_arglist:
        print(batch_arglist)
        file_dir = Path(batch_arglist[0])
        files = [f for f in file_dir.iterdir() if not f.is_dir()]
        for file in files:
            print(f'Opening file: {file.name}')
            suffix = Path(file).suffix
            if suffix == '.mdl':
                with open(file, 'r') as f:
                    buffer = f.read()
            elif suffix == '.mdx':
                with open(file, 'rb') as f:
                    buffer = f.read()
            else:
                raise ValueError('Unsupported file format. Supported formats: .mdl, .mdx')
            outpath = os.path.join(batch_arglist[1], file.name)
            outpath = Path(outpath)
            outpath = str(outpath).split('.')[0]
            if batch_arglist[2] == 'MDL':
                outpath = str(outpath) + '.mdl'
                print(f'Parsing file: {file.name}')
                output = convert(buffer, 'MDL')
                print(f'Converting file: {file.name}')
                print(f'Saving file: {file.name} as {Path(outpath).name} in {Path(outpath).parent}')
                with open(outpath, 'w') as f:
                    f.write(output)
                print(f'File: {file.name} successfully saved as mdl')
            elif batch_arglist[2] == 'MDX':
                outpath = str(outpath) + '.mdx'
                print(f'Parsing file: {file.name}')
                output = convert(buffer, 'MDX')
                print(f'Converting file: {file.name}')
                print(f'Saving file: {file.name} as {Path(outpath).name} in {Path(outpath).parent}')
                with open(outpath, 'wb') as f:
                    f.write(output)
                print(f'File: {file.name} successfully saved as mdx')



if __name__ == "__main__": main()
