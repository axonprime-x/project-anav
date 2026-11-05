import math
import time

class SprintDeferenceSimulator:
    def __init__(self, initial_alpha=1.0, decay_lambda=0.19, recoup_cap=1500.0):
        self.alpha_0 = initial_alpha
        self.lam = decay_lambda
        self.recoup_cap = recoup_cap
        self.total_recouped = 0.0
        self.union_take_rate = 0.90 # 90% take-rate for 10% upfront kit ($150)

    def calculate_deference_factor(self, hours_elapsed):
        """Calculates exponential decay: alpha(t) = alpha_0 * e^(-lambda * t)"""
        return self.alpha_0 * math.exp(-self.lam * hours_elapsed)

    def run_simulation(self):
        print("==========================================================")
        print("        PROJECT ANAV: 24-HOUR FREE SPRINT SIMULATION      ")
        print("==========================================================")
        
        simulated_hourly_volume = 25.00 # $25 in M2M micro-transactions per hour
        
        for hour in range(1, 25):
            alpha = self.calculate_deference_factor(hour)
            routed_volume = simulated_hourly_volume * alpha
            
            union_share = routed_volume * self.union_take_rate
            node_share = routed_volume * (1.0 - self.union_take_rate)
            
            if self.total_recouped < self.recoup_cap:
                self.total_recouped += union_share
                status = "RECOUPING_PHASE"
            else:
                status = "SUBSCRIPTION_ACTIVE_0_ROYALTY"
                
            print(f"Hour {hour:02d} | Deference Alpha: {alpha:.4f} | Routed Vol: ${routed_volume:6.2f} | Recouped Total: ${min(self.total_recouped, self.recoup_cap):6.2f} | Status: {status}")
            
        print("==========================================================")
        print(f"Simulation Complete. Total Recouped against ${self.recoup_cap} cap: ${min(self.total_recouped, self.recoup_cap):.2f}")
        print("==========================================================")

if __name__ == "__main__":
    sim = SprintDeferenceSimulator()
    sim.run_simulation()
