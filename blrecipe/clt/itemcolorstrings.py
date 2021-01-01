"""
Read and interpret the Boundless itemcolorstrings.dat file
"""

from collections import namedtuple
from struct import unpack_from


VarLen = namedtuple('VarLen', ['data_offset', 'data_len'])

VAR_LEN = [VarLen(1, 3), VarLen(2, 6), VarLen(1, 3), VarLen(2, 10)]


class StringTable(object):
    """
    A decoded string table.
    """

    def __init__(self, data, offset, max_index):
        self._data = data
        self._names = []

        (encodings_offset, word_index_offset, words_offset, bit_length) = unpack_from('<IIIB', self._data, offset)
        offset += (3 * 4 + 1)
        encoding_indeces = [self._decode_intsize(offset, bit_length, i)
                            for i in range(max_index)]

        word_index_bit_length = unpack_from('<B', self._data, word_index_offset)[0]
        word_index_length = int((words_offset - word_index_offset) * 8 / word_index_bit_length)
        word_indeces = [self._decode_intsize(word_index_offset+1, word_index_bit_length, i)
                        for i in range(word_index_length+1)]

        for i in range(max_index):
            self._names.append('')
            encoding_offset = encodings_offset + encoding_indeces[i]
            bit_offset = 0
            encoding = self._decode_varlen(encoding_offset, bit_offset)
            word_count = self._get_bits_at(encoding_offset,
                                           bit_offset + encoding.data_offset,
                                           encoding.data_len)
            for w in range(word_count):
                bit_offset += (encoding.data_offset + encoding.data_len)
                encoding = self._decode_varlen(encoding_offset, bit_offset)
                word_index = self._get_bits_at(encoding_offset,
                                               bit_offset + encoding.data_offset,
                                               encoding.data_len)
                fmt = '{}s'.format(word_indeces[word_index+1] - word_indeces[word_index])
                off = words_offset + word_indeces[word_index]
                word = unpack_from(fmt, self._data, off)[0].decode('iso8859-1')
                sep = (' ' if w > 0 else '')
                self._names[i] = sep.join((self._names[i], word))

    def _decode_intsize(self, base_offset, bit_length, index):
        """
        Extracts the bit_length-bit integer stored at index index from base_offset.
        """
        byte_offset = base_offset + int(index * bit_length / 8)
        bit_offset = (index * bit_length) % 8
        (word,) = unpack_from("<I", self._data, byte_offset)
        value = int(format(word, '032b')[::-1][bit_offset:bit_offset+bit_length][::-1], 2)
        return value

    def _get_bits_at(self, base_offset, bit_offset, bit_len):
        """
        Get the bit_len bits at bit_offset bits from base_offset as an integer.
        """
        byte_offset = int(bit_offset / 8)
        bit_in_byte_offset = bit_offset % 8
        (word,) = unpack_from("<I", self._data, base_offset + byte_offset)
        value = int(format(word, '032b')[::-1][bit_in_byte_offset:bit_in_byte_offset+bit_len][::-1], 2)
        return value

    def _decode_varlen(self, base_offset, bit_offset):
        return VAR_LEN[self._get_bits_at(base_offset, bit_offset, 2)]

    def name(self, index):
        """
        Get an indicated name.
        """
        return self._names[index]


class Translation(object):
    """
    A set of localized names for things.
    """

    def __init__(self, data, offset, name_counts):
        (colour_string_offset, metal_string_offset, item_string_offset) = unpack_from('<III', data, offset)
        offset += (3 * 4)
        self._si = StringTable(data, offset, name_counts["subtitles"]+1)
        self._ci = StringTable(data, colour_string_offset, name_counts["colours"])
        self._mi = StringTable(data, metal_string_offset, name_counts["metals"])
        self._ii = StringTable(data, item_string_offset, name_counts["items"])

    def subtitle(self, index):
        """
        Get an indicated subtitle
        """
        return self._si.name(index)

    def colour(self, index):
        """
        Get an indicated colour name
        """
        return self._ci.name(index)

    def metal(self, index):
        """
        Get an indicated metal name
        """
        return self._mi.name(index)

    def item(self, index):
        """
        Get an indicated item name
        """
        return self._ii.name(index)


class ObjectNames(object):
    """
    A collection of localized object names
    """

    def __init__(self, filename):
        self._name_counts = {
            "colours": 255,
            "items": 0,
            "languages": 0,
            "metals": 0,
            "subtitles": 0,
        }
        self._items = []
        self._languages = {}

        with open(filename, 'rb') as datfile:
            self._data = datfile.read()

            offset = 0

            self._name_counts["metals"] = unpack_from('<B', self._data, offset)[0]
            offset += 1

            self._name_counts["items"] = unpack_from('<H', self._data, offset)[0]
            offset += 2

            for _ in range(self._name_counts["items"]):
                (item_id, item_subindex) = unpack_from('<HB', self._data, offset)
                offset += (1 + 2)
                if item_subindex > self._name_counts["subtitles"]:
                    self._name_counts["subtitles"] = item_subindex
                self._items.append((item_id, item_subindex))

            self._name_counts["languages"] = unpack_from('<B', self._data, offset)[0]
            offset += 1

            for _ in range(self._name_counts["languages"]):
                (name_length,) = unpack_from('<B', self._data, offset)
                offset += 1
                (name, language_offset) = unpack_from('<{}sI'.format(name_length), self._data, offset)
                offset += (name_length + 4)
                self._languages[name.decode('iso8859-1')] = language_offset

    def translation(self, language):
        """
        Get the translation for a named language
        """
        return Translation(self._data, self._languages[language], self._name_counts)

    def item_count(self):
        return self._name_counts["items"]

    def item(self, index):
        return self._items[index]

    def languages(self):
        return self._languages


