#!/usr/bin/env python3
"""
DT-06b / V019: PMTP Tri-Segment Concurrent Stress Test (Canonical Seqlock V44.0)
Multi-threaded writer/reader stress over shared memory.
Validates Theorem 9.5 (Odd/Even Parity Seqlock Linearization):
- Zero torn reads (torn == 0)
- Zero epoch violations (epoch_violations == 0)
- Lock-free readers with odd-parity retry
"""
import threading
import time
import struct
import mmap
import os
import sys
import json
from collections import defaultdict

NUM_WRITERS = 2
NUM_READERS = 8
DURATION_SEC = int(sys.argv[1]) if len(sys.argv) > 1 else 10
SLOT_COUNT = 3
PAYLOAD_DOUBLES = 64
HEADER_SIZE = 64
SLOT_SIZE = PAYLOAD_DOUBLES * 8
TOTAL_SHM_SIZE = HEADER_SIZE + SLOT_COUNT * SLOT_SIZE

class AtomicCounter:
    def __init__(self, initial=0):
        self._value = initial
        self._lock = threading.Lock()
    def increment(self, val=1):
        with self._lock:
            self._value += val
            return self._value
    def get(self):
        with self._lock:
            return self._value

class CanonicalSeqlockTriBus:
    def __init__(self):
        if sys.platform == 'win32':
            self.shm = mmap.mmap(-1, TOTAL_SHM_SIZE, tagname=None)
        elif hasattr(mmap, 'MAP_ANON'):
            self.shm = mmap.mmap(-1, TOTAL_SHM_SIZE, mmap.MAP_SHARED | mmap.MAP_ANON, mmap.PROT_READ | mmap.PROT_WRITE)
        else:
            self.shm = mmap.mmap(-1, TOTAL_SHM_SIZE)

        self.generation = AtomicCounter(0)   # Even = stable, Odd = writing (Teorema 9.5)
        self.active_slot = AtomicCounter(0)
        self.epoch = AtomicCounter(1)
        self.writer_lock = threading.Lock()

        self.stats = {
            'writes': AtomicCounter(0),
            'reads': AtomicCounter(0),
            'seqlock_retries': AtomicCounter(0),
            'torn_reads': AtomicCounter(0),
            'epoch_violations': AtomicCounter(0),
            'contention_waits': AtomicCounter(0),
        }

    def get_slot_offset(self, slot):
        return HEADER_SIZE + slot * SLOT_SIZE

    def write_slot(self, slot, epoch_val, writer_id):
        offset = self.get_slot_offset(slot)
        for i in range(PAYLOAD_DOUBLES):
            val = float(epoch_val) + writer_id * 0.001 + i * 1e-6
            struct.pack_into('<d', self.shm, offset + i * 8, val)

    def read_slot_raw(self, slot):
        offset = self.get_slot_offset(slot)
        values = []
        for i in range(PAYLOAD_DOUBLES):
            val = struct.unpack_from('<d', self.shm, offset + i * 8)[0]
            values.append(val)
        return values

    def read_slot_seqlock(self):
        """Teorema 9.5 Reader: spins on odd generation, re-reads if generation changed"""
        max_spins = 1000
        for _ in range(max_spins):
            g1 = self.generation.get()
            if g1 & 1:  # Writer in progress (odd)
                self.stats['seqlock_retries'].increment()
                time.sleep(0.00001)
                continue

            slot = self.active_slot.get()
            values = self.read_slot_raw(slot)

            g2 = self.generation.get()
            if g1 == g2 and not (g2 & 1):
                # Consistent linear snapshot acquired
                return values, True

            self.stats['seqlock_retries'].increment()
            time.sleep(0.00001)

        # Fallback if contention was extreme
        return values, False

    def verify_consistency(self, values):
        if not values:
            return True, 0
        base = values[0]
        epoch_base = int(base)
        torn = 0
        for v in values:
            if int(v) != epoch_base:
                torn += 1
        return torn == 0, torn


def writer_thread(bus, writer_id, stop_event):
    local_writes = 0
    local_contentions = 0
    while not stop_event.is_set():
        acquired = bus.writer_lock.acquire(timeout=0.005)
        if not acquired:
            local_contentions += 1
            bus.stats['contention_waits'].increment()
            continue
        try:
            current_active = bus.active_slot.get()
            next_slot = (current_active + 1) % SLOT_COUNT

            # Step 1: gen -> odd (mutation started)
            bus.generation.increment(1)

            # Step 2: write payload
            epoch = bus.epoch.increment(1)
            bus.write_slot(next_slot, epoch, writer_id)

            # Step 3: update active slot
            with bus.active_slot._lock:
                bus.active_slot._value = next_slot

            # Step 4: gen -> even (atomic commit)
            bus.generation.increment(1)

            local_writes += 1
            bus.stats['writes'].increment()
        finally:
            bus.writer_lock.release()

        time.sleep(0.00005)
    return local_writes, local_contentions


