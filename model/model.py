from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi


        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        relazioni = TourDAO.get_tour_attrazioni()
        if not relazioni:
            return

        for r in relazioni:
            id_tour = str(r["id_tour"])
            id_attr = str(r["id_attrazione"])

            tour = self.tour_map.get(id_tour)
            attr = self.attrazioni_map.get(id_attr)

            if tour is None or attr is None:
                continue

            try:
                tour.attrazioni
            except AttributeError:
                tour.attrazioni = set()

            try:
                attr.tour
            except AttributeError:
                attr.tour = set()

            tour.attrazioni.add(attr)
            attr.tour.add(tour)

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._max_giorni = max_giorni
        self._max_budget = max_budget

        # FILTRO I TOUR DELLA REGIONE
        self._tour_filtrati = [
            t for t in self.tour_map.values()
            if t.id_regione == id_regione
        ]

        self._ricorsione(
            0,
            [],
            0,  # durata
            0.0,  # costo
            0,  # valore culturale
            set(),  # attrazioni usate
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        tour_list = self._tour_filtrati

        if start_index >= len(tour_list):
            return

        for i in range(start_index, len(tour_list)):
            tour = tour_list[i]

            if any(a in attrazioni_usate for a in tour.attrazioni):
                continue

            nuova_durata = durata_corrente + tour.durata_giorni
            if self._max_giorni is not None and nuova_durata > self._max_giorni:
                continue

            nuovo_costo = costo_corrente + float(tour.costo)
            if self._max_budget is not None and nuovo_costo > self._max_budget:
                continue

            nuove_attrazioni = attrazioni_usate.union(tour.attrazioni)

            attrazioni_nuove = nuove_attrazioni - attrazioni_usate
            incremento_valore = sum(a.valore_culturale for a in attrazioni_nuove)

            pacchetto_parziale.append(tour)
            self._ricorsione(
                i + 1,
                pacchetto_parziale,
                nuova_durata,
                nuovo_costo,
                valore_corrente + incremento_valore,
                nuove_attrazioni
            )

            pacchetto_parziale.pop()