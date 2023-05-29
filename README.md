### **!!! Python 3.10 ou supérieur requis !!!**

# Dépendances

- **pygame**:
librairie utilisée pour dessiner le jeu

- **neat-python**:
librairie pour l'implémentation de Neat en python


# Utilisation

## Jouer

Pour jouer soi-même: python play.py

## IA

Le dossier *game* constitue le package du jeu.
Tous les autres dossiers contiennent une version de l'ia différentes, contenues dans le <code>main.py</code> du dossier

### Faire jouer l'IA

Pour la voire jouer, tout en bas du <code>main.py</code>, il suffit simplement de commenter la ligne run_neat() et décommenter la ligne test_ai():  
<code>\# run_neat(configs)
test_ai(configs) </code>

### Entraîner l'IA

Pour l'entraîner, faire l'inverse:  
<code>run_neat(configs)
\# test_ai(configs) </code>




