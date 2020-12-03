## lexnet documentation

lexnet is a **python module** for **textual data analysis** relying on several external libraries (NetworkX, pandas, scipy, matplotlib, numpy). It takes as input a .tsv file containing a tagged text (one token per line with four values corresponding to 'form', 'lemma', 'POS' and 'morph') and returns a weighted graph to allow **visualization of word cooccurrences** with respect to statistical significance. It uses graph properties to makes some calculus ; you can notably get the intersection rate of different lexical fields.

Please note lexnet's implementation is strictly minimal for now : it doesn't have any kind of input control, nor has it specific error messages. You should therefore look carefully at the way the code is built. Anyway, feel free to raise an issue if you're in trouble getting it to run properly. 

<br>

### Main functions

- **lexnet**(keylist, path, poslist, n, arg, dtype, method) -> NetworkX Graph
    - <ins>keylist</ins> : list containing the keywords whose lexical field will be visualized on the graph. keylist items have to be character strings formatted in the following way : 'word POS'. keylist items should always occur at least once in the input text (and their POS should be in poslist), otherwise an error will be raised.
    - <ins>path</ins> : character string containing the absolute path to the .tsv file you want to use as input, or the absolute path to the directory containing all the .tsv files (and only those files) you want to use as input.
    - <ins>poslist</ins> : list containing the POS you're interested in. In other terms, lexnet's analysis will be performed on the sole words that have a POS whose general category (i.e. whose first three letters in the 'POS' column from the input .tsv file) match a poslist item. poslist items have to be character strings formatted in the following way : 'POS'. poslist items have to occur at least once in the input text, otherwise an error will be raised.
    - <ins>n</ins> : integer that determines the size of the keyword-centered intervals in which the cooccurrences are counted.
    - <ins>dtype</ins> : character string that determines the 'nature' of keylist items, and therefore of nodes : can be basically 'lemma', i.e. maximum one node for a given lemma, or 'form', i.e. possibly several nodes for a given lemma with respect to the different forms of this lemma occurring in the text. Other values will raise an error.
    - <ins>character string</ins> : character string that determines which edge will be drawn on the resulting graph : can be basically 'key', to display the sole edges included in the keywords' degrees, or 'all', to display the other edges as well. Other values will raise an error.

- **intersection**(keylist, G, order) -> list of shared nodes, intersection rate, weighted intersection rate
    - <ins>keylist</ins> : same object as described above, i.e. the keywords for the different lexical fields to intersect. keylist items should always belong to G's nodes, otherwise an error will be raised.
    - <ins>G</ins> : any graph returned by the lexnet() function.
    - <ins>order</ins> : integer that determines the maximum length of the path between a keyword and any word that belongs to its lexical field (increasing order will increase intersection rates).

### Visualization information

- The **colour of a node** depends on its POS. The coulours are currently purple for verbs ('VER'), blue for nouns ('NOM'), pink for adjectives ('ADJ').
- The **size of a node** depends on its frequency in the text (once words whose POS is not included in poslist have been removed).
- The **width of an edge** depends on the statistical significance of the cooccurrence between the two vertices, using a hypergeometric model.
- The **style of an edge** is plain if one of the vertices is in keylist ; it is dashed otherwise. 



[text written using [Markdown syntax](https://about.gitlab.com/handbook/markdown-guide)]
