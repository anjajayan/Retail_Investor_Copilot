import sys
import bs4

print("Python executable:", sys.executable)
print("bs4 version:", bs4.__version__)

try:
    import lxml
    import lxml.etree
    print("lxml imported successfully")
    print("lxml version:", lxml.__version__)
except Exception as e:
    print("lxml import failed:", repr(e))

from bs4.builder import builder_registry
print("Available builders:", [builder.NAME for builder in builder_registry.builders])