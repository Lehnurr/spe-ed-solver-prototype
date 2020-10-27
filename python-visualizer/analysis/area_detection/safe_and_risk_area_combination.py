from analysis.area_detection.risk_area_calculation import calculate_risk_areas
from analysis.area_detection.safe_area_detection import detect_safe_areas, SafeArea
from game_data.game.Board import Board
import numpy as np


class RiskEvaluatedSafeArea:
    def __init__(self, points: [], risk: float):
        self.points = points
        self.risk = risk


def do_risk_assessment(safe_area: SafeArea, risk_areas) -> RiskEvaluatedSafeArea:
    risk_sum = sum([risk_areas[p[1], p[0]] for p in safe_area.points])
    risk_avg = risk_sum / len(safe_area.points)
    return RiskEvaluatedSafeArea(safe_area.points, risk_avg)


def get_risk_evaluated_safe_areas(board: Board):
    risk_areas = calculate_risk_areas(board)
    safe_areas, safe_area_labels = detect_safe_areas(np.array(board.cells))
    return [do_risk_assessment(safe_area, risk_areas) for safe_area in safe_areas], safe_area_labels
