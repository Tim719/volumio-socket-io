from volumio import Volumio


def main():
    v = Volumio("volumio.local")

    choix = ""
    while choix != "Q":
        print("\n\n\nVotre choix : Qu[E]ue [V]olume [R]adio [Q]uitter")
        print("Statut actuel : ", v.status(), " | En cours :", v.playing())
        choix = input("> ")
        choix = choix.upper()


        if choix == 'V':
            print("Volume actuel", v.volume())
            vol = int(input("Volume : "))
            v.set_volume(vol)
        if choix == 'E':
            queue = v.queue()
            for music in queue:
                print(Volumio.get_name(music))
        if choix == 'R':
            print("Radios disponibles : ")
            for key, radio in enumerate(v.radios()):
                print(key, radio['title'])
            radio = int(input("Radio> "))
            radio_uri = v.radios()[radio]['uri']
            print("uri : ", radio_uri)
            v.play_radio(radio_uri)

if __name__ == '__main__':
    main()
