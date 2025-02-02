#!/usr/bin/env python
"""
Unit tests for the bitarray module.
"""

import unittest

import bitstring
from bitstring import BitArray


class All(unittest.TestCase):
    def testCreationFromUint(self):
        s = BitArray(uint=15, length=6)
        self.assertEqual(s.bin, "001111")
        s = BitArray(uint=0, length=1)
        self.assertEqual(s.bin, "0")
        s.uint = 1
        self.assertEqual(s.uint, 1)
        s = BitArray(length=8)
        s.uint = 0
        self.assertEqual(s.uint, 0)
        s.uint = 255
        self.assertEqual(s.uint, 255)
        self.assertEqual(s.len, 8)
        with self.assertRaises(bitstring.CreationError):
            s.uint = 256

    def testCreationFromOct(self):
        s = BitArray(oct="7")
        self.assertEqual(s.oct, "7")
        self.assertEqual(s.bin, "111")
        s.append("0o1")
        self.assertEqual(s.bin, "111001")
        s.oct = "12345670"
        self.assertEqual(s.length, 24)
        self.assertEqual(s.bin, "001010011100101110111000")
        s = BitArray("0o123")
        self.assertEqual(s.oct, "123")


class NoPosAttribute(unittest.TestCase):
    def testReplace(self):
        s = BitArray("0b01")
        s.replace("0b1", "0b11")
        self.assertEqual(s, "0b011")

    def testDelete(self):
        s = BitArray("0b000000001")
        del s[-1:]
        self.assertEqual(s, "0b00000000")

    def testInsert(self):
        s = BitArray("0b00")
        s.insert("0xf", 1)
        self.assertEqual(s, "0b011110")

    def testInsertParameters(self):
        s = BitArray("0b111")
        with self.assertRaises(TypeError):
            s.insert("0x4")

    def testOverwrite(self):
        s = BitArray("0b01110")
        s.overwrite("0b000", 1)
        self.assertEqual(s, "0b00000")

    def testOverwriteParameters(self):
        s = BitArray("0b0000")
        with self.assertRaises(TypeError):
            s.overwrite("0b111")

    def testPrepend(self):
        s = BitArray("0b0")
        s.prepend([1])
        self.assertEqual(s, [1, 0])

    def testRol(self):
        s = BitArray("0b0001")
        s.rol(1)
        self.assertEqual(s, "0b0010")

    def testRor(self):
        s = BitArray("0b1000")
        s.ror(1)
        self.assertEqual(s, "0b0100")

    def testSetItem(self):
        s = BitArray("0b000100")
        s[4:5] = "0xf"
        self.assertEqual(s, "0b000111110")
        s[0:1] = [1]
        self.assertEqual(s, "0b100111110")


class Bugs(unittest.TestCase):
    def testAddingNonsense(self):
        a = BitArray([0])
        a += "0"  # a uint of length 0 - so nothing gets added.
        self.assertEqual(a, [0])
        with self.assertRaises(ValueError):
            a += "3"
        with self.assertRaises(ValueError):
            a += "se"
        with self.assertRaises(ValueError):
            a += "float:32"

    def testPrependAfterCreationFromDataWithOffset(self):
        s1 = BitArray(bytes=b"\x00\x00\x07\xff\xf0\x00", offset=21, length=15)
        self.assertFalse(s1.any(0))
        s1.prepend("0b0")
        self.assertEqual(s1.bin, "0111111111111111")
        s1.prepend("0b0")
        self.assertEqual(s1.bin, "00111111111111111")


