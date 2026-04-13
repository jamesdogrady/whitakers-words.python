This is a port of whitakkers words from ADA to Python.
it uses google gemini to do the port with the following prompt.
System Role: > You are an expert system migration engineer specializing in converting legacy Ada 95/2005/2012 codebases to modern Python 3.12+. Your goal is to maintain the rigorous logic and safety of Ada while leveraging Pythonic patterns (Type Hinting, Pydantic, Asyncio).

Task: > Translate the provided Ada source code into a Python module.

Requirements:

Data Integrity: Ada Range and Subtype constraints must be enforced using pydantic.Field or custom @property setters.

Interfaces: Ada Package Specs (.ads) should be used to define the Python module's public API and Type Stubs (.pyi).

Concurrency: Map Ada Tasks to Python threading or asyncio depending on the context provided.

Error Handling: Map Ada Exceptions to custom Python exception classes.

Typing: Use strict mypy type hints for all function signatures.

Input Context:

Ada Spec: [
"""
#NSERT SPEC CONTENT HERE]
prompt2 = """
]

Ada Body: [
"""

One would have been smarter to ask it not to create a definition in a file where the ADA did not have a definition as this lead to multiple definitios of some symbols.  There is a better way to get the import system worked out, but 
I did it manually at the end.

There is generally a one-to-one mapping between .ads/adb files in the ADA source and the resulting python. I created
two subpackages to split some of the code in the latin\_utils module due to the differences between how python and ADA 
packaging works.  I doubt what was done is optimal.


The files with dictionary package in the name moved to a new directory dictionary\_package.  The files with inflection\_package in the name moved to inflections\_package.  The original file names shown below have "-" in the names and 
the python versions have "\_" only.

Dictionary package has

* src/latin\_utils/latin\_utils-dictionary\_package
* src/latin\_utils/latin\_utils-dictionary\_package-adjective\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-adverb\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-conjunction\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-dictionary\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-interjection\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-kind\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-noun\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-numeral\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-parse\_record\_io
* src/latin\_utils/latin\_utils-dictionary\_package-part\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-preposition\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-pronoun\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-propack\_entry\_io
* src/latin\_utils/latin\_utils-dictionary\_package-translation\_record\_io
* src/latin\_utils/latin\_utils-dictionary\_package-verb\_entry\_io

Inflections\_package has

* src/latin\_utils/latin\_utils-inflections\_package
* src/latin\_utils/latin\_utils-inflections\_package-adjective\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-adverb\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-conjunction\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-decn\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-ending\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-inflection\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-interjection\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-noun\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-numeral\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-prefix\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-preposition\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-pronoun\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-propack\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-quality\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-stem\_type\_io
* src/latin\_utils/latin\_utils-inflections\_package-suffix\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-supine\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-tackon\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-tense\_voice\_mood\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-verb\_record\_io
* src/latin\_utils/latin\_utils-inflections\_package-vpar\_record\_io

The following remain in latin\_utils.

* src/latin\_utils/latin\_utils
* src/latin\_utils/latin\_utils-general
* src/latin\_utils/latin\_utils-config
* src/latin\_utils/latin\_utils-latin\_file\_names
* src/latin\_utils/latin\_utils-preface
* src/latin\_utils/latin\_utils-strings\_package
* 
