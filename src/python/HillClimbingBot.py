#!/usr/bin/env python

"""
HillClimbingBot - A bit smarter kind of bot, who searches for its strongest planet and then attacks the weakest planet.
The score is computed based on the number of ships.
"""
# Import the PlanetWars class from the PlanetWars module.
from PlanetWarsAPI import PlanetWars

def do_turn(pw):
    """@type pw: PlanetWars"""

    # The source variable will contain the planet from which we send the ships.
    source = 0
    # The dest variable will contain the destination, the planet to which we send the ships.
    dest = 0

    source_score = -1  # source score must be as large as possible (start with very low score)
    dest_score = 100000  # destination score must be as little as possible (start with high score)

    # Find my strongest planet (highest amount of ships)
    for my_planet in pw.my_planets():

        #we do not want to look at ships which only have 1 or less ships cause we can not qonquer any planet with it
        score_max_my_planet = my_planet.number_ships()

        if score_max_my_planet <= 1 :
            continue;

        if  source == 0:
            source_score    = score_max_my_planet
            source          = my_planet            
        elif score_max_my_planet > source_score and my_planet.growth_rate() < source.growth_rate:
            source_score    = score_max_my_planet
            source          = my_planet


    #find planets which we can conquer with our source planet
    conquerableNeutrals = conquerablePlanets(pw.neutral_planets(), source)
    conquerableOpponets = conquerablePlanets(pw.enemy_planets(), source)

    #find the planet with the biggest growthrate
    biggestNeutral      = biggestGrowthRate(conquerableNeutrals)
    biggestOpponent     = biggestGrowthRate(conquerableOpponets)

    #select the best candidate based on highest growthrate
    if biggestNeutral == 0:
        dest = biggestOpponent
    elif biggestOpponent == 0:
        dest = biggestNeutral
    elif biggestNeutral.growth_rate() > biggestOpponent.growth_rate():
        dest = biggestNeutral

    # Attack.
    # If the source and dest variables contain actual planets, then send half of the ships from source to dest.
    if source is not None and dest is not None:
        pw.issue_order(source, dest)


#used to find planets which can conquer based on the selected source planet
def conquerablePlanets(planets, source):
    attacking_ships = source.number_ships() / 2
    found_planets   = []
    for planet in planets:
        if planet.number_ships() < attacking_ships:
            found_planets.append(planet)
    return found_planets


#used to find planet with biggest growthrate based on input planets
def biggestGrowthRate(planets):
    biggest_planet = 0

    for planet in planets:
        if biggest_planet == 0:
            biggest_planet = planet
        elif planet.growth_rate() > biggest_planet.growth_rate():
             biggest_planet = planet
    return biggest_planet

# Don't change from this point on. Also not necessary to understand all the details.
# Machinery that reads the status of the game and puts it into PlanetWars.
# It calls do_turn.
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