class ByteAligned(unittest.TestCase):
    def testDefault(self, defaultbytealigned=bitstring.bytealigned):
        self.assertFalse(defaultbytealigned)

    def testChangingIt(self):
        bitstring.bytealigned = True
        self.assertTrue(bitstring.bytealigned)
        bitstring.bytealigned = False

    def testNotByteAligned(self):
        bitstring.bytealigned = False
        a = BitArray("0x00 ff 0f f")
        b = list(a.findall("0xff"))
        self.assertEqual(b, [8, 20])
        p = a.find("0x0f")[0]
        self.assertEqual(p, 4)
        p = a.rfind("0xff")[0]
        self.assertEqual(p, 20)
        s = list(a.split("0xff"))
        self.assertEqual(s, ["0x00", "0xff0", "0xff"])
        a.replace("0xff", "")
        self.assertEqual(a, "0x000")

    def testByteAligned(self):
        bitstring.bytealigned = True
        a = BitArray("0x00 ff 0f f")
        b = list(a.findall("0xff"))
        self.assertEqual(b, [8])
        p = a.find("0x0f")[0]
        self.assertEqual(p, 16)
        p = a.rfind("0xff")[0]
        self.assertEqual(p, 8)
        s = list(a.split("0xff"))
        self.assertEqual(s, ["0x00", "0xff0ff"])
        a.replace("0xff", "")
        self.assertEqual(a, "0x000ff")


class SliceAssignment(unittest.TestCase):
    def testSliceAssignmentSingleBit(self):
        a = BitArray("0b000")
        a[2] = "0b1"
        self.assertEqual(a.bin, "001")
        a[0] = BitArray(bin="1")
        self.assertEqual(a.bin, "101")
        a[-1] = "0b0"
        self.assertEqual(a.bin, "100")
        a[-3] = "0b0"
        self.assertEqual(a.bin, "000")

    def testSliceAssignmentSingleBitErrors(self):
        a = BitArray("0b000")
        with self.assertRaises(IndexError):
            a[-4] = "0b1"
        with self.assertRaises(IndexError):
            a[3] = "0b1"
        with self.assertRaises(TypeError):
            a[1] = 1.3

    def testSliceAssignmentMulipleBits(self):
        a = BitArray("0b0")
        a[0] = "0b110"
        self.assertEqual(a.bin, "110")
        a[0] = "0b000"
        self.assertEqual(a.bin, "00010")
        a[0:3] = "0b111"
        self.assertEqual(a.bin, "11110")
        a[-2:] = "0b011"
        self.assertEqual(a.bin, "111011")
        a[:] = "0x12345"
        self.assertEqual(a.hex, "12345")
        a[:] = ""
        self.assertFalse(a)

    def testSliceAssignmentMultipleBitsErrors(self):
        a = BitArray()
        with self.assertRaises(IndexError):
            a[0] = "0b00"
        a += "0b1"
        a[0:2] = "0b11"
        self.assertEqual(a, "0b11")

    def testDelSliceStep(self):
        a = BitArray(bin="100111101001001110110100101")
        del a[::2]
        self.assertEqual(a.bin, "0110010101100")
        del a[3:9:3]
        self.assertEqual(a.bin, "01101101100")
        del a[2:7:1]
        self.assertEqual(a.bin, "011100")
        del a[::99]
        self.assertEqual(a.bin, "11100")
        del a[::1]
        self.assertEqual(a.bin, "")

    def testDelSliceNegativeStep(self):
        a = BitArray("0b0001011101101100100110000001")
        del a[5:23:-3]
        self.assertEqual(a.bin, "0001011101101100100110000001")
        del a[25:3:-3]
        self.assertEqual(a.bin, "00011101010000100001")
        del a[:6:-7]
        self.assertEqual(a.bin, "000111010100010000")
        del a[15::-2]
        self.assertEqual(a.bin, "0010000000")
        del a[::-1]
        self.assertEqual(a.bin, "")

    def testDelSliceNegativeEnd(self):
        a = BitArray("0b01001000100001")
        del a[:-5]
        self.assertEqual(a, "0b00001")
        a = BitArray("0b01001000100001")
        del a[-11:-5]
        self.assertEqual(a, "0b01000001")

    def testDelSliceErrors(self):
        a = BitArray(10)
        del a[5:3]
        self.assertEqual(a, 10)
        del a[3:5:-1]
        self.assertEqual(a, 10)

    def testDelSingleElement(self):
        a = BitArray("0b0010011")
        del a[-1]
        self.assertEqual(a.bin, "001001")
        del a[2]
        self.assertEqual(a.bin, "00001")
        with self.assertRaises(IndexError):
            del a[5]

    def testSetSliceStep(self):
        a = BitArray(bin="0000000000")
        a[::2] = "0b11111"
        self.assertEqual(a.bin, "1010101010")
        a[4:9:3] = [0, 0]
        self.assertEqual(a.bin, "1010001010")
        a[7:3:-1] = [1, 1, 1, 0]
        self.assertEqual(a.bin, "1010011110")
        a[7:1:-2] = [0, 0, 1]
        self.assertEqual(a.bin, "1011001010")
        a[::-5] = [1, 1]
        self.assertEqual(a.bin, "1011101011")
        a[::-1] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        self.assertEqual(a.bin, "1000000000")

    def testSetSliceErrors(self):
        a = BitArray(8)
        try:
            a[::3] = [1]
            self.assertTrue(False)
        except ValueError:
            pass

        class A(object):
            pass

        try:
            a[1:2] = A()
            self.assertTrue(False)
        except TypeError:
            pass
        try:
            a[1:4:-1] = [1, 2]
            self.assertTrue(False)
        except ValueError:
            pass


