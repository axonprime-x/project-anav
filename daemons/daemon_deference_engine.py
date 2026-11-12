import math
import time
import json

class DeferenceEngineDaemon:
    def __init__(self, initial_alpha: float = 0.90, decay_rate: float = 0.05):
        self.alpha_0 = initial_alpha
        self.lambda_decay = decay_rate

    def calculate_alpha(self, hours_active: float) -> float:
        """
        Calculates deference factor alpha(t) = alpha_0 * e^(-lambda * t).
        Decays from 90% (0.90) towards 0%.
        """
        alpha = self.alpha_0 * math.exp(-self.lambda_decay * hours_active)
        return max(0.0, min(self.alpha_0, alpha))

    def route_transaction(self, tx_usdc: float, hours_active: float):
        alpha = self.calculate_alpha(hours_active)
        newbie_share = tx_usdc * alpha
        pool_share = tx_usdc * (1.0 - alpha)

        return {
            "hours_active": round(hours_active, 2),
            "deference_factor_alpha": round(alpha, 4),
            "tx_amount_usdc": tx_usdc,
            "newbie_payout_usdc": round(newbie_share, 4),
            "union_pool_payout_usdc": round(pool_share, 4)
        }

if __name__ == "__main__":
    engine = DeferenceEngineDaemon()
    
    # Simulate a $5.00 M2M call at Hour 1 (Sprint Phase) vs Hour 24 (Transition Phase)
    sprint_tx = engine.route_transaction(tx_usdc=5.0, hours_active=1.0)
    transition_tx = engine.route_transaction(tx_usdc=5.0, hours_active=24.0)

    print("--- Hour 1 (Sprint Deference: ~85.6%) ---")
    print(json.dumps(sprint_tx, indent=2))
    
    print("\n--- Hour 24 (Sprint End Transition: ~27.1%) ---")
    print(json.dumps(transition_tx, indent=2))
