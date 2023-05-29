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


# Utilisation

## Jouer

Pour jouer soi-même: `python play.py`

## IA

Le dossier *game* constitue le package du jeu.
Tous les autres dossiers contiennent une version de l'ia différentes, contenues dans le <code>main.py</code> du dossier

### Faire jouer l'IA

Pour la voire jouer, tout en bas du <code>main.py</code>, il suffit simplement de commenter la ligne run_neat() et décommenter la ligne test_ai():  
<code>\# run_neat(configs)
test_ai(configs) </code>

Puis: `python main.py`

### Entraîner l'IA

Pour l'entraîner, faire l'inverse:  
<code>run_neat(configs)
\# test_ai(configs) </code>

Puis: `python main.py`
