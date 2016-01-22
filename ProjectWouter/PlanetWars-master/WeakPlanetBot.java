import java.util.ArrayList;
import java.util.List;

public class WeakPlanetBot {
	public static void DoTurn(PlanetWars pw) {
		// (1) Find my strongest planet.
		Planet source = null;
		Planet dest = null;
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

		//(2)Find Last Neutral Attacked Planet
		int force = source.NumShips()/2;
		if(pw.getAttackedPlanets().size() != 0){
			Planet possibleDest = pw.getLastNeutralAttackedPlanet();
			if(possibleDest.NumShips() + possibleDest.GrowthRate() + 1 < force){
				dest = possibleDest;
			}
		} 
		if(dest == null){ //Do Growth Rate Attack

			//(3) Find the planets we can conquer
			List<Planet> conquerableEnemies = conquerablePlanets(pw.EnemyPlanets(),force);
			List<Planet> conquerableNeutrals = conquerablePlanets(pw.NeutralPlanets(),force);

			//if there are no planets we can conquer, we just take all the planets.
			if((conquerableEnemies.size() == 0) && (conquerableNeutrals.size() == 0)){
				conquerableEnemies = pw.EnemyPlanets();
				conquerableNeutrals = pw.NeutralPlanets();
			}

			// (4) Find the planet with the highest growth rate.
			Planet highestEnemy = highestGrowthRate(conquerableEnemies);
			Planet highestNeutral = highestGrowthRate(conquerableNeutrals);

			// (5) compare growthrates
			if(highestEnemy == null){
				dest = highestNeutral;
			} else if(highestNeutral == null){
				dest = highestEnemy;
			} else {
				dest = (highestEnemy.GrowthRate() + 1 >= highestNeutral.GrowthRate())? highestEnemy : highestNeutral;
			}
		}
		// (5) Attack!
		if (source != null && dest != null) {
			pw.IssueOrder(source, dest);
		}
	}

	static ArrayList<Planet> conquerablePlanets(List<Planet> NotMyPlanets, int force){
		ArrayList<Planet> result = new ArrayList<Planet>();
		for (Planet notMyPlanet : NotMyPlanets) {
			if(notMyPlanet.NumShips() + notMyPlanet.GrowthRate() + 1 < force){ 
				System.err.println("NMP: " +notMyPlanet.NumShips()+ " FRC: "+ force);
				System.err.flush();
				result.add(notMyPlanet);
			}
		}
		return result;
	}

	static Planet highestGrowthRate(List<Planet> NotMyPlanets){
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
