from simulation import Simulation

if __name__ == "__main__":
    simulation = Simulation()

    simulation.initiate()

    while simulation.running:
        simulation.simulation_loop()
