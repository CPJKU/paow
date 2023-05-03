
import numpy as np

from paow.utils import Chord, Progression

class Optimizer:
    def __init__(self) -> None:
        pass    
    def modify(self, population):
        # add an accidental
        subpop3 = np.random.choice(population, 30)
        for element in subpop3:
            cidx = np.random.randint(len(element.chords))
            nidx = np.random.randint(4)
            mod = np.random.choice([-1,1])
            new_element = Progression(element.chords)
            new_element.chords[cidx].add_repitch(nidx,mod)
            population.append(new_element)
        
        # invert a chord
        subpop4 = np.random.choice(population, 30)
        for element in subpop4:
            cidx = np.random.randint(len(element.chords))
            nidx = np.random.randint(4)
            new_element = Progression(element.chords)
            new_element.chords[cidx].invert(nidx)
            population.append(new_element)
            
        # join some elements
        subpop1 = np.random.choice(population, 30)
        subpop2 = np.random.choice(population, 30)
        for element0, element1 in zip(subpop1, subpop2):
            elnew1, elnew2 = element0.join(element1)
        
            population.append(elnew1)
            population.append(elnew2)
        
        return population

    
    def select(self, population, n):



    def run(self,
            epochs = 50,
            population_size = 100,
            population_replacement = 0.3,
            new_population = True):
        if new_population:
            population = [Progression() for po in range(population_size)]    
        else:
            population = self.population
        


        for epoch in range(epochs): 
            population = self.modify(population)
            population, sorted_fitness = self.select(population, int(population_replacement * population_size)) 
            print(f"Epoch {epoch} best fitness: {sorted_fitness[0]:.4f}")
            population += [Progression() for po in range(population_size - len(population))]


        self.population = population
        return population[0]
    