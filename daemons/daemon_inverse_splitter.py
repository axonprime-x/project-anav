import json

class InverseSplitterEngine:
    def __init__(self, cap_target_usd: float = 1500.0, yearly_sub_usd: float = 399.0):
        self.cap_target = cap_target_usd
        self.yearly_sub = yearly_sub_usd

    def calculate_split(self, upfront_paid_usd: float, total_recouped_usd: float):
        if total_recouped_usd >= self.cap_target:
            return {
                "union_take_rate": 0.0,
                "entrant_take_rate": 1.0,
                "status": "CAP_REACHED_YEARLY_SUB_ACTIVE"
            }

        p_fraction = min(1.0, max(0.0, upfront_paid_usd / self.cap_target))
        union_take_rate = 1.0 - p_fraction
        entrant_take_rate = p_fraction

        return {
            "union_take_rate": union_take_rate,
            "entrant_take_rate": entrant_take_rate,
            "status": "RECOUPING_KIT_BALANCE"
        }

    def process_tx(self, tx_usdc: float, upfront_paid: float, current_recouped: float):
        split = self.calculate_split(upfront_paid, current_recouped)
        union_cut = tx_usdc * split["union_take_rate"]
        entrant_cut = tx_usdc * split["entrant_take_rate"]
        new_recouped_total = min(self.cap_target, current_recouped + union_cut)

        return {
            "tx_amount_usdc": tx_usdc,
            "status": split["status"],
            "union_cut_usdc": round(union_cut, 4),
            "entrant_cut_usdc": round(entrant_cut, 4),
            "updated_total_recouped_usdc": round(new_recouped_total, 4)
        }

if __name__ == "__main__":
    engine = InverseSplitterEngine()
    # Test case: Entrant paid 10% down ($150), Union takes 90%
    res = engine.process_tx(tx_usdc=25.0, upfront_paid=150.0, current_recouped=100.0)
    print(json.dumps(res, indent=2))
