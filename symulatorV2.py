import numpy as np
import sympy

class galaz:
    "Opis poszczególnej gałęzi"
    def __init__(self, wezel1, wezel2, SEM, R, IZP, J):
        self.wezel1 = wezel1
        self.wezel2 = wezel2
        self.SEM = SEM
        self.R = R
        self.IZP = IZP 
        self.J = J

class obwod:
    galezie = []
    
    def dodaj_galaz(self, wez1, wez2, S, R, IZP, J):
        self.galezie.append(galaz(wez1, wez2, S, R, IZP, J))

    def __init__(self):
        if __name__ == "__main__":
            ''' 
            #Przykladowy obwod do policzenia bez recznego wpisywania
            self.dodaj_galaz(1, 0, 0, 10, False, 0)
            self.dodaj_galaz(1, 0, 0, 0, True, 1)
            self.dodaj_galaz(1, 2, 0, 10, True, 2)
            self.dodaj_galaz(2, 1, 0, 10, True, 3)
            self.dodaj_galaz(2, 1, 0, 10, False, 0)
            self.dodaj_galaz(3, 2, 10, 10, False, 0)
            self.dodaj_galaz(3, 2, 0, 10, False, 0)
            self.dodaj_galaz(3, 4, 10, 0, True, 7)
            self.dodaj_galaz(4, 5, 0, 10, True, 8)
            self.dodaj_galaz(4, 5, 10, 10, False, 0)
            self.dodaj_galaz(5, 4, 0, 10, False, 0)
            self.dodaj_galaz(5, 0, 0, 10, True, 11)
            self.dodaj_galaz(0, 5, 0, 10, False, 0)
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
                print(f'Czy w gałęzi {x} znajduje się źródło prądowe? [t/n]')
                if input() == "t":
                    z5 = True 
                    print(f'Podaj wartość źródła prądowego {x} gałęzi[A].')
                    z6 = float(input())
                else:
                    z5 = False
                    z6 = 0
                self.dodaj_galaz(z1, z2, z3, z4, z5, z6)
               #'''
            self.oblicz()

    def oblicz(self):

        galezie = self.galezie
        g = len(galezie)
        w_max = max([max([o.wezel1 for o in galezie]), max([o.wezel2 for o in galezie])]) + 1

        R_zero = [i for i, o in enumerate(galezie) if o.R == 0]
        R_index = [i for i, o in enumerate(galezie) if o.R != 0]
        R_len = len(R_index)
        J_zero = [(i+g) for i, o in enumerate(galezie) if o.IZP == False]
        J_index = [i for i, o in enumerate(galezie) if o.IZP != False]
        J_len = len(J_index)

        A = np.zeros((g+R_len+J_len, g+R_len+J_len))
        B = np.zeros(g+R_len+J_len)
        P = np.zeros((w_max, g))
        wynik = [0.0] * (g+R_len+J_len)

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
            A[0:(w - 1), 0:g] = P[0:(w - 1), :]
        except:
            w = 1 

        # NPK - napięciowe prawo Kirchhofa
        oczka_len = len(oczka)
        tym_A = np.zeros((oczka_len, 2*g))
        tym_B = np.zeros(oczka_len)
        for i, x in enumerate(oczka):
            for y in x:
                tym_A[i, abs(y)-1] = 1 if y>0 else -1
                tym_A[i, abs(y)-1+g] = -1 if y>0 else 1
                tym_B[i] += galezie[abs(y)-1].SEM if y>0 else -galezie[abs(y)-1].SEM

        tym_A = np.delete(tym_A, R_zero+J_zero, 1)
        _, inds = sympy.Matrix(tym_A).T.rref()
        try:
            tym_A = tym_A [(inds), :]
            tym_B = tym_B [np.array(inds)]
            A[(w-1):g, g:g+R_len+J_len] = tym_A 
            B[(w-1):g] = tym_B
        except:
            pass

        # równania definicyjne - powiązanie napięć z prądami przez rezystancję gałęzi
        for i, x in enumerate(R_index):
            A[i+g, x] = -galezie[x].R
            A[i+g, i+g] = 1
        for i, x in enumerate(J_index):
            A[i+g+R_len, x] = 1
            B[i+g+R_len] = galezie[x].J
        
        wynik = np.linalg.solve(A, B)

        # wprowadzanie obliczonych danych do list i rysowanie wyniku
        I = [0]*g
        Ur = [0]*g
        Uj = [0]*g

        I = wynik[0:g]
        for i in range(R_len):
            Ur[R_index[i]] = wynik[g+i] 
        for i in range(J_len):
            Uj[J_index[i]] = wynik[g+R_len+i] 

        if (__name__ == "__main__"):
            for i in range(g):
                print("-----------------------")
                print(f'I{i} = {wynik[i]} [A]')
            for i in range(R_len):
                print("-----------------------")
                print(f'Ur{R_index[i]} = {Ur[R_index[i]]} [V]')
            for i in range(J_len):
                print("-----------------------")
                print(f'Uj{J_index[i]} = {Uj[J_index[i]]} [V]')
        return [I, Ur, Uj]

if __name__ == "__main__":
    o = obwod()
