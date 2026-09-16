class DecisionModel:
    def __init__(self, alternatives: list, criteria_names: list, criteria_types: list, raw_matrix: list):
        self.alternatives = alternatives
        self.criteria_names = criteria_names
        self.criteria_types = criteria_types
        self.raw_matrix = raw_matrix
        self.num_alts = len(alternatives)
        self.num_crit = len(criteria_names)

    def normalize(self) -> list:
        normalized = [[0.0] * self.num_crit for _ in range(self.num_alts)]
        for j in range(self.num_crit):
            col_vals = [self.raw_matrix[i][j] for i in range(self.num_alts)]
            max_v = max(col_vals)
            min_v = min(col_vals)
            for i in range(self.num_alts):
                if self.criteria_types[j] == 'max':
                    normalized[i][j] = col_vals[i] / max_v if max_v != 0 else 0.0
                else:
                    normalized[i][j] = min_v / col_vals[i] if col_vals[i] != 0 else 0.0
        return normalized

    def pareto_filter(self, normalized: list) -> list:
        pareto_indices = list(range(self.num_alts))
        to_remove = set()

        for i in range(self.num_alts):
            for j in range(self.num_alts):
                if i != j and j not in to_remove:
                    all_ge = all(normalized[i][k] >= normalized[j][k] for k in range(self.num_crit))
                    strict_gt = any(normalized[i][k] > normalized[j][k] for k in range(self.num_crit))
                    if all_ge and strict_gt:
                        to_remove.add(j)

        return [idx for idx in pareto_indices if idx not in to_remove]

    @staticmethod
    def calculate_weights(expert_scores: list) -> list:
        num_crit = len(expert_scores[0])
        col_sums = [sum(expert_scores[exp][c] for exp in range(len(expert_scores))) for c in range(num_crit)]
        total_sum = sum(col_sums)
        return [s / total_sum for s in col_sums]

    def electre_analysis(self, active_indices: list, normalized: list, weights: list, c_star: float, d_star: float):
        m = len(active_indices)
        c_matrix = [[0.0] * m for _ in range(m)]
        d_matrix = [[0.0] * m for _ in range(m)]

        for j_idx in range(m):
            j = active_indices[j_idx]
            for k_idx in range(m):
                if j_idx == k_idx:
                    continue
                k = active_indices[k_idx]

                c_jk = 0.0
                max_diff = 0.0

                for c in range(self.num_crit):
                    p_j = normalized[j][c]
                    p_k = normalized[k][c]
                    if p_j >= p_k:
                        c_jk += weights[c]
                    else:
                        diff = p_k - p_j
                        if diff > max_diff:
                            max_diff = diff

                c_matrix[j_idx][k_idx] = c_jk
                d_matrix[j_idx][k_idx] = max_diff

        c_indices = []
        d_indices = []
        for j_idx in range(m):
            c_row = [c_matrix[j_idx][k_idx] for k_idx in range(m) if j_idx != k_idx]
            d_row = [d_matrix[j_idx][k_idx] for k_idx in range(m) if j_idx != k_idx]
            c_indices.append(min(c_row) if c_row else 0.0)
            d_indices.append(max(d_row) if d_row else 0.0)

        core = []
        for j_idx in range(m):
            if c_indices[j_idx] >= c_star and d_indices[j_idx] <= d_star:
                core.append(active_indices[j_idx])

        return c_matrix, d_matrix, c_indices, d_indices, core