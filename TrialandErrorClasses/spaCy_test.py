#Learning class for spaCy 
#Want to see if it can be used to improve the traceability matrix python 

from spacy.lang.en import English

#Creating nlp english object
# Use the object to analyze text 
# Contains all the components in the pipeline 
# Uses langauage specfic tools 
nlp = English()

doc = nlp("Hello world!")

for token in doc: 
    print(token.text)






