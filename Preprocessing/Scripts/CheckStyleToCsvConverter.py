from xml.dom import minidom

# parse an xml file by name
file = minidom.parse('models.xml')

#use getElementsByTagName() to get tag
models = file.getElementsByTagName('model')

# one specific item attribute
print('model #2 attribute:')
print(models[1].attributes['name'].value)