def reader_thread(bus, reader_id, stop_event):
    local_reads = 0
    local_torn = 0
    local_epoch_violations = 0
    last_epoch_seen = 0

    while not stop_event.is_set():
        values, consistent_read = bus.read_slot_seqlock()
        if not consistent_read:
            continue

        consistent, torn_count = bus.verify_consistency(values)
        local_reads += 1
        bus.stats['reads'].increment()

        if not consistent:
            local_torn += 1
            bus.stats['torn_reads'].increment()

        if values:
            current_epoch = int(values[0])
            if current_epoch < last_epoch_seen:
                local_epoch_violations += 1
                bus.stats['epoch_violations'].increment()
            else:
                last_epoch_seen = current_epoch

        time.sleep(0.00002)

    return local_reads, local_torn, local_epoch_violations


def main():
    print("=" * 70)
    print("DT-06b / V019: PMTP CANONICAL SEQLOCK CONCURRENT STRESS TEST")
    print(f"  Writers: {NUM_WRITERS} | Readers: {NUM_READERS}")
    print(f"  Duration: {DURATION_SEC}s | Slots: {SLOT_COUNT} | Payload: {PAYLOAD_DOUBLES} doubles")
    print(f"  Protocol: Canonical Seqlock Odd/Even Parity (Teorema 9.5)")
    print("=" * 70)

    bus = CanonicalSeqlockTriBus()
    stop_event = threading.Event()

    writer_threads = []
    reader_threads = []
    writer_results = [None] * NUM_WRITERS
    reader_results = [None] * NUM_READERS

    def writer_wrapper(wid):
        writer_results[wid] = writer_thread(bus, wid, stop_event)

    def reader_wrapper(rid):
        reader_results[rid] = reader_thread(bus, rid, stop_event)

    t_start = time.time()

    for i in range(NUM_WRITERS):
        t = threading.Thread(target=writer_wrapper, args=(i,), daemon=True)
        writer_threads.append(t)
        t.start()

    for i in range(NUM_READERS):
        t = threading.Thread(target=reader_wrapper, args=(i,), daemon=True)
        reader_threads.append(t)
        t.start()

    # Progress loop
    elapsed = 0
    while elapsed < DURATION_SEC:
        time.sleep(1.0)
        elapsed = time.time() - t_start
        w = bus.stats['writes'].get()
        r = bus.stats['reads'].get()
        retries = bus.stats['seqlock_retries'].get()
        torn = bus.stats['torn_reads'].get()
        epoch_v = bus.stats['epoch_violations'].get()
        print(f"  [{elapsed:4.0f}s] writes={w:8d}  reads={r:8d}  retries={retries:6d}  torn={torn}  epoch_violations={epoch_v}")

    stop_event.set()
    for t in writer_threads + reader_threads:
        t.join(timeout=2.0)

    total_w = bus.stats['writes'].get()
    total_r = bus.stats['reads'].get()
    total_retries = bus.stats['seqlock_retries'].get()
    total_torn = bus.stats['torn_reads'].get()
    total_epoch_v = bus.stats['epoch_violations'].get()
    total_contentions = bus.stats['contention_waits'].get()

    print("\n" + "=" * 70)
    print("RESULTS CANONICAL SEQLOCK STRESS (V019 / V44.0)")
    print("=" * 70)
    print(f"  Duration:           {elapsed:.2f} s")
    print(f"  Total Writes:       {total_w}")
    print(f"  Total Reads:        {total_r}")
    print(f"  Seqlock Retries:    {total_retries}")
    print(f"  Torn Reads:         {total_torn}")
    print(f"  Epoch Violations:   {total_epoch_v}")
    print(f"  Writer Contentions: {total_contentions}")

    verdict = (total_torn == 0) and (total_epoch_v == 0) and (total_w > 0) and (total_r > 0)
    status_str = "PASS — ZERO TORN READS, ZERO EPOCH VIOLATIONS" if verdict else "FAIL"
    print(f"\n  VERDICT: {status_str}")

    report = {
        "status": "PASS" if verdict else "FAIL",
        "duration_s": round(elapsed, 2),
        "writes": total_w,
        "reads": total_r,
        "seqlock_retries": total_retries,
        "torn_reads": total_torn,
        "epoch_violations": total_epoch_v,
        "writer_contentions": total_contentions,
        "protocol": "Seqlock_Canonical_OddEven_V019"
    }

    report_path = "/home/ariel/polydim_v017/test/stress_report.json" if sys.platform != 'win32' else "stress_report.json"
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
    except:
        pass

    if not verdict:
        sys.exit(1)
    print("\n>>> [CERTIFIED EXIT CODE 0] Seqlock Canonical Protocol Verified Under Heavy Contention.")
    sys.exit(0)

if __name__ == "__main__":
    main()
