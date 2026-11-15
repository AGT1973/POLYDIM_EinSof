// ============================================================================
// ATELIER NATIVE SIPHASH-2-4 ACCELERATOR FOR PYTHON CTYPES (CDYLIB)
// Compilar con: rustc --crate-type cdylib -O E:\SUITE\pmtp\atelier_siphash.rs -o E:\SUITE\pmtp\atelier_siphash.dll
// ============================================================================

#[inline]
fn rotl64(x: u64, b: u32) -> u64 {
    (x << b) | (x >> (64 - b))
}

#[inline]
fn sipround(v0: &mut u64, v1: &mut u64, v2: &mut u64, v3: &mut u64) {
    *v0 = v0.wrapping_add(*v1);
    *v1 = rotl64(*v1, 13) ^ *v0;
    *v0 = rotl64(*v0, 32);
    *v2 = v2.wrapping_add(*v3);
    *v3 = rotl64(*v3, 16) ^ *v2;
    *v0 = v0.wrapping_add(*v3);
    *v3 = rotl64(*v3, 21) ^ *v0;
    *v2 = v2.wrapping_add(*v1);
    *v1 = rotl64(*v1, 17) ^ *v2;
    *v2 = rotl64(*v2, 32);
}

#[inline]
fn read_le_u64(slice: &[u8]) -> u64 {
    u64::from_le_bytes([
        slice[0], slice[1], slice[2], slice[3],
        slice[4], slice[5], slice[6], slice[7],
    ])
}

#[no_mangle]
pub unsafe extern "C" fn pmtp_siphash24_u64(
    key_ptr: *const u8,
    data_ptr: *const u8,
    data_len: usize,
) -> u64 {
    if key_ptr.is_null() || (data_ptr.is_null() && data_len > 0) {
        return 0;
    }
    let key = std::slice::from_raw_parts(key_ptr, 16);
    let data = if data_len > 0 {
        std::slice::from_raw_parts(data_ptr, data_len)
    } else {
        &[]
    };

    let k0 = read_le_u64(&key[0..8]);
    let k1 = read_le_u64(&key[8..16]);
    let mut v0 = 0x736f6d6570736575u64 ^ k0;
    let mut v1 = 0x646f72616e646f6du64 ^ k1;
    let mut v2 = 0x6c7967656e657261u64 ^ k0;
    let mut v3 = 0x7465646279746573u64 ^ k1;

    let n = data.len();
    let full = n & !7usize;
    let mut off = 0usize;
    while off < full {
        let m = read_le_u64(&data[off..off + 8]);
        v3 ^= m;
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
        v0 ^= m;
        off += 8;
    }

    let mut b: u64 = ((n & 0xff) as u64) << 56;
    let rem = n & 7;
    for idx in 0..rem {
        b |= (data[full + idx] as u64) << (8 * idx);
    }
    v3 ^= b;
    sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    v0 ^= b;
    v2 ^= 0xff;
    for _ in range(0, 4) {
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    }
    (v0 ^ v1) ^ (v2 ^ v3)
}

#[inline]
fn range(start: usize, end: usize) -> std::ops::Range<usize> {
    start..end
}
