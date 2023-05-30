### **!!! Python 3.10 ou supérieur requis !!!**

# Dépendances

- **pygame**:
librairie utilisée pour dessiner le jeu

- **neat-python**:
librairie pour l'implémentation de Neat en python

- **numpy**:
librairie utilisée pour calculée les inputs du réseau sous forma de matrice et transformation

- **graphviz**:
librairie utilisée pour générer les .svg des réseaux

- **matplotlib**:
librairie utilisée pour généerer les .svg des réseaux


# Jouer

Pour jouer soi-même: `python play.py`

# Utilisation de l'IA

Le dossier *game* constitue le package du jeu.  
`1ère_implémentation`, `2ème_implémentation` et `3ème_implémentation` contiennent chacun une des implémentation présentées dans le rapport, dans le même ordre.  
Chacune de ces implémentations contient un fichier `main.py` qu'il faut exécuter pour utiliser l'ia.  

Seule la 1ère implémentation est commentée, avec des explications. Si vous souhaitez lire et comprendre le code, il est grandement recommandé de le faire sur celle-ci.  
Les autres implémentations sont très similaires, donc si vous comprenez la 1ère, vous devriez comprendre les autres.

## Faire jouer l'IA

Pour la voire jouer, tout en bas du `main.py`, il suffit simplement de commenter la ligne run_neat() et décommenter la ligne test_ai():  
`# run_neat(configs)`  
`test_ai(configs)`

Puis: `python main.py`

## Entraîner l'IA

Pour l'entraîner, faire l'inverse:  
`run_neat(configs)`  
`# test_ai(configs)`  

Puis: `python main.py`
