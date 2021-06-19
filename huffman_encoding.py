import os
import heapq


class Node:
    def __init__(self, character, frequency):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, Node):
            return False
        return self.freq == other.freq


class HuffmanEncoder:
    def __init__(self, path):
        self.path = path

        self.heap = []

        # character -> code map
        self.map = {}

        # code -> character map
        self.reverse_map = {}

    def merge(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged_node = Node(None, node1.frequency + node2.frequency)
            merged_node.left = node1
            merged_node.right = node2

            heapq.heappush(self.heap, merged_node)

    def create_heap(self, frequency_dict):
        for key in frequency_dict:
            node = Node(key, frequency_dict[key])
            heapq.heappush(self.heap, node)

    def create_frequency_dict(self, text):
        frequency_dict = {}
        for character in text:
            if not character in frequency_dict:
                frequency_dict[character] = 1
            else:
                frequency_dict[character] += 1
        return frequency_dict

    def create_codes_util(self, root, current_code):
        if root == None:
            return

        if root.character != None:
            self.map[root.character] = current_code
            self.reverse_map[current_code] = root.character
            return

        self.create_codes_util(root.left, current_code + "0")
        self.create_codes_util(root.right, current_code + "1")

    def create_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.create_codes_util(root, current_code)

    def fetch_encoded_text(self, text):
        encoded_text = ""
        for character in text:
            encoded_text += self.map[character]

        return encoded_text

    def pad_encoded_text(self, encoded_text):
        padding = 8 - (len(encoded_text) % 8)
        for i in range(padding):
            encoded_text += "0"

        padding_info = "{0:08b}".format(padding)
        encoded_text = padding_info + encoded_text
        return encoded_text

    def get_byte_array(self, text):
        if len(text) % 8 != 0:
            print("ERROR : Encoded text is not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(text), 8):
            byte = text[i : i + 8]
            b.append(int(byte, 2))
        return b

    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"

        with open(self.path, "r+") as file, open(output_path, "wb") as output:
            text = file.read()
            text = text.rstrip()

            frequency_dict = self.create_frequency_dict(text)
            self.create_heap(frequency_dict)
            self.merge()
            self.create_codes()

            encoded_text = self.fetch_encoded_text(text)
            encoded_text_with_padding = self.pad_encoded_text(encoded_text)

            b = self.get_byte_array(encoded_text_with_padding)
            output.write(bytes(b))

        print("Compressed the given file")
        return output_path
