import numpy as np
import sympy

class galaz:
    "Opis poszczególnej gałęzi"
    def __init__(self, wezel1, wezel2, SEM, R):
        self.wezel1 = wezel1
        self.wezel2 = wezel2
        self.SEM = SEM
        self.R = R

class obwod:
    galezie = []
    
    def dodaj_galaz(self, wez1, wez2, S, R):
        self.galezie.append(galaz(wez1, wez2, S, R))

    def __init__(self):
        if __name__ == "__main__":
            ''' 
            #Przykladowy obwod do policzenia bez recznego wpisywania
            self.dodaj_galaz(0, 1, 10, 0)
            self.dodaj_galaz(1, 1, -10, 2)
            self.dodaj_galaz(1, 2, 0, 2.5)
            self.dodaj_galaz(2, 2, 4, 2)
            self.dodaj_galaz(2, 2, 0, 2)
            self.dodaj_galaz(2, 0, 0, 0)
            '''
            # Ręczne wprowadzanie obwodu z zabezpieczeniem przed błędnymi danymi
            first = True
            while True:
                print("Podaj liczbę gałęzi. (>0)")
                g = int(input())
                if g > 0:
                    break 
                print("Liczba gałęzi musi być większa od 0!")
            for x in range(g):
                while True:
                    print(f'Podaj węzły {x} gałęzi. (>=0)')
                    z1 = int(input())
                    z2 = int(input())
                    wezl = [o.wezel1 for o in self.galezie] + [i.wezel2 for i in self.galezie]
                    if z1 < 0 or z2 < 0:
                        print("Numery węzłów nie mogą być ujemne!")
                    elif not((z1 in wezl) or (z2 in wezl) or first):
                        print("Wybrane węzły nie łączą się z inną gałęzią!")
                    else: 
                        first = False
                        break
                print(f'Podaj wartość siły elektromotorycznej {x} gałęzi[V].')
                z3 = float(input())
                while True:
                    print(f'Podaj wartość rezystancji {x} gałęzi[{chr(8486)}]. (>=0)')
                    z4 = float(input())
                    if z4 >=0:
                        break
                    print("Wprowadzono ujemną wartość rezystancji!")
                self.dodaj_galaz(z1, z2, z3, z4)
               #'''
            self.oblicz()

    def oblicz(self):

        galezie = self.galezie
        g = len(galezie)
        w_max = max([max([o.wezel1 for o in galezie]), max([o.wezel2 for o in galezie])]) + 1

        A = np.zeros((2 * g, 2 * g))
        B = np.zeros(2 * g)
        P = np.zeros((w_max, g))
        wynik = [0.0] * (2*g)

        # uzupełnianie macierzy połączeniowej - wiersze węzły, kolumny gałęzie
        for i, x in enumerate(galezie):
            if x.wezel1 != x.wezel2:
                P[x.wezel1, i] = -1
                P[x.wezel2, i] = 1

        # tworzenie listy oczek 
        oczka = []
        for i, x in enumerate(galezie):
            if x.wezel1 == x.wezel2:
                oczka.append([i+1])
                continue
            pozycja = [0] * w_max
            temp_wezly = [x.wezel2]
            temp_galezie = [i+1]
            poziom = 0
            while True:
                if pozycja[poziom] > g-1:
                    if poziom == 0:
                        break
                    pozycja[poziom] = 0
                    temp_galezie.pop()
                    temp_wezly.pop()
                    poziom -= 1
                    pozycja[poziom] += 1

                elif (P[temp_wezly[poziom], pozycja[poziom]] == -1 and not(galezie[pozycja[poziom]].wezel2 in temp_wezly) and (pozycja[poziom] != i)):
                    temp_galezie.append(pozycja[poziom]+1)
                    temp_wezly.append(galezie[pozycja[poziom]].wezel2)
                    poziom += 1

                elif (P[temp_wezly[poziom], pozycja[poziom]] == 1 and not(galezie[pozycja[poziom]].wezel1 in temp_wezly) and (pozycja[poziom] != i)):
                    temp_galezie.append(-pozycja[poziom]-1)
                    temp_wezly.append(galezie[pozycja[poziom]].wezel1)
                    poziom += 1

                else:
                    pozycja[poziom] += 1

                if temp_wezly[-1] == x.wezel1:
                    oczko = temp_galezie.copy()
                    oczko = sorted(oczko, key=abs)
                    oczko_neg = []
                    for y in oczko:
                        oczko_neg.append(-y)
                    if not(oczko in oczka or oczko_neg in oczka):
                        oczka.append(oczko) 
                    temp_galezie.pop()
                    temp_wezly.pop()
                    poziom -= 1
                    pozycja[poziom] += 1

        oczka.sort(key=len)

        # usunięcie pustych wierszów w macierzy połączeniowej oraz zmniejszenie liczby wezlchołków do realnej wartości
        P = P[~np.all(P==0, axis=1)]
        w = np.shape(P)[0]

        # PPK - prądowe prawo Kirchhoffa
        try:
            A[0:(w - 1), 0:(g)] = P[0:(w - 1), :]
        except:
            w = 1 

        # NPK - napięciowe prawo Kirchhofa
        oczka_len = len(oczka)
        tym_A = np.zeros((oczka_len, g))
        tym_B = np.zeros(oczka_len)
        for i, x in enumerate(oczka):
            for y in x:
                tym_A[i, abs(y)-1] = 1 if y>0 else -1
                tym_B[i] += galezie[abs(y)-1].SEM if y>0 else -galezie[abs(y)-1].SEM

        _, inds = sympy.Matrix(tym_A).T.rref()
        try:
            tym_A = tym_A [(inds), :]
            tym_B = tym_B [np.array(inds)]
            A[(w-1):g, g:(2*g)] = tym_A 
            B[(w-1):g] = tym_B
        except:
            pass

        # równania definicyjne - powiązanie napięć z prądami przez rezystancję gałęzi
        for i, x in enumerate(galezie):
            A[(i + g), i] = -x.R
            A[(i + g), (i + g)] = 1

        wynik = np.linalg.solve(A, B)
        I = []
        U = []
        # rysowanie wyniku
        for i, x in enumerate(wynik):
            if __name__ == "__main__":
                print("---------------------------------")
            if i < len(wynik)/2:
                I.append(x)
                if __name__ == "__main__":
                    print(f'I{i} = {x} [A]')
            else:
                U.append(x)
                if __name__ == "__main__":
                    print(f'U{i-g} = {x} [V]')

        return [I, U]

if __name__ == "__main__":
    o = obwod()
