#!/usr/bin/env python

import cProfile
import pstats
import random
import time

import bitstring

# Some performance tests. Each is a task - it is permissible to rewrite
# to do it in a different way.


# TEST 1: Create a bitstring, read every 3 bits and count how many equal '001'.
def perf1():
    s = bitstring.Bits("0xef1356a6200b3, 0b0")
    s *= 10000
    c = 0
    for triplet in s.cut(3):
        if triplet == "0b001":
            c += 1
    assert c == 20003


def perf2():
    s = bitstring.BitArray(10000000)
    s.set(1, [10, 100, 1000, 100000])
    count = 0
    for bit in s:
        if bit:
            count += 1
    assert count == 4


def perf3():
    s = bitstring.BitArray()
    for i in range(50000):
        s += "uint:12=244, float:32=0.4"
        s += "0x3e44f, 0b11011, 0o75523"
        s += [0, 1, 2, 0, 0, 1, 2, 0, -1, 0, "hello"]
        s += 104


def perf4():
    random.seed(999)
    i = random.randrange(0, 2 ** 80000000)
    s = bitstring.BitArray(uint=i, length=80000000)
    for ss in [
        "0b11010010101",
        "0xabcdef1234, 0b000101111010101010011010100100101010101",
        "0x4321",
    ]:
        print(len(list(s.findall(ss))))


def run(f):
    start_time = time.time()
    print("Running {0}".format(str(f)))
    f()
    print("Took {0} s".format(time.time() - start_time))


def main():
    start_time = time.time()
    run(perf1)
    run(perf2)
    run(perf3)
    run(perf4)
    print("Total time {0} s".format(time.time() - start_time))


if __name__ == "__main__":
    cProfile.run("main()", "stats")
    p = pstats.Stats("stats")
    p.sort_stats("time").print_stats(50)
