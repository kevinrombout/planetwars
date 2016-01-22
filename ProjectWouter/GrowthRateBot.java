import java.util.*;

/* A bit smarter kind of bot, who searches for its strongest planet and then attacks the weakest planet.
 The score is computed based on the number of ships.
 */

public class BullyBot {
	public static void DoTurn(PlanetWars pw) {
		// (1) Find my strongest planet.
		Planet source = null;
		double sourceScore = Double.MIN_VALUE;
		for (Planet myPlanet : pw.MyPlanets()) {
			// skip planets with only one ship
			if (myPlanet.NumShips() <= 1){
				continue;
			}
			//This score is one way of defining how 'good' my planet is. 
			double score = (double) myPlanet.NumShips();
			if (score > sourceScore) {
				//we want to maximize the score, so store the planet with the best score
				sourceScore = score;
				source = myPlanet;
			}
		}
		
		//(2) Find the planets we can conquer
		int force = source.NumShips()/2;
		ArrayList<Planet> conquerableEnemies = conquerablePlanets(pw.EnemyPlanets(),force);
		ArrayList<Planet> conquerableNeutrals = conquerablePlanets(pw.NeutralPlanets(),force);
				
		//if there are no planets we can conquer, we just take all the planets. 		
		conquerableEnemies = (conquerableEnemies.size() == 0) ? pw.EnemyPlanets() : conquerableEnemies;
		conquerableNeutrals = (conquerableNeutrals.size() == 0) ? pw.NeutralPlanets() : conquerableNeutrals;
		
		// (3) Find the planet with the highest growth rate.
		Planet highestEnemy = highestGrowthRate(conquerableEnemies);
		Planet highestNeutral = highestGrowthRate(conquerableNeutrals);
		
		// (4) compare growthrates
		Planet dest = (highestEnemy.GrowthRate() + 1 >= highestNeutral)? highestEnemy : highestNeutral;
		
		// (5) Attack!
		if (source != null && dest != null) {
			pw.IssueOrder(source, dest);
		}
	}

	ArrayList<Planet> conquerablePlanets(ArrayList<Planet> NotMyPlanets, int force){
		ArrayList<Planet> result = new ArrayList<Planet>();
		for (Planet notMyPlanet : NotMyPlanets) {
			if(notMyPlanet.NumSchips() + 1 < force){ 
				result.add(notMyPlanet);
			}
		}
		return result;
	}
	
	Planet highestGrowthRate(ArrayList NotMyPlanets){
		Planet dest = null;
		double destScore = Double.MIN_VALUE;
		for (Planet notMyPlanet : NotMyPlanets) {
			double score = (double) (notMyPlanet.GrowthRate());
			if (score > destScore) {
				destScore = score;
				dest = notMyPlanet;
			}
		}
		return dest;
	}
	
	public static void main(String[] args) {
		String line = "";
		String message = "";
		int c;
		try {
			while ((c = System.in.read()) >= 0) {
				switch (c) {
				case '\n':
					if (line.equals("go")) {
						PlanetWars pw = new PlanetWars(message);
						DoTurn(pw);
						pw.FinishTurn();
						message = "";
					} else {
						message += line + "\n";
					}
					line = "";
					break;
				default:
					line += (char) c;
					break;
				}
			}
		} catch (Exception e) {
			// Owned.
		}
	}
}
