from decimal import Decimal


class ArithmeticEncoder:
    def __init__(self, freq_table, save=False):
        self.history = []
        self.history_binary = []
        self.save = save
        if save:
            print(
                "WARNING : Saving the intermediate stages can cause memory overflow if message is large"
            )
        self.probab_table = self.build_probab_table(freq_table)

    def build_probab_table(self, freq_table):
        total = sum(list(freq_table.values()))

        probab_table = {}
        for key in freq_table:
            probab_table[key] = freq_table[key] / total

        return probab_table

    def evaluate_stage(self, pmin, pmax):
        probabs = {}
        prange = pmax - pmin
        probab_keys = list(self.probab_table.keys())
        for index in range(len(probab_keys)):
            curr_key = probab_keys[index]
            curr_probab = Decimal(self.probab_table[curr_key])
            cumulative_probab = curr_probab * prange + pmin
            probabs[curr_key] = [pmin, cumulative_probab]
            pmin = cumulative_probab
        return probabs

    def build_encoded_text(self, final_probabs):
        temp_probabs = []
        for key in final_probabs:
            temp_probabs.extend(final_probabs[key])

        pmin_last = min(temp_probabs)
        pmax_last = max(temp_probabs)
        encoded_value = (pmin_last + pmax_last) / 2

        return pmin_last, pmax_last, encoded_value

    def encode(self, text):
        text = list(text)

        curr_min = Decimal(0.0)
        curr_max = Decimal(1.0)

        for index in range(len(text)):
            stage_probabs = self.evaluate_stage(curr_min, curr_max)

            curr_term = text[index]
            curr_min = stage_probabs[curr_term][0]
            curr_max = stage_probabs[curr_term][1]

            if self.save:
                self.history.append(stage_probabs)

        last_stage_probabs = self.evaluate_stage(curr_min, curr_max)

        if self.save:
            self.history.append(last_stage_probabs)

        min_val, max_val, encoded_val = self.build_encoded_text(last_stage_probabs)
        return min_val, max_val, encoded_val
