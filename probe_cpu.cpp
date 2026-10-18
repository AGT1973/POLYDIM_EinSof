#include <iostream>
int main() {
    bool has_avx = __builtin_cpu_supports("avx");
    bool has_avx2 = __builtin_cpu_supports("avx2");
    bool has_fma = __builtin_cpu_supports("fma");
    std::cout << "AVX=" << has_avx << " AVX2=" << has_avx2 << " FMA=" << has_fma << std::endl;
    return 0;
}
