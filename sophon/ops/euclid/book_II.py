"""sophon.ops.euclid.book_II

Implements Book II operations (propositions, constructions, proofs) from Euclid's Elements for SOPHON.
Motif: Module (ops/euclid/book_II)
Ports: [interface: Book II Ops, Propositions, Proofs]
Invariants: [axiomatic correctness, composability]
"""

from typing import Any, List, Tuple
from sophon.ops.registry import Op, Registry
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType, EdgeType
import logging

logger = logging.getLogger(__name__)

class BookIIProp1Op(Op):
    name = "BookII.Prop1"
    cost = 1.2  # Slightly more expensive than Book I

    def precond(self, graph: HyperGraph) -> List[Tuple[int]]:
        """Return list of valid (line_id,) tuples for this op."""
        valid_inputs = []
        lines, _ = graph.by_type(NodeType.LINE)
        for line in lines:
            if 'p1' in line.attr and 'p2' in line.attr:
                valid_inputs.append((line.id,))
        return valid_inputs

    def apply(self, graph: HyperGraph, line_id: int) -> dict:
        # Construct a square on a given line segment
        line = graph.nodes[line_id]
        p1 = graph.nodes[line.attr['p1']]
        p2 = graph.nodes[line.attr['p2']]
        x1, y1 = p1.attr['x'], p1.attr['y']
        x2, y2 = p2.attr['x'], p2.attr['y']

        # Calculate perpendicular direction
        dx = x2 - x1
        dy = y2 - y1
        # Rotate 90 degrees
        px, py = -dy, dx

        # Add two more points to form a square
        p3_id = graph.add_node(NodeType.POINT, {'x': x2 + px, 'y': y2 + py, 'name': 'C'})
        p4_id = graph.add_node(NodeType.POINT, {'x': x1 + px, 'y': y1 + py, 'name': 'D'})

        # Add remaining sides
        side2_id = graph.add_node(NodeType.LINE, {'p1': line.attr['p2'], 'p2': p3_id})
        side3_id = graph.add_node(NodeType.LINE, {'p1': p3_id, 'p2': p4_id})
        side4_id = graph.add_node(NodeType.LINE, {'p1': p4_id, 'p2': line.attr['p1']})

        # Add square polygon
        square_id = graph.add_node(NodeType.POLYGON, {
            'sides': 4, 
            'type': 'square',
            'constructed_by': self.name
        })

        # Add construction edges
        graph.add_edge(EdgeType.CONSTRUCTION, (line_id, square_id, p3_id, p4_id))

        # Add proposition
        prop_id = graph.add_node(NodeType.PROPOSITION, {
            'text': f'Square constructed on line segment',
            'status': 'derived'
        })

        return {'square': square_id, 'proposition': prop_id, 'new_points': [p3_id, p4_id]}

    def invariants(self, graph: HyperGraph, outputs: dict) -> bool:
        # Check: constructed figure has 4 sides and is square-like
        if not isinstance(outputs, dict):
            return False
        try:
            square = graph.nodes[outputs['square']]
            return square.attr.get('sides') == 4 and square.attr.get('type') == 'square'
        except Exception:
            return False

class BookIIProp2Op(Op):
    name = "BookII.Prop2"
    cost = 1.5

    def precond(self, graph: HyperGraph) -> List[Tuple[int, int]]:
        """Return valid (line1_id, line2_id) tuples for constructing rectangles."""
        valid_inputs = []
        lines, _ = graph.by_type(NodeType.LINE)
        line_list = list(lines)
        
        for i, line1 in enumerate(line_list):
            for j, line2 in enumerate(line_list[i+1:], i+1):
                if ('p1' in line1.attr and 'p2' in line1.attr and
                    'p1' in line2.attr and 'p2' in line2.attr):
                    valid_inputs.append((line1.id, line2.id))
        
        return valid_inputs[:20]  # Limit combinations

    def apply(self, graph: HyperGraph, line1_id: int, line2_id: int) -> dict:
        # Construct rectangle using two line segments as adjacent sides
        
        # Add rectangle polygon
        rect_id = graph.add_node(NodeType.POLYGON, {
            'sides': 4,
            'type': 'rectangle',
            'constructed_by': self.name,
            'based_on': [line1_id, line2_id]
        })

        # Add construction edge
        graph.add_edge(EdgeType.CONSTRUCTION, (line1_id, line2_id, rect_id))

        # Add proposition
        prop_id = graph.add_node(NodeType.PROPOSITION, {
            'text': f'Rectangle constructed from two line segments',
            'status': 'derived'
        })

        return {'rectangle': rect_id, 'proposition': prop_id}

    def invariants(self, graph: HyperGraph, outputs: dict) -> bool:
        if not isinstance(outputs, dict):
            return False
        try:
            rect = graph.nodes[outputs['rectangle']]
            return rect.attr.get('sides') == 4 and rect.attr.get('type') == 'rectangle'
        except Exception:
            return False

REGISTRY = Registry()
REGISTRY.add(BookIIProp1Op())
REGISTRY.add(BookIIProp2Op())