class Subclassing(unittest.TestCase):
    def testIsInstance(self):
        class SubBits(BitArray):
            pass

        a = SubBits()
        self.assertTrue(isinstance(a, SubBits))

    def testClassType(self):
        class SubBits(BitArray):
            pass

        self.assertEqual(SubBits().__class__, SubBits)


class Clear(unittest.TestCase):
    def testClear(self):
        s = BitArray("0xfff")
        s.clear()
        self.assertEqual(s.len, 0)


class Copy(unittest.TestCase):
    def testCopyMethod(self):
        s = BitArray(9)
        t = s.copy()
        self.assertEqual(s, t)
        t[0] = True
        self.assertEqual(t.bin, "100000000")
        self.assertEqual(s.bin, "000000000")


class ModifiedByAddingBug(unittest.TestCase):
    def testAdding(self):
        a = BitArray("0b0")
        b = BitArray("0b11")
        c = a + b
        self.assertEqual(c, "0b011")
        self.assertEqual(a, "0b0")
        self.assertEqual(b, "0b11")


class Lsb0Setting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bitstring.set_lsb0(True)

    @classmethod
    def tearDownClass(cls):
        bitstring.set_lsb0(False)

    def testSetSingleBit(self):
        a = BitArray(10)
        a[0] = True
        self.assertEqual(a, "0b0000000001")
        a[1] = True
        self.assertEqual(a, "0b0000000011")
        a[0] = False
        self.assertEqual(a, "0b0000000010")
        a[9] = True
        self.assertEqual(a, "0b1000000010")
        with self.assertRaises(IndexError):
            a[10] = True

    def testSetSingleNegativeBit(self):
        a = BitArray("0o000")
        a[-1] = True
        self.assertEqual(a, "0b100000000")
        a[-2] = True
        self.assertEqual(a, "0o600")
        a[-9] = True
        self.assertEqual(a, "0o601")
        with self.assertRaises(IndexError):
            a[-10] = True

    def testInvertBit(self):
        a = BitArray("0b11110000")
        a.invert()
        self.assertEqual(a, "0x0f")
        a.invert(0)
        self.assertEqual(a, "0b00001110")
        a.invert(-1)
        self.assertEqual(a, "0b10001110")

    def testDeletingBits(self):
        a = BitArray("0b11110")
        del a[0]
        self.assertEqual(a, "0xf")

    def testDeletingRange(self):
        a = BitArray("0b101111000")
        del a[0:1]
        self.assertEqual(a, "0b10111100")
        del a[2:6]
        self.assertEqual(a, "0b1000")
        a = BitArray("0xabcdef")
        del a[:8]
        self.assertEqual(a, "0xabcd")
        del a[-4:]
        self.assertEqual(a, "0xbcd")
        del a[:-4]
        self.assertEqual(a, "0xb")

    def testAppendingBits(self):
        a = BitArray("0b111")
        a.append("0b000")
        self.assertEqual(a.bin, "000111")
        a += "0xabc"
        self.assertEqual(a, "0xabc, 0b000111")

    def testSettingSlice(self):
        a = BitArray("0x012345678")
        a[4:12] = "0xfe"
        self.assertEqual(a, "0x012345fe8")
        a[0:4] = "0xbeef"
        self.assertEqual(a, "0x012345febeef")

    def testTruncatingStart(self):
        a = BitArray("0b1110000")
        a = a[4:]
        self.assertEqual(a, "0b111")

    def testTruncatingEnd(self):
        a = BitArray("0x123456")
        a = a[:16]
        self.assertEqual(a, "0x3456")

    def testAll(self):
        a = BitArray("0b0000101")
        self.assertTrue(a.all(1, [0, 2]))
        self.assertTrue(a.all(False, [-1, -2, -3, -4]))

    def testAny(self):
        a = BitArray("0b0001")
        self.assertTrue(a.any(1, [0, 1, 2]))

    def testEndswith(self):
        a = BitArray("0xdeadbeef")
        self.assertTrue(a.endswith("0xdead"))

    def testStartswith(self):
        a = BitArray("0xdeadbeef")
        self.assertTrue(a.startswith("0xbeef"))

    def testCut(self):
        a = BitArray("0xff00ff1111ff2222")
        b = list(a.cut(16))
        self.assertEqual(b, ["0x2222", "0x11ff", "0xff11", "0xff00"])

    def testFind(self):
        a = BitArray("0b10101010, 0xabcd, 0b10101010, 0x0")
        (p,) = a.find("0b10101010", bytealigned=False)
        self.assertEqual(p, 4)
        (p,) = a.find("0b10101010", start=4, bytealigned=False)
        self.assertEqual(p, 4)
        (p,) = a.find("0b10101010", start=5, bytealigned=False)
        self.assertEqual(p, 22)

    def testRfind(self):
        pass

    def testFindall(self):
        pass

    def testSplit(self):
        a = BitArray("0x4700004711472222")
        b = list(a.split("0x47", bytealigned=True))
        self.assertEqual(b, ["", "0x472222", "0x4711", "0x470000"])

    def testByteSwap(self):
        a = BitArray("0xff00ff00ff00")
        n = a.byteswap(2, end=32, repeat=True)
        self.assertEqual(n, 2)
        self.assertEqual(a, "0xff0000ff00ff")

    def testInsert(self):
        a = BitArray("0x0123456")
        a.insert("0xf", 4)
        self.assertEqual(a, "0x012345f6")

    def testOverwrite(self):
        a = BitArray("0x00000000")
        a.overwrite("0xdead", 4)
        self.assertEqual(a, "0x000dead0")

    def testReplace(self):
        pass

    def testReverse(self):
        pass

    def testRor(self):
        a = BitArray("0b111000")
        a.ror(1)
        self.assertEqual(a, "0b011100")
        a = BitArray("0b111000")
        a.ror(1, start=2, end=6)
        self.assertEqual(a, "0b011100")

    def testRol(self):
        pass

    def testSet(self):
        a = BitArray(100)
        a.set(1, [0, 2, 4])
        self.assertTrue(a[0])
        self.assertTrue(a.startswith("0b000010101"))
        a = BitArray("0b111")
        a.set(False, 0)
        self.assertEqual(a, "0b110")


class Repr(unittest.TestCase):
    def testStandardRepr(self):
        a = BitArray("0o12345")
        self.assertEqual(repr(a), "BitArray('0b001010011100101')")
