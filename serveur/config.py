""" 
L'URL :   L'url de connection au serveur de la webcam
        Sert aussi pour démarrer/stopper le flux vidéo 

HOST_PUBLIC_URL : l'url publique du serveur webcam 

TEXTE_ACTIVATED : sert à afficher un texte issu de l'inférence
                  pour le changer : camera.py -> def _capture_loop()
                  
LABELS : le texte à afficher au dessus du cadre de détection, en fonction du modèle Yolo
"""

URL = "http://192.168.1.32:5002"
HOST_PUBLIC_URL = "90.19.115.251"
SOCKET_PORT = 10050 
TEXTE_ACTIVATED = False  
LABELS = ['Casque OK','Casque NO','Gilet NO','Gilet OK']
TOKEN = 'tgreadfsg54s5fazkjg_uyg'
MODEL = 'models_pt/best_1.pt'