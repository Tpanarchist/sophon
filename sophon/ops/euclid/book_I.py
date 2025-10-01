"""sophon.ops.euclid.book_I

Implements Book I operations (propositions, constructions, proofs) from Euclid's Elements for SOPHON.
Motif: Module (ops/euclid/book_I)
Ports: [interface: Book I Ops, Propositions, Proofs]
Invariants: [axiomatic correctness, composability]
"""

from typing import Any, List, Tuple
from sophon.ops.registry import Op, Registry
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType, EdgeType
import math
import logging

logger = logging.getLogger(__name__)

class BookIProp1Op(Op):
    name = "BookI.Prop1"
    cost = 1.0

    def precond(self, graph: HyperGraph) -> List[Tuple[int]]:
        """Return list of valid (line_id,) tuples for this op."""
        valid_inputs = []
        lines, _ = graph.by_type(NodeType.LINE)
        for line in lines:
            logger.debug("PRECOND Checking LINE node %s attr=%s", line.id, line.attr)
            if 'p1' in line.attr and 'p2' in line.attr:
                p1 = graph.nodes.get(line.attr['p1'])
                p2 = graph.nodes.get(line.attr['p2'])
                logger.debug("p1=%s, p2=%s", p1, p2)
                if (p1 and p2 and
                    'x' in p1.attr and 'y' in p1.attr and
                    'x' in p2.attr and 'y' in p2.attr):
                    logger.debug("Valid input: (%s,)", line.id)
                    valid_inputs.append((line.id,))
                else:
                    logger.debug("Invalid: missing coords")
            else:
                logger.debug("Invalid: missing p1/p2")
        return valid_inputs

    def apply(self, graph: HyperGraph, line_id: int) -> dict:
        # Construct equilateral triangle on given segment
        line = graph.nodes[line_id]
        p1 = graph.nodes[line.attr['p1']]
        p2 = graph.nodes[line.attr['p2']]
        x1, y1 = p1.attr['x'], p1.attr['y']
        x2, y2 = p2.attr['x'], p2.attr['y']

        # Construct third point using rotation (60 degrees)
        dx = x2 - x1
        dy = y2 - y1
        angle = math.pi / 3
        x3 = x1 + dx * math.cos(angle) - dy * math.sin(angle)
        y3 = y1 + dx * math.sin(angle) + dy * math.cos(angle)

        # Add point C
        p3_id = graph.add_node(NodeType.POINT, {'x': x3, 'y': y3, 'name': 'C'})

        # Add sides AC and BC
        ac_id = graph.add_node(NodeType.LINE, {'p1': line.attr['p1'], 'p2': p3_id})
        bc_id = graph.add_node(NodeType.LINE, {'p1': line.attr['p2'], 'p2': p3_id})

        # Add construction edges
        graph.add_edge(EdgeType.CONSTRUCTION, (line_id, p3_id, ac_id, bc_id))

        # Add proposition
        prop_id = graph.add_node(NodeType.PROPOSITION, {
            'text': f'Triangle ABC is equilateral',
            'status': 'derived'
        })

        return {'triangle_point': p3_id, 'proposition': prop_id, 'ac': ac_id, 'bc': bc_id, 'ab': line_id}

    def invariants(self, graph: HyperGraph, outputs: dict) -> bool:
        # Check: three sides are equal within tolerance
        if not isinstance(outputs, dict):
            return False
        try:
            p1 = graph.nodes[graph.nodes[outputs['ab']].attr['p1']]
            p2 = graph.nodes[graph.nodes[outputs['ab']].attr['p2']]
            p3 = graph.nodes[outputs['triangle_point']]
            def dist(a, b):
                return math.hypot(a.attr['x'] - b.attr['x'], a.attr['y'] - b.attr['y'])
            d1 = dist(p1, p2)
            d2 = dist(p1, p3)
            d3 = dist(p2, p3)
            tol = 1e-6
            return abs(d1 - d2) < tol and abs(d2 - d3) < tol and abs(d1 - d3) < tol
        except Exception:
            return False

REGISTRY = Registry()
REGISTRY.add(BookIProp1Op())
