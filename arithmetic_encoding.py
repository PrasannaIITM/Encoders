from decimal import Decimal
from utils import bin2float, float2bin


class ArithmeticEncoder:
    def __init__(self, freq_table, save=False):
        self.history = []
        self.history_binary = []
        self.decoder_history = []

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

    def process_stage_binary(self, stage_min_bin, stage_max_bin):
        stage_mid_bin = stage_min_bin + "1"
        stage_min_bin = stage_min_bin + "0"

        stage_probs = {}
        stage_probs[0] = [stage_min_bin, stage_mid_bin]
        stage_probs[1] = [stage_mid_bin, stage_max_bin]

        return stage_probs

    def encode_binary(self, min_val, max_val):
        binary_code = None

        curr_min_bin = "0.0"
        curr_max_bin = "1.0"

        stage_probabs = {}
        stage_probabs[0] = [curr_min_bin, "0.1"]
        stage_probabs[1] = ["0.1", curr_max_bin]

        while True:
            if max_val < bin2float(stage_probabs[0][1]):
                # search in first half
                curr_min_bin = stage_probabs[0][0]
                curr_max_bin = stage_probabs[0][1]
            else:
                # search in second half
                curr_min_bin = stage_probabs[1][0]
                curr_max_bin = stage_probabs[1][1]

            if self.save:
                self.history_binary.append(stage_probabs)

            # update limits by updating mid according to new min, max
            stage_probabs = self.process_stage_binary(curr_min_bin, curr_max_bin)

            # The binary code is found.
            if (bin2float(stage_probabs[0][0]) >= min_val) and (
                bin2float(stage_probabs[0][1]) < max_val
            ):
                binary_code = stage_probabs[0][0]
                break
            elif (bin2float(stage_probabs[1][0]) >= min_val) and (
                bin2float(stage_probabs[1][1]) < max_val
            ):
                binary_code = stage_probabs[1][0]
                break

        if self.save:
            self.history_binary.append(stage_probabs)

        return binary_code

    def decode(self, encoded_msg, msg_length):

        decoded_msg = []

        curr_min = Decimal(0.0)
        curr_max = Decimal(1.0)

        for pos in range(msg_length):
            stage_probabs = self.evaluate_stage(curr_min, curr_max)

            for key, value in stage_probabs.items():
                if encoded_msg >= value[0] and encoded_msg <= value[1]:
                    break

            decoded_msg.append(key)

            curr_min = stage_probabs[key][0]
            curr_max = stage_probabs[key][1]

            if self.save:
                self.decoder_history.append(stage_probabs)

        if self.save:
            last_stage_probabs = self.evaluate_stage(curr_min, curr_max)
            self.decoder_history.append(last_stage_probabs)

        return "".join(decoded_msg)
