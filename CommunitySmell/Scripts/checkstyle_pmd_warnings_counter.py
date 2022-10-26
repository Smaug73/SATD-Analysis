#   Script per il conteggio dei warning all'interno di checkstyle e generazione di csv
#   Il conteggio va fatto a livello di metodo, per capire se un warning si trova all'interno di un metodo
#   va visto l'informazione sulle line dal dataset costruito con pydriller e la line del warning dal xml di checkstyle

#   Nei file costruiti con pydriler c'e' una label Begin--End che ci dice inizio e fine di un metodo
#   Abbiamo una riga per ogni metodo di una classe per ogni commit, e di conseguenza dove inizia e finisce il metodo
#   Per quanto riguarda il csv di pmd abbiamo il nome della label File scritta allo stesso modo di quello di pydriller

#   Per ogni metodo presente nei dataset di pydriller dobbiamo aggiungere il numero di warning checkstyle

#   Cose di cui tenere conto:   File omonimi, cercare di capire come aggiungere i Community Smell all'interno del dataset


#   Step:
#   1   Leggere csv pydriller di un certo progetto e il csv contenente gli omonimi

#   2   Leggere commit per commit:
#           2.1 Per ogni file del commit preso in considerazione:
    #           3.1 Controllare che non abbia omonimi
    #           3.2 Leggere file pmd e checkstyle

    #           3.3 Per ogni medoto all'interno di quel file:
    #                   4.1 cercare il file pmd e checkstyle usando il commit per orientarci tra le cartelle
    #                   4.2 contare warning checkstyle e pmd per quel metodo controllando la riga nella quale di trova
    #                   4.3 aggiungere l'informazione all'interno del csv di pydriller