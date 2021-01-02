# mdx-mdl-converter
This is a model converter module that converts\
Warcraft 3 mdx model files to mdl or vice versa. It has a built-in mdl and mdx\
parser which is a ported version of ghostwolf's typescript mdlx parser. It can handle current reforged models. 
It can also be used via commandline arguments.
# Usage
Here is a simple example:


```python
from PyMdlxConverter import Converter
from PyMdlxConverter.Parser import parse

with open('abc.mdl', 'r') as f:
    buffer = f.read()

buffer = Converter.convert(buffer, 'MDX')
buffer = Converter.convert(buffer, 'MDL') # Can overwrite mdl or mdx with no problem

model = parse(buffer) # You can also use the parser and access model elements
print(model.global_sequences)
```
alternatively you can use the converter with arguments:
for windows:
```shell
python PyMdlxConverter --convert "abc.mdx" "abc.mdl" "MDL"
python PyMdlxConverter --convert "abc.mdl" "abc.mdx" "MDX"
python PyMdlxConverter --batchedinstance "Input_Folder" "Output_Folder" "MDX"
python PyMdlxConverter --batchedinstance "Input_Folder" "Output_Folder" "MDL"
```
for unix systems:
```bash
python3 PyMdlxConverter --convert "abc.mdx" "abc.mdl" "MDL"
python3 PyMdlxConverter --batchedinstance "Input_Folder" "Output_Folder" "MDX"
```
This parser is reimplemented in python from [Ghostwolf's TypeScript Code](https://github.com/flowtsohg/mdx-m3-viewer/tree/master/src/parsers/mdlx)\

## Todo (planned in next release)
* Code organization
* Migration to numpy arrays for better performance
