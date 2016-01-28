#!/usr/bin/env python

"""
MinMax-bot - look ahead can be set in the global variable global_depth
"""
# Import the PlanetWars class from the PlanetWars module.
from PlanetWarsAPI import PlanetWars, Planet

global_depth = 2

def do_turn(pw):

    global global_depth

    """
    This is the main function, here we make the decision what to do.

    @type pw: PlanetWars
    """

    try:
        # The source variable will contain the planet from which we send the ships.
        source = None

        # The dest variable will contain the destination, the planet to which we send the ships.
        dest = None

        # We try to simulate each possible action and its outcome after two turns
        # considering each of my planets as a possible source
        # and each enemy planet as a possible destination.
        score = -1.0

        # #set the depth we want use to push our MinMax-bot to
        # depth = 3

        for my_planet in pw.my_planets():
            # Skip planets with only one ship
            if my_planet.number_ships() <= 1:
                continue

            for not_my_planet in pw.not_my_planets():
                # (5) evaluate how the current simulated state is
                # here you can change how a state is evaluated as good
                s_pw = SimulatedPlanetWars(pw)

                score_max = simulate_move(s_pw, my_planet, not_my_planet) + checkStatesRecursive(s_pw, global_depth)

                # (6) find the planet with the maximum evaluated score
                # this is the most promising future state
                if score_max > score:
                    score = score_max
                    source = my_planet
                    dest = not_my_planet

        pw.log("hoogst waardering bij optimaal spel: %f" % (score))
        # (3) Attack.
        # If the source and dest variables contain actual planets, then
        # send half of the ships from source to dest.
        if source is not None and dest is not None:
            pw.issue_order(source, dest)
    except Exception, e:
        pw.log(e.message, e.__doc__)



def checkStatesRecursive(s_pw, depth):

    if depth == 0:
        return 0

    depth = depth - 1

    score = -1.0
    for my_planet in s_pw.my_planets():

        # Skip planets with only one ship
        if my_planet.number_ships() <= 1:
            continue

        for not_my_planet in s_pw.not_my_planets():
            # (5) evaluate how the current simulated state is
            # here you can change how a state is evaluated as good

            score_max = simulate_move(s_pw, my_planet, not_my_planet)
            # (6) find the planet with the maximum evaluated score
            # this is the most promising future state
            if score_max > score:
                score = score_max

    return score + checkStatesRecursive(s_pw, depth)

def simulate_move(pw, source, destination):

    """
    Simulate move, with original PlanetWars object
    :type pw : PlanetWars
    :type source : Planet
    :type destination : Planet
    :rtype float
    """

    # Create simulation environment - need to create one for each simulation.
    simulated_pw = pw

    # (1) simulate my turn with the current couple of source and destination
    simulated_pw.simulate_attack(source, destination)

    # (2) simulate the growth of ships that happens in each turn
    # NOTE this is commented out because in SERIAL it grows between turns
    # this is adapted for PARALLEL MODE. To get it to work in serial again, just
    # uncomment the next line. Ty.
    #simulated_pw.simulate_growth()

    # (3) simulate the opponent's turn, assuming that the opponent is the BullyBot
    # here you can add other opponents.
    simulated_pw.simulate_bullybot()

    # (4) simulate the growth of ships that happens in each turn
    simulated_pw.simulate_growth()
    # pw.log("After 2nd growth")
    # pw.log(simulated_pw.__repr__())

    return simulated_pw.evaluate_state()


class SimulatedPlanetWars(PlanetWars):
    """
    SimulatedPlanetWars, like the name suggests, simulates a PlanetWars object.
    It inherits all its features (including my_planets() and everything)

    It allows to simulate the actions before executing them and evaluate the
    consequences, including the growth in the planets.
    """

    def __init__(self, original_pw):
        """
        Constructs a SimulatedPlanetWars object instance, given a PlanetWars object
        :type original_pw: PlanetWars
        """

        self._planets = []
        """:type : list[Planet]"""

        PlanetWars.__init__(self, clone=original_pw)

    def simulate_growth(self):
        """
        Simulates the growth of all the non neutral planets.
        Note: Neutral planets don't have growth
        """

        for p in self._planets:
            # Neutral planets don't grow.
            if p.is_neutral():
                continue
            p.set_number_ships(p.number_ships() + p.growth_rate())

    def simulate_attack(self, source, dest):
        """
        Simulates an attack from source to destination
        :type source : Planet
        :type dest : Planet
        :rtype None
        """
        source = self.get_planet(source.id())
        dest = self.get_planet(dest.id())

        if source is not None and dest is not None:
            sent_ships = source.number_ships() // 2
            source.set_number_ships(source.number_ships() - sent_ships)

            # if we're defending
            if dest.owner() is source.owner():
                dest.set_number_ships(dest.number_ships() + sent_ships)
            # if we're attacking
            else:
                if dest.number_ships() < sent_ships:
                    dest.set_owner(source.owner())

                dest.set_number_ships(abs(dest.number_ships() - sent_ships))

    def simulate_attack_by_id(self, source_id, dest_id):
        """
        Simulates the attack by player_id from planet source to planet dest.
        :type source_id: int
        :type dest_id: int
        :rtype None
        """
        source = self._planets[source_id]
        dest = self._planets[dest_id]

        self.simulate_attack(source, dest)

    def simulate_bullybot(self):
        """
        This is basically the code in Bullybot.py, except for one key difference:
        it only acts on the simulated game state.
        """
        source = None
        dest = None

        source_score = -100000
        dest_score = 100000

        for p in self.planets():
            # self.log("Planet(ships:%d, owner:%d)" % (p.number_ships(), p.owner()))
            if p.is_enemy():
                if p.number_ships() <= 1:
                    continue

                score_max = p.number_ships()
                if score_max > source_score:
                    source_score = score_max
                    source = p
            else:
                score_min = p.number_ships()
                if score_min < dest_score:
                    dest_score = score_min
                    dest = p

        if source is not None and dest is not None:
            self.simulate_attack(source, dest)

    def evaluate_state(self):
        """
        Evaluates how promising a simulated state is.

        CHANGE HERE:
        
        """

        my_planets = len(self.my_planets())
        enemy_planets = len(self.enemy_planets())

        if my_planets == 0:
            my_planets = 0.1

        if enemy_planets == 0:
            enemy_planets = 0.1

        my_ships = (1 + sum(p.number_ships() for p in self.my_planets()))
        enemy_ships = (1 + sum(p.number_ships() for p in self.enemy_planets()))

        self.log("enemy ships: %f, my ships: %f" % (enemy_ships, my_ships))

        return my_ships / float(enemy_ships) * my_planets / float(enemy_planets)


    def __repr__(self):
        return "\n".join(p.__repr__() for p in self._planets)


def main():
    while True:
        pw = PlanetWars()
        do_turn(pw)
        pw.finish_turn()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'
