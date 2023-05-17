# Inférence Yolo avec webcam distante 

Le dossier webcam contient le serveur qui va ouvrir le flux vidéo et l'envoyer par socket. Le dossier serveur récupère le flux vidéo, effectue la détection et propulse un page web avec le résultat (vidéo et texte) de la détection.   

Chaque dossier a un fichier de configuration config.py afin d'entrer les bons éléments réseaux. Il est possible que des ports soient à autoriser et que des règles réseaux soient à établir afin d'effectuer la connection par socket.   

Le programme est écrit en python, propulsé par deux serveurs Flask.    

Il est possible d'utiliser d'autres modèles Yolov5, à placer dans le dossier serveur/models_pt. Le nom du modèle ainsi que les labels sont à renseigner dans le fichier de configuration.  

Chaque dossier est à utiliser sur un terminal différent. Il est conseillé d'utiliser des environnements python3.8 pour chaque dossier, et d'y installer les dépendances requises (fichiers requirements.txt). 

