class Volumio:
    def __init__(self, address="localhost", port=3000):
        """
        Classe permettant d'interagir avec le server socket.io de Volumio
        :param address: adresse du serveur
        :param port: port du serveur
        """
        from socketIO_client import SocketIO

        self._state = {}
        self._queue = list()
        self._radios = list()
        self._waiting = 1

        print(f"Creating socket {address}:{port}")
        self._sock = SocketIO(address, port)

        # Définition des fonctions de callback
        self._sock.on('pushState', self._on_push_state)
        self._sock.on('pushBrowseLibrary', self._on_push_browse_library)
        self._sock.on('pushQueue', self._on_push_queue)

        print("Getting initial state")
        self.get_state()

    def _on_push_state(self, *args):
        """
        Callback appelée à chaque màj d'état. Met à jour localement l'état du lecteur
        """
        print("State updated")
        self._state = args[0]

    def _on_push_browse_library(self, *args):
        """
        Callback appelée lorsqu'on parcourt la bibliothèque (utilisé pour connaître la liste des webradios)
        """
        radios_list = args[0]['navigation']['lists'][0]['items']
        self._radios = list()
        for radio in radios_list:
            self._radios.append({
                'title': radio['title'],
                'uri': radio['uri']
            })

    def _on_push_queue(self, *args):
        """
        Callback appelée lorsqu'on récupère la liste des musiques en file d'attente.
        """
        print("Fetching queue")
        self._queue = list()
        for music in args[0]:
            # Les seules infos qui nous intéressent sont l'URI et le titre ou le nom (les radios ont un titre, les chansons ont un nom)
            self._queue.append({
                "uri": music['uri'],
                "title": music.get('title', None),
                "name": music.get('name', None),
            })

    def _send(self, command, args=None, callback=None):
        """
        Envoie une commande au serveur socket.io.
        :param command: commande à envoyer
        :param args: Arguments, sous forme de dictionnaire
        :param callback: Fonction de callback appelée au retour de la requête
        :return:
        """
        self._sock.emit(command, args, callback)
        self._sock.wait_for_callbacks(seconds=self._waiting)

    # Fonctions de mise à jour du lecteur
    def get_state(self):
        self._send('getState', callback=self._on_push_state)

    def get_radios(self):
        self._send('browseLibrary', {"uri": "radio/myWebRadio"}, self._on_push_browse_library)

    def get_queue(self):
        self._send('getQueue', callback=self._on_push_queue)

    def radios(self):
        """
        Retourne la liste des radios sauvegardées dans l'application
        :return: Liste contenant les URI et les noms des radios
        """
        self.get_radios()
        return self._radios

    def state(self):
        """
        Retourne les informations générales sur l'état du lecteur
        :return: Dictionnaire contenant des informtions sur ltérat du lecteur
        """
        return self._state

    def status(self):
        """
        Retourne le statut du lecteur (play/pause)
        :return: Une valeur parmi ["play", "pause"]
        """
        return self._state["status"]

    def playing(self):
        """
        Retourne le nom de la chanson en cours
        :return: Nom de la chanson en cours
        """
        return Volumio.get_name(self._state)

    def queue(self):
        """
        Retourne la liste de lecture courante
        :return: Liste contenant les musique sous forme de dictionnaire {uri, title, name}
        """
        self.get_queue()
        return self._queue

    def volume(self):
        """
        Retourne le volume courant
        :return: Volume compris entre 0 et 100
        """
        return self._state["volume"]

    def set_volume(self, volume):
        """
        Définit le volume de lecture
        :param volume: Volume souhaité [0-100]
        """
        assert isinstance(volume, int), f":volume: doit être un entier (type : {type(volume)})"
        assert 0 <= volume <= 100, f":volume: doit être compris entre 0 et 100 (valeur : {volume})"
        self._send('volume', volume, callback=self._on_push_state)

    def play_radio(self, uri):
        """
        Joue immédiatement la radio dont l'URI est passée en paramètre
        :param uri: URI de la radio à jouer
        """

        # Méthode de force brute, on est obligé de vider la queue, et d'ajouter une musique,
        # Sinon elle s'ajoute à la fin de la queue.
        self._send('clearQueue')
        self._send('addPlay', {'status':'play', 'service':'webradio', 'uri':uri})

    @staticmethod
    def get_name(music_as_dict):
        """
        Permet d'extraire le nom (qui est soit le champ 'title' soit le champ 'name' d'une musique
        :param music_as_dict: le dictionnaire représentant la musique
        :return: le titre, ou le nom, ou bien None
        """
        title = music_as_dict.get("title", None)
        name = music_as_dict.get("name", None)
        return title if title is not None else name
