"""sophon.affect.eoe

Implements the Equation of Emotion (EOE) affective controller for SOPHON.
Motif: Module (affect/eoe)
Ports: [interface: affective controller, EOE, energy↔mass tuning, closure gain]
Invariants: [affective learning, energy↔structure conversion, closure optimization]
"""

import math

from typing import Tuple, Sequence

class Valuator:
    """Equation of Emotion affective controller."""

    def __init__(
        self,
        c2: float = 1.0,
        alpha: float = 0.2,
        beta: float = 0.05,
        lambdas: Sequence[float] = (1.0, 0.6, 0.3, 0.4)
    ) -> None:
        """
        c2: energy↔mass conversion constant
        alpha: consolidation rate (E → m)
        beta: release rate (m → E)
        lambdas: (valence, arousal, uncertainty, closure) weights
        """
        self.c2: float = c2
        self.alpha: float = alpha
        self.beta: float = beta
        self.lam: Sequence[float] = lambdas

    def eoe(self, EP: float, P: float) -> Tuple[float, float, float]:
        """Compute ER, valence, arousal from expectation and perception."""
        ER: float = P - EP
        V: float = math.tanh(2.0 * ER)  # Valence: normalized error
        A: float = abs(ER)               # Arousal: magnitude
        return ER, V, A

    def priority(self, V: float, A: float, U: float, C: float) -> float:
        """Compute priority from valence, arousal, uncertainty, closure."""
        l1, l2, l3, l4 = self.lam
        return l1 * V + l2 * A + l3 * U + l4 * C

    def consolidate(self, E: float, m: float, rewards: Sequence[float]) -> Tuple[float, float]:
        """Convert energy to mass based on rewards (E → m)."""
        total_reward: float = sum(rewards)
        dE: float = -self.alpha * total_reward
        dM: float = -dE / self.c2
        return max(E + dE, 0.0), m + dM

    def release(self, E: float, m: float, dm: float) -> Tuple[float, float]:
        """Convert mass to energy (m → E)."""
        dm = min(dm, m)
        return E + self.c2 * dm, m - dm
