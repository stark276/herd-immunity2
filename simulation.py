import random, sys
random.seed(42)
from person import Person
from logger import Logger
from virus import Virus


class Simulation(object):

    def __init__(self, pop_size, vacc_percentage, virus, initial_infected=1):

        self.pop_size = pop_size # Int
        self.next_person_id = 1 # Int
        self.virus = virus # Virus object
        self.alive_for_vaccinations = 0
        self.initial_infected = initial_infected # Int
        self.total_infected = 0 # Int
        self.current_infected = 0 # Int
        self.vacc_percentage = vacc_percentage # float between 0 and 1
        self.total_dead = 0 # Int
        self.newly_infected = []
        self.population = self._create_population(self.initial_infected) # List of Person objects
        self.file_name = "_virus_name_{}_simulation_pop_{}_vp_{}_infected_{}.txt".format(
            self.virus.name, pop_size, vacc_percentage, initial_infected)
        self.logger = Logger(self.file_name)

    def _create_population(self, initial_infected):

        population = []

        for i in range(self.initial_infected):
            infected_person = Person(self.next_person_id, False, self.virus) # Creating a Person object
            self.next_person_id += 1
            population.append(infected_person)

        for i in range(int(self.vacc_percentage * self.pop_size)):
            vaccinated_person = Person(self.next_person_id, True)
            self.next_person_id += 1
            population.append(vaccinated_person)

        for i in range(self.pop_size - self.initial_infected - int(self.vacc_percentage * self.pop_size)):
            unvaccinated_person = Person(self.next_person_id, False)
            self.next_person_id += 1
            population.append(unvaccinated_person)

        return population
        

    def _simulation_should_continue(self):

        vaccinated_count = 0
        total_dead_count = 0
        infected_count = 0

        for person in self.population:
            if person.is_alive and person.is_vaccinated:
                vaccinated_count += 1
            if not person.is_alive:
                total_dead_count += 1
            if person.infection:
                infected_count += 1
        # DEAD OR NOT INFECTED
        if self.total_dead == self.pop_size or infected_count == 0:
            return False
        # VACCINATED
        if vaccinated_count == self.pop_size - total_dead_count:
            return False
        return True
        print(self.total_dead)
    def run(self):

        time_step_counter = 0
        should_continue = self._simulation_should_continue()

        while should_continue:
            self.time_step()
            self._infect_newly_infected()
            time_step_counter += 1
            should_continue = self._simulation_should_continue()

        print('The simulation has ended after {} turns.'.format(time_step_counter))
        print(self.alive_for_vaccinations)

    def time_step(self):

        interaction_count = 0
        for person in self.population:
            if person.infection == self.virus and person.is_alive:
                while interaction_count < 100:
                    random_person = random.choice(self.population)
                    if random_person.is_alive and random_person._id != person._id:
                        interaction_count += 1
                        self.interaction(person, random_person)
                interaction_count = 0

        for person in self.population:
            if person.is_alive and person.infection:
                if person.did_survive_infection():
                    self.logger.log_infection_survival(person, False)
                else:
                    self.logger.log_infection_survival(person, True)
                    self.total_dead += 1

    def interaction(self, person, random_person):

        assert person.is_alive == True
        assert random_person.is_alive == True

        
        if random_person.is_vaccinated is True:
            self.alive_for_vaccinations += 1
            self.logger.log_interaction(person, random_person, None, True, None)
        elif random_person.infection is True:
            self.logger.log_interaction(person, random_person, True, None, None)
        else:
            if self.virus.repro_rate >= random.random():
                self.newly_infected.append(random_person._id)
                self.total_infected += 1
                self.logger.log_interaction(person, random_person, None, None, True)
            else:
                self.logger.log_interaction(person, random_person)



    def _infect_newly_infected(self):

        for person in self.population:
            for id in self.newly_infected:
                if person._id == id:
                    person.infection = self.virus
                    self.current_infected += 1
        self.newly_infected  = []


if __name__ == "__main__":
    params = sys.argv[1:]
    virus_name = str(params[2])
    repro_num = float(params[3])
    mortality_rate = float(params[4])

    pop_size = int(params[0])
    vacc_percentage = float(params[1])

    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1

    virus = Virus(virus_name, repro_num, mortality_rate)
    sim = Simulation(pop_size, vacc_percentage, virus, initial_infected)

    sim.run()
