
import random
import time
from collections import defaultdict

from networkx import config

# MYCELLIUM V0.1
# Decentralized supply-demand negotiation and failure recovery

rng = random.Random(42)

# 8 suppliers + 12 demand nodes = 20 autonomous agents
suppliers = {
    f"S{i}": rng.randint(16, 22)
    for i in range(8)
}

buyers = {
    f"D{i}": rng.randint(6, 10)
    for i in range(12)
}

# Each buyer knows only four neighboring suppliers.
# Each connection has a different transaction cost.
neighbors = {}
costs = {}

for buyer in buyers:
    neighbors[buyer] = rng.sample(list(suppliers), 4)
    for supplier in neighbors[buyer]:
        costs[(supplier, buyer)] = rng.randint(1, 10)


def negotiate(allocations, active_suppliers):
    """Nodes negotiate locally until no more trades are possible."""

    allocations = allocations.copy()
    rounds = 0

    while rounds < 50:
        rounds += 1

        used_supply = defaultdict(int)
        filled_demand = defaultdict(int)

        for (supplier, buyer), amount in allocations.items():
            used_supply[supplier] += amount
            filled_demand[buyer] += amount

        # Buyers send requests to their cheapest available neighbor.
        offers = defaultdict(list)

        for buyer, demand in buyers.items():
            needed = demand - filled_demand[buyer]
            if needed <= 0:
                continue

            available = [
                s for s in neighbors[buyer]
                if s in active_suppliers
                and used_supply[s] < suppliers[s]
            ]

            if available:
                supplier = min(available, key=lambda s: costs[(s, buyer)])
                offers[supplier].append((buyer, needed))

        progress = 0

        # Each supplier independently evaluates incoming requests.
        for supplier, requests in offers.items():
            remaining = suppliers[supplier] - used_supply[supplier]

            # Prioritize buyers with the largest unmet demand.
            requests.sort(key=lambda item: -item[1])

            for buyer, needed in requests:
                accepted = min(needed, remaining)

                if accepted > 0:
                    key = (supplier, buyer)
                    allocations[key] = allocations.get(key, 0) + accepted
                    remaining -= accepted
                    progress += accepted

                if remaining == 0:
                    break

        if progress == 0:
            break

    return allocations, rounds


def report(title, allocations, rounds):
    delivered = sum(allocations.values())
    total_demand = sum(buyers.values())
    cost = sum(
        amount * costs[(supplier, buyer)]
        for (supplier, buyer), amount in allocations.items()
    )

    print(f"\n{title}")
    print("-" * 40)
    print(f"Demand served: {delivered}/{total_demand}")
    print(f"Unmet demand: {total_demand - delivered}")
    print(f"Allocation cost: {cost}")
    print(f"Negotiation rounds: {rounds}")


print("MYCELLIUM V0.1")
print("Initializing 20-node network...")

# Phase 1: Normal conditions
start = time.perf_counter()

initial, rounds = negotiate({}, set(suppliers))

initial_time = time.perf_counter() - start
report("NORMAL NETWORK", initial, rounds)

# Phase 2: Remove the most heavily utilized supplier.
utilization = defaultdict(int)

for (supplier, buyer), amount in initial.items():
    utilization[supplier] += amount

failed_node = max(utilization, key=utilization.get)
print(f"\nDISRUPTION: Supplier {failed_node} has failed!")

# Preserve all surviving allocations.
remaining_allocations = {
    (supplier, buyer): amount
    for (supplier, buyer), amount in initial.items()
    if supplier != failed_node
}

lost_units = sum(initial.values()) - sum(remaining_allocations.values())

# Phase 3: Surviving nodes renegotiate.
start = time.perf_counter()

recovered, recovery_rounds = negotiate(
    remaining_allocations,
    set(suppliers) - {failed_node}
)

recovery_time = time.perf_counter() - start

report("RECOVERED NETWORK", recovered, recovery_rounds)

restored_units = sum(recovered.values()) - sum(remaining_allocations.values())

print("\nRECOVERY RESULTS")
print("-" * 40)
print(f"Units disrupted: {lost_units}")
print(f"Units restored: {restored_units}")
print(f"Recovery computation time: {recovery_time:.6f} seconds")

# Check basic conservation rules.
assert all(s != failed_node for s, b in recovered)

for supplier in suppliers:
    used = sum(
        amount for (s, b), amount in recovered.items()
        if s == supplier
    )
    assert used <= suppliers[supplier]

for buyer in buyers:
    filled = sum(
        amount for (s, b), amount in recovered.items()
        if b == buyer
    )
    assert filled <= buyers[buyer]

print("\nSimulation complete. All allocation checks passed.")

git config --global user.name "assougdamyassine-max"
git config --global user.email "assougdamyassine@gmail.com"
git config --global --list

