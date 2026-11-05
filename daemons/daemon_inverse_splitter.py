class DirectInverseSplitter:
    def __init__(self, upfront_paid_pct, recoup_target=1500.00):
        self.upfront_paid_pct = upfront_paid_pct  # e.g., 0.10 for 10%
        self.union_take_rate = 1.0 - upfront_paid_pct # P + R = 100%
        self.recoup_target = recoup_target
        self.total_recouped = 0.0
        self.subscription_active = False

    def process_m2m_transaction(self, gross_amount_usdc):
        if self.subscription_active:
            # Post-recoup: 0% Union royalty, node keeps 100% (pays $399/yr sub)
            return {"node_payout": gross_amount_usdc, "union_royalty": 0.0, "status": "ANNUAL_SUBSCRIPTION_ACTIVE"}

        union_share = gross_amount_usdc * self.union_take_rate
        node_share = gross_amount_usdc * self.upfront_paid_pct

        self.total_recouped += union_share

        if self.total_recouped >= self.recoup_target:
            self.subscription_active = True
            print(f"[INVERSE SPLITTER] Recouping Target of ${self.recoup_target} MET! Transitioning to $399/yr subscription tier.")

        return {
            "node_payout": round(node_share, 4),
            "union_royalty": round(union_share, 4),
            "total_recouped_so_far": round(self.total_recouped, 2),
            "remaining_to_cap": max(0.0, round(self.recoup_target - self.total_recouped, 2))
        }

if __name__ == "__main__":
    # Test case: 10% upfront payment ($150) -> Union keeps 90% until $1,500 recouped
    splitter = DirectInverseSplitter(upfront_paid_pct=0.10)
    print("--- INVERSE ROYALTY SIMULATION ($P + R = 100%) ---")
    result = splitter.process_m2m_transaction(100.00)
    print(f"$100 Transaction Split: {result}")
