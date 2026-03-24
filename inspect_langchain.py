import pkgutil, langchain

print("langchain version", langchain.__version__)
for module in pkgutil.walk_packages(langchain.__path__, langchain.__name__ + '.'):
    if 'chains' in module.name:
        print(module.name)

try:
    import langchain.chains.combine_documents
    print('Found combine_documents')
    print(dir(langchain.chains.combine_documents))
except Exception as e:
    print('Error importing combine_documents:', e)
