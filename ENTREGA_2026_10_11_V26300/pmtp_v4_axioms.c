// Lean compiler output
// Module: PMTP_V4_CORE.pmtp_v4_axioms
// Imports: public import Init public meta import Init
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* lean_nat_to_int(lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
lean_object* lean_string_length(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
lean_object* l_Int_repr(lean_object*);
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
lean_object* l_Bool_repr___redArg(uint8_t);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_MemoryDomain_ofNat(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqMemoryDomain(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqMemoryDomain___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprMemoryDomain_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Polydim.V4.MemoryDomain.HOST_SHM"};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__0 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprMemoryDomain_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__1 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__1_value;
static const lean_string_object l_Polydim_V4_instReprMemoryDomain_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 34, .m_capacity = 34, .m_length = 33, .m_data = "Polydim.V4.MemoryDomain.CUDA_VRAM"};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__2 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprMemoryDomain_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__2_value)}};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__3 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprMemoryDomain_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 34, .m_capacity = 34, .m_length = 33, .m_data = "Polydim.V4.MemoryDomain.ROCM_VRAM"};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__4 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprMemoryDomain_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__5 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__5_value;
static const lean_string_object l_Polydim_V4_instReprMemoryDomain_repr___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 36, .m_capacity = 36, .m_length = 35, .m_data = "Polydim.V4.MemoryDomain.RDMA_FABRIC"};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__6 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__6_value;
static const lean_ctor_object l_Polydim_V4_instReprMemoryDomain_repr___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__6_value)}};
static const lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__7 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain_repr___closed__7_value;
static lean_once_cell_t l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__8;
static lean_once_cell_t l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprMemoryDomain_repr___closed__9;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprMemoryDomain_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprMemoryDomain_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprMemoryDomain___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprMemoryDomain_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprMemoryDomain___closed__0 = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprMemoryDomain = (const lean_object*)&l_Polydim_V4_instReprMemoryDomain___closed__0_value;
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqLeaseDescriptor(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqLeaseDescriptor___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__0_value;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "epoch"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__2_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__3_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__6_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "node_id"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__11_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "base_addr"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__13 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__13_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__13_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__14 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__14_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "byte_length"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__16 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__16_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__16_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__17 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__17_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = "is_committed_read"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__19 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__19_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__19_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__20 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__20_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "memory_domain"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__22 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__22_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__22_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__23 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__23_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24;
static const lean_string_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__25 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__25_value;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26;
static lean_once_cell_t l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28_value;
static const lean_ctor_object l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__25_value)}};
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprLeaseDescriptor___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprLeaseDescriptor_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprLeaseDescriptor___closed__0 = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprLeaseDescriptor = (const lean_object*)&l_Polydim_V4_instReprLeaseDescriptor___closed__0_value;
LEAN_EXPORT lean_object* l_Polydim_V4_subnormal__min__quantum;
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqNeumaierState_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqNeumaierState_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqNeumaierState(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqNeumaierState___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "sum"};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4;
static const lean_string_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "residue"};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__6_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprNeumaierState___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprNeumaierState_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprNeumaierState___closed__0 = (const lean_object*)&l_Polydim_V4_instReprNeumaierState___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprNeumaierState = (const lean_object*)&l_Polydim_V4_instReprNeumaierState___closed__0_value;
LEAN_EXPORT lean_object* l_Polydim_V4_NeumaierState_effective__energy(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_NeumaierState_effective__energy___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqRcuReader_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqRcuReader_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqRcuReader(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqRcuReader___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "reader_id"};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "observed_epoch"};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__5_value;
static lean_once_cell_t l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6;
static const lean_string_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "is_active"};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__7_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuReader_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__7_value)}};
static const lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__8_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprRcuReader___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprRcuReader_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprRcuReader___closed__0 = (const lean_object*)&l_Polydim_V4_instReprRcuReader___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprRcuReader = (const lean_object*)&l_Polydim_V4_instReprRcuReader___closed__0_value;
LEAN_EXPORT lean_object* l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1_spec__2(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0(lean_object*, lean_object*);
static const lean_string_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "[]"};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__0 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__0_value;
static const lean_ctor_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__0_value)}};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__1 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__1_value;
static const lean_string_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "["};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__2 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__2_value;
static const lean_ctor_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__3 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__3_value;
static const lean_string_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "]"};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__4 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__4_value;
static lean_once_cell_t l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5;
static lean_once_cell_t l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6;
static const lean_ctor_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__2_value)}};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__7 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__7_value;
static const lean_ctor_object l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__4_value)}};
static const lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__8 = (const lean_object*)&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__8_value;
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg(lean_object*);
static const lean_string_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "current_epoch"};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "readers"};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__5_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprRcuRingBuffer___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprRcuRingBuffer_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprRcuRingBuffer___closed__0 = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprRcuRingBuffer = (const lean_object*)&l_Polydim_V4_instReprRcuRingBuffer___closed__0_value;
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqWire128_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqWire128_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqWire128(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqWire128___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprWire128_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "high_64"};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprWire128_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprWire128_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprWire128_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprWire128_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "low_64"};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprWire128_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprWire128_repr___redArg___closed__5_value;
static lean_once_cell_t l_Polydim_V4_instReprWire128_repr___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprWire128_repr___redArg___closed__6;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprWire128___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprWire128_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprWire128___closed__0 = (const lean_object*)&l_Polydim_V4_instReprWire128___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprWire128 = (const lean_object*)&l_Polydim_V4_instReprWire128___closed__0_value;
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqTensorDescriptor_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqTensorDescriptor_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqTensorDescriptor(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqTensorDescriptor___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "domain_id"};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__1_value;
static const lean_string_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "buffer_addr"};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__2_value)}};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "byte_size"};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__5_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprTensorDescriptor___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprTensorDescriptor_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprTensorDescriptor___closed__0 = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprTensorDescriptor = (const lean_object*)&l_Polydim_V4_instReprTensorDescriptor___closed__0_value;
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqGrassmannProjectorCert(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqGrassmannProjectorCert___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "rank_K"};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "ambient_D"};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__5_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "rank_pos"};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__6_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__6_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__7_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "_"};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "rank_bounded"};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__11_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprGrassmannProjectorCert___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprGrassmannProjectorCert_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert___closed__0 = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprGrassmannProjectorCert = (const lean_object*)&l_Polydim_V4_instReprGrassmannProjectorCert___closed__0_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "cross_frobenius_sq"};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4;
static const lean_string_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "cross_bounded"};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__6_value;
static const lean_string_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "same_rank"};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__7_value;
static const lean_ctor_object l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__7_value)}};
static const lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__8_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_CayleySpectralDecomp_ofNat(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqCayleySpectralDecomp(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqCayleySpectralDecomp___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 42, .m_capacity = 42, .m_length = 41, .m_data = "Polydim.V4.CayleySpectralDecomp.in_kernel"};
static const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__1 = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__1_value;
static const lean_string_object l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 41, .m_capacity = 41, .m_length = 40, .m_data = "Polydim.V4.CayleySpectralDecomp.in_range"};
static const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__2 = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__2_value)}};
static const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__3 = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__3_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprCayleySpectralDecomp___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprCayleySpectralDecomp_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprCayleySpectralDecomp = (const lean_object*)&l_Polydim_V4_instReprCayleySpectralDecomp___closed__0_value;
static const lean_string_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "dim"};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "dim_pos"};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__5_value;
static const lean_string_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "input_norm_sq"};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__6_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__6_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__7_value;
static const lean_string_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "output_norm_sq"};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "norm_preserved"};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__11_value;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprCayleyOrthogonalityCert___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert = (const lean_object*)&l_Polydim_V4_instReprCayleyOrthogonalityCert___closed__0_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "dim_kernel"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "dim_range"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__6_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "dim_total"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__7_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__7_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__8_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "h_eig_kernel"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__9_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__9_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__10_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "h_eig_range"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__11_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__11_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__12 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__12_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "dim_sum"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__13 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__13_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__13_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__14 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__14_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "eig_kernel"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__15 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__15_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__15_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__16 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__16_value;
static const lean_string_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "eig_range"};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__17 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__17_value;
static const lean_ctor_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__17_value)}};
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__18 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__18_value;
static lean_once_cell_t l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19;
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_V4_instReprCayleyAsymptoticReflectorCert___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert___closed__0 = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert = (const lean_object*)&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert___closed__0_value;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__fraction__lattice__bits;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__integer__exponent__bits;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__term__growth__bits;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__sign__bit;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__word__size;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__num__gpr__words;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__minimal__signed__width;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__implementation__width;
LEAN_EXPORT lean_object* l_Polydim_V4_kulisch__implementation__guard__margin;
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorIdx(uint8_t v_x_1_){
_start:
{
switch(v_x_1_)
{
case 0:
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(0u);
return v___x_2_;
}
case 1:
{
lean_object* v___x_3_; 
v___x_3_ = lean_unsigned_to_nat(1u);
return v___x_3_;
}
case 2:
{
lean_object* v___x_4_; 
v___x_4_ = lean_unsigned_to_nat(2u);
return v___x_4_;
}
default: 
{
lean_object* v___x_5_; 
v___x_5_ = lean_unsigned_to_nat(3u);
return v___x_5_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorIdx___boxed(lean_object* v_x_6_){
_start:
{
uint8_t v_x_boxed_7_; lean_object* v_res_8_; 
v_x_boxed_7_ = lean_unbox(v_x_6_);
v_res_8_ = l_Polydim_V4_MemoryDomain_ctorIdx(v_x_boxed_7_);
return v_res_8_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___redArg(lean_object* v_k_9_){
_start:
{
lean_inc(v_k_9_);
return v_k_9_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___redArg___boxed(lean_object* v_k_10_){
_start:
{
lean_object* v_res_11_; 
v_res_11_ = l_Polydim_V4_MemoryDomain_ctorElim___redArg(v_k_10_);
lean_dec(v_k_10_);
return v_res_11_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim(lean_object* v_motive_12_, lean_object* v_ctorIdx_13_, uint8_t v_t_14_, lean_object* v_h_15_, lean_object* v_k_16_){
_start:
{
lean_inc(v_k_16_);
return v_k_16_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ctorElim___boxed(lean_object* v_motive_17_, lean_object* v_ctorIdx_18_, lean_object* v_t_19_, lean_object* v_h_20_, lean_object* v_k_21_){
_start:
{
uint8_t v_t_boxed_22_; lean_object* v_res_23_; 
v_t_boxed_22_ = lean_unbox(v_t_19_);
v_res_23_ = l_Polydim_V4_MemoryDomain_ctorElim(v_motive_17_, v_ctorIdx_18_, v_t_boxed_22_, v_h_20_, v_k_21_);
lean_dec(v_k_21_);
lean_dec(v_ctorIdx_18_);
return v_res_23_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___redArg(lean_object* v_HOST__SHM_24_){
_start:
{
lean_inc(v_HOST__SHM_24_);
return v_HOST__SHM_24_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___redArg___boxed(lean_object* v_HOST__SHM_25_){
_start:
{
lean_object* v_res_26_; 
v_res_26_ = l_Polydim_V4_MemoryDomain_HOST__SHM_elim___redArg(v_HOST__SHM_25_);
lean_dec(v_HOST__SHM_25_);
return v_res_26_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim(lean_object* v_motive_27_, uint8_t v_t_28_, lean_object* v_h_29_, lean_object* v_HOST__SHM_30_){
_start:
{
lean_inc(v_HOST__SHM_30_);
return v_HOST__SHM_30_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_HOST__SHM_elim___boxed(lean_object* v_motive_31_, lean_object* v_t_32_, lean_object* v_h_33_, lean_object* v_HOST__SHM_34_){
_start:
{
uint8_t v_t_boxed_35_; lean_object* v_res_36_; 
v_t_boxed_35_ = lean_unbox(v_t_32_);
v_res_36_ = l_Polydim_V4_MemoryDomain_HOST__SHM_elim(v_motive_31_, v_t_boxed_35_, v_h_33_, v_HOST__SHM_34_);
lean_dec(v_HOST__SHM_34_);
return v_res_36_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___redArg(lean_object* v_CUDA__VRAM_37_){
_start:
{
lean_inc(v_CUDA__VRAM_37_);
return v_CUDA__VRAM_37_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___redArg___boxed(lean_object* v_CUDA__VRAM_38_){
_start:
{
lean_object* v_res_39_; 
v_res_39_ = l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___redArg(v_CUDA__VRAM_38_);
lean_dec(v_CUDA__VRAM_38_);
return v_res_39_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim(lean_object* v_motive_40_, uint8_t v_t_41_, lean_object* v_h_42_, lean_object* v_CUDA__VRAM_43_){
_start:
{
lean_inc(v_CUDA__VRAM_43_);
return v_CUDA__VRAM_43_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim___boxed(lean_object* v_motive_44_, lean_object* v_t_45_, lean_object* v_h_46_, lean_object* v_CUDA__VRAM_47_){
_start:
{
uint8_t v_t_boxed_48_; lean_object* v_res_49_; 
v_t_boxed_48_ = lean_unbox(v_t_45_);
v_res_49_ = l_Polydim_V4_MemoryDomain_CUDA__VRAM_elim(v_motive_44_, v_t_boxed_48_, v_h_46_, v_CUDA__VRAM_47_);
lean_dec(v_CUDA__VRAM_47_);
return v_res_49_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___redArg(lean_object* v_ROCM__VRAM_50_){
_start:
{
lean_inc(v_ROCM__VRAM_50_);
return v_ROCM__VRAM_50_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___redArg___boxed(lean_object* v_ROCM__VRAM_51_){
_start:
{
lean_object* v_res_52_; 
v_res_52_ = l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___redArg(v_ROCM__VRAM_51_);
lean_dec(v_ROCM__VRAM_51_);
return v_res_52_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim(lean_object* v_motive_53_, uint8_t v_t_54_, lean_object* v_h_55_, lean_object* v_ROCM__VRAM_56_){
_start:
{
lean_inc(v_ROCM__VRAM_56_);
return v_ROCM__VRAM_56_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim___boxed(lean_object* v_motive_57_, lean_object* v_t_58_, lean_object* v_h_59_, lean_object* v_ROCM__VRAM_60_){
_start:
{
uint8_t v_t_boxed_61_; lean_object* v_res_62_; 
v_t_boxed_61_ = lean_unbox(v_t_58_);
v_res_62_ = l_Polydim_V4_MemoryDomain_ROCM__VRAM_elim(v_motive_57_, v_t_boxed_61_, v_h_59_, v_ROCM__VRAM_60_);
lean_dec(v_ROCM__VRAM_60_);
return v_res_62_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___redArg(lean_object* v_RDMA__FABRIC_63_){
_start:
{
lean_inc(v_RDMA__FABRIC_63_);
return v_RDMA__FABRIC_63_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___redArg___boxed(lean_object* v_RDMA__FABRIC_64_){
_start:
{
lean_object* v_res_65_; 
v_res_65_ = l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___redArg(v_RDMA__FABRIC_64_);
lean_dec(v_RDMA__FABRIC_64_);
return v_res_65_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim(lean_object* v_motive_66_, uint8_t v_t_67_, lean_object* v_h_68_, lean_object* v_RDMA__FABRIC_69_){
_start:
{
lean_inc(v_RDMA__FABRIC_69_);
return v_RDMA__FABRIC_69_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim___boxed(lean_object* v_motive_70_, lean_object* v_t_71_, lean_object* v_h_72_, lean_object* v_RDMA__FABRIC_73_){
_start:
{
uint8_t v_t_boxed_74_; lean_object* v_res_75_; 
v_t_boxed_74_ = lean_unbox(v_t_71_);
v_res_75_ = l_Polydim_V4_MemoryDomain_RDMA__FABRIC_elim(v_motive_70_, v_t_boxed_74_, v_h_72_, v_RDMA__FABRIC_73_);
lean_dec(v_RDMA__FABRIC_73_);
return v_res_75_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_MemoryDomain_ofNat(lean_object* v_n_76_){
_start:
{
lean_object* v___x_77_; uint8_t v___x_78_; 
v___x_77_ = lean_unsigned_to_nat(1u);
v___x_78_ = lean_nat_dec_le(v_n_76_, v___x_77_);
if (v___x_78_ == 0)
{
lean_object* v___x_79_; uint8_t v___x_80_; 
v___x_79_ = lean_unsigned_to_nat(2u);
v___x_80_ = lean_nat_dec_le(v_n_76_, v___x_79_);
if (v___x_80_ == 0)
{
uint8_t v___x_81_; 
v___x_81_ = 3;
return v___x_81_;
}
else
{
uint8_t v___x_82_; 
v___x_82_ = 2;
return v___x_82_;
}
}
else
{
lean_object* v___x_83_; uint8_t v___x_84_; 
v___x_83_ = lean_unsigned_to_nat(0u);
v___x_84_ = lean_nat_dec_le(v_n_76_, v___x_83_);
if (v___x_84_ == 0)
{
uint8_t v___x_85_; 
v___x_85_ = 1;
return v___x_85_;
}
else
{
uint8_t v___x_86_; 
v___x_86_ = 0;
return v___x_86_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_MemoryDomain_ofNat___boxed(lean_object* v_n_87_){
_start:
{
uint8_t v_res_88_; lean_object* v_r_89_; 
v_res_88_ = l_Polydim_V4_MemoryDomain_ofNat(v_n_87_);
lean_dec(v_n_87_);
v_r_89_ = lean_box(v_res_88_);
return v_r_89_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqMemoryDomain(uint8_t v_x_90_, uint8_t v_y_91_){
_start:
{
lean_object* v___x_92_; lean_object* v___x_93_; uint8_t v___x_94_; 
v___x_92_ = l_Polydim_V4_MemoryDomain_ctorIdx(v_x_90_);
v___x_93_ = l_Polydim_V4_MemoryDomain_ctorIdx(v_y_91_);
v___x_94_ = lean_nat_dec_eq(v___x_92_, v___x_93_);
lean_dec(v___x_93_);
lean_dec(v___x_92_);
return v___x_94_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqMemoryDomain___boxed(lean_object* v_x_95_, lean_object* v_y_96_){
_start:
{
uint8_t v_x_13__boxed_97_; uint8_t v_y_14__boxed_98_; uint8_t v_res_99_; lean_object* v_r_100_; 
v_x_13__boxed_97_ = lean_unbox(v_x_95_);
v_y_14__boxed_98_ = lean_unbox(v_y_96_);
v_res_99_ = l_Polydim_V4_instDecidableEqMemoryDomain(v_x_13__boxed_97_, v_y_14__boxed_98_);
v_r_100_ = lean_box(v_res_99_);
return v_r_100_;
}
}
static lean_object* _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8(void){
_start:
{
lean_object* v___x_113_; lean_object* v___x_114_; 
v___x_113_ = lean_unsigned_to_nat(2u);
v___x_114_ = lean_nat_to_int(v___x_113_);
return v___x_114_;
}
}
static lean_object* _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9(void){
_start:
{
lean_object* v___x_115_; lean_object* v___x_116_; 
v___x_115_ = lean_unsigned_to_nat(1u);
v___x_116_ = lean_nat_to_int(v___x_115_);
return v___x_116_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprMemoryDomain_repr(uint8_t v_x_117_, lean_object* v_prec_118_){
_start:
{
lean_object* v___y_120_; lean_object* v___y_127_; lean_object* v___y_134_; lean_object* v___y_141_; 
switch(v_x_117_)
{
case 0:
{
lean_object* v___x_147_; uint8_t v___x_148_; 
v___x_147_ = lean_unsigned_to_nat(1024u);
v___x_148_ = lean_nat_dec_le(v___x_147_, v_prec_118_);
if (v___x_148_ == 0)
{
lean_object* v___x_149_; 
v___x_149_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_120_ = v___x_149_;
goto v___jp_119_;
}
else
{
lean_object* v___x_150_; 
v___x_150_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_120_ = v___x_150_;
goto v___jp_119_;
}
}
case 1:
{
lean_object* v___x_151_; uint8_t v___x_152_; 
v___x_151_ = lean_unsigned_to_nat(1024u);
v___x_152_ = lean_nat_dec_le(v___x_151_, v_prec_118_);
if (v___x_152_ == 0)
{
lean_object* v___x_153_; 
v___x_153_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_127_ = v___x_153_;
goto v___jp_126_;
}
else
{
lean_object* v___x_154_; 
v___x_154_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_127_ = v___x_154_;
goto v___jp_126_;
}
}
case 2:
{
lean_object* v___x_155_; uint8_t v___x_156_; 
v___x_155_ = lean_unsigned_to_nat(1024u);
v___x_156_ = lean_nat_dec_le(v___x_155_, v_prec_118_);
if (v___x_156_ == 0)
{
lean_object* v___x_157_; 
v___x_157_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_134_ = v___x_157_;
goto v___jp_133_;
}
else
{
lean_object* v___x_158_; 
v___x_158_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_134_ = v___x_158_;
goto v___jp_133_;
}
}
default: 
{
lean_object* v___x_159_; uint8_t v___x_160_; 
v___x_159_ = lean_unsigned_to_nat(1024u);
v___x_160_ = lean_nat_dec_le(v___x_159_, v_prec_118_);
if (v___x_160_ == 0)
{
lean_object* v___x_161_; 
v___x_161_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_141_ = v___x_161_;
goto v___jp_140_;
}
else
{
lean_object* v___x_162_; 
v___x_162_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_141_ = v___x_162_;
goto v___jp_140_;
}
}
}
v___jp_119_:
{
lean_object* v___x_121_; lean_object* v___x_122_; uint8_t v___x_123_; lean_object* v___x_124_; lean_object* v___x_125_; 
v___x_121_ = ((lean_object*)(l_Polydim_V4_instReprMemoryDomain_repr___closed__1));
lean_inc(v___y_120_);
v___x_122_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_122_, 0, v___y_120_);
lean_ctor_set(v___x_122_, 1, v___x_121_);
v___x_123_ = 0;
v___x_124_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_124_, 0, v___x_122_);
lean_ctor_set_uint8(v___x_124_, sizeof(void*)*1, v___x_123_);
v___x_125_ = l_Repr_addAppParen(v___x_124_, v_prec_118_);
return v___x_125_;
}
v___jp_126_:
{
lean_object* v___x_128_; lean_object* v___x_129_; uint8_t v___x_130_; lean_object* v___x_131_; lean_object* v___x_132_; 
v___x_128_ = ((lean_object*)(l_Polydim_V4_instReprMemoryDomain_repr___closed__3));
lean_inc(v___y_127_);
v___x_129_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_129_, 0, v___y_127_);
lean_ctor_set(v___x_129_, 1, v___x_128_);
v___x_130_ = 0;
v___x_131_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_131_, 0, v___x_129_);
lean_ctor_set_uint8(v___x_131_, sizeof(void*)*1, v___x_130_);
v___x_132_ = l_Repr_addAppParen(v___x_131_, v_prec_118_);
return v___x_132_;
}
v___jp_133_:
{
lean_object* v___x_135_; lean_object* v___x_136_; uint8_t v___x_137_; lean_object* v___x_138_; lean_object* v___x_139_; 
v___x_135_ = ((lean_object*)(l_Polydim_V4_instReprMemoryDomain_repr___closed__5));
lean_inc(v___y_134_);
v___x_136_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_136_, 0, v___y_134_);
lean_ctor_set(v___x_136_, 1, v___x_135_);
v___x_137_ = 0;
v___x_138_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_138_, 0, v___x_136_);
lean_ctor_set_uint8(v___x_138_, sizeof(void*)*1, v___x_137_);
v___x_139_ = l_Repr_addAppParen(v___x_138_, v_prec_118_);
return v___x_139_;
}
v___jp_140_:
{
lean_object* v___x_142_; lean_object* v___x_143_; uint8_t v___x_144_; lean_object* v___x_145_; lean_object* v___x_146_; 
v___x_142_ = ((lean_object*)(l_Polydim_V4_instReprMemoryDomain_repr___closed__7));
lean_inc(v___y_141_);
v___x_143_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_143_, 0, v___y_141_);
lean_ctor_set(v___x_143_, 1, v___x_142_);
v___x_144_ = 0;
v___x_145_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_145_, 0, v___x_143_);
lean_ctor_set_uint8(v___x_145_, sizeof(void*)*1, v___x_144_);
v___x_146_ = l_Repr_addAppParen(v___x_145_, v_prec_118_);
return v___x_146_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprMemoryDomain_repr___boxed(lean_object* v_x_163_, lean_object* v_prec_164_){
_start:
{
uint8_t v_x_233__boxed_165_; lean_object* v_res_166_; 
v_x_233__boxed_165_ = lean_unbox(v_x_163_);
v_res_166_ = l_Polydim_V4_instReprMemoryDomain_repr(v_x_233__boxed_165_, v_prec_164_);
lean_dec(v_prec_164_);
return v_res_166_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq(lean_object* v_x_169_, lean_object* v_x_170_){
_start:
{
lean_object* v_epoch_171_; lean_object* v_node__id_172_; lean_object* v_base__addr_173_; lean_object* v_byte__length_174_; uint8_t v_is__committed__read_175_; uint8_t v_memory__domain_176_; lean_object* v_epoch_177_; lean_object* v_node__id_178_; lean_object* v_base__addr_179_; lean_object* v_byte__length_180_; uint8_t v_is__committed__read_181_; uint8_t v_memory__domain_182_; uint8_t v___x_183_; 
v_epoch_171_ = lean_ctor_get(v_x_169_, 0);
v_node__id_172_ = lean_ctor_get(v_x_169_, 1);
v_base__addr_173_ = lean_ctor_get(v_x_169_, 2);
v_byte__length_174_ = lean_ctor_get(v_x_169_, 3);
v_is__committed__read_175_ = lean_ctor_get_uint8(v_x_169_, sizeof(void*)*4);
v_memory__domain_176_ = lean_ctor_get_uint8(v_x_169_, sizeof(void*)*4 + 1);
v_epoch_177_ = lean_ctor_get(v_x_170_, 0);
v_node__id_178_ = lean_ctor_get(v_x_170_, 1);
v_base__addr_179_ = lean_ctor_get(v_x_170_, 2);
v_byte__length_180_ = lean_ctor_get(v_x_170_, 3);
v_is__committed__read_181_ = lean_ctor_get_uint8(v_x_170_, sizeof(void*)*4);
v_memory__domain_182_ = lean_ctor_get_uint8(v_x_170_, sizeof(void*)*4 + 1);
v___x_183_ = lean_nat_dec_eq(v_epoch_171_, v_epoch_177_);
if (v___x_183_ == 0)
{
return v___x_183_;
}
else
{
uint8_t v___x_184_; 
v___x_184_ = lean_nat_dec_eq(v_node__id_172_, v_node__id_178_);
if (v___x_184_ == 0)
{
return v___x_184_;
}
else
{
uint8_t v___x_185_; 
v___x_185_ = lean_nat_dec_eq(v_base__addr_173_, v_base__addr_179_);
if (v___x_185_ == 0)
{
return v___x_185_;
}
else
{
uint8_t v___x_186_; 
v___x_186_ = lean_nat_dec_eq(v_byte__length_174_, v_byte__length_180_);
if (v___x_186_ == 0)
{
return v___x_186_;
}
else
{
if (v_is__committed__read_175_ == 0)
{
if (v_is__committed__read_181_ == 0)
{
uint8_t v___x_187_; 
v___x_187_ = l_Polydim_V4_instDecidableEqMemoryDomain(v_memory__domain_176_, v_memory__domain_182_);
return v___x_187_;
}
else
{
return v_is__committed__read_175_;
}
}
else
{
if (v_is__committed__read_181_ == 0)
{
return v_is__committed__read_181_;
}
else
{
uint8_t v___x_188_; 
v___x_188_ = l_Polydim_V4_instDecidableEqMemoryDomain(v_memory__domain_176_, v_memory__domain_182_);
return v___x_188_;
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq___boxed(lean_object* v_x_189_, lean_object* v_x_190_){
_start:
{
uint8_t v_res_191_; lean_object* v_r_192_; 
v_res_191_ = l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq(v_x_189_, v_x_190_);
lean_dec_ref(v_x_190_);
lean_dec_ref(v_x_189_);
v_r_192_ = lean_box(v_res_191_);
return v_r_192_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqLeaseDescriptor(lean_object* v_x_193_, lean_object* v_x_194_){
_start:
{
uint8_t v___x_195_; 
v___x_195_ = l_Polydim_V4_instDecidableEqLeaseDescriptor_decEq(v_x_193_, v_x_194_);
return v___x_195_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqLeaseDescriptor___boxed(lean_object* v_x_196_, lean_object* v_x_197_){
_start:
{
uint8_t v_res_198_; lean_object* v_r_199_; 
v_res_198_ = l_Polydim_V4_instDecidableEqLeaseDescriptor(v_x_196_, v_x_197_);
lean_dec_ref(v_x_197_);
lean_dec_ref(v_x_196_);
v_r_199_ = lean_box(v_res_198_);
return v_r_199_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_213_; lean_object* v___x_214_; 
v___x_213_ = lean_unsigned_to_nat(9u);
v___x_214_ = lean_nat_to_int(v___x_213_);
return v___x_214_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12(void){
_start:
{
lean_object* v___x_221_; lean_object* v___x_222_; 
v___x_221_ = lean_unsigned_to_nat(11u);
v___x_222_ = lean_nat_to_int(v___x_221_);
return v___x_222_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15(void){
_start:
{
lean_object* v___x_226_; lean_object* v___x_227_; 
v___x_226_ = lean_unsigned_to_nat(13u);
v___x_227_ = lean_nat_to_int(v___x_226_);
return v___x_227_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18(void){
_start:
{
lean_object* v___x_231_; lean_object* v___x_232_; 
v___x_231_ = lean_unsigned_to_nat(15u);
v___x_232_ = lean_nat_to_int(v___x_231_);
return v___x_232_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21(void){
_start:
{
lean_object* v___x_236_; lean_object* v___x_237_; 
v___x_236_ = lean_unsigned_to_nat(21u);
v___x_237_ = lean_nat_to_int(v___x_236_);
return v___x_237_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24(void){
_start:
{
lean_object* v___x_241_; lean_object* v___x_242_; 
v___x_241_ = lean_unsigned_to_nat(17u);
v___x_242_ = lean_nat_to_int(v___x_241_);
return v___x_242_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26(void){
_start:
{
lean_object* v___x_244_; lean_object* v___x_245_; 
v___x_244_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__0));
v___x_245_ = lean_string_length(v___x_244_);
return v___x_245_;
}
}
static lean_object* _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27(void){
_start:
{
lean_object* v___x_246_; lean_object* v___x_247_; 
v___x_246_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__26);
v___x_247_ = lean_nat_to_int(v___x_246_);
return v___x_247_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___redArg(lean_object* v_x_252_){
_start:
{
lean_object* v_epoch_253_; lean_object* v_node__id_254_; lean_object* v_base__addr_255_; lean_object* v_byte__length_256_; uint8_t v_is__committed__read_257_; uint8_t v_memory__domain_258_; lean_object* v___x_259_; lean_object* v___x_260_; lean_object* v___x_261_; lean_object* v___x_262_; lean_object* v___x_263_; lean_object* v___x_264_; uint8_t v___x_265_; lean_object* v___x_266_; lean_object* v___x_267_; lean_object* v___x_268_; lean_object* v___x_269_; lean_object* v___x_270_; lean_object* v___x_271_; lean_object* v___x_272_; lean_object* v___x_273_; lean_object* v___x_274_; lean_object* v___x_275_; lean_object* v___x_276_; lean_object* v___x_277_; lean_object* v___x_278_; lean_object* v___x_279_; lean_object* v___x_280_; lean_object* v___x_281_; lean_object* v___x_282_; lean_object* v___x_283_; lean_object* v___x_284_; lean_object* v___x_285_; lean_object* v___x_286_; lean_object* v___x_287_; lean_object* v___x_288_; lean_object* v___x_289_; lean_object* v___x_290_; lean_object* v___x_291_; lean_object* v___x_292_; lean_object* v___x_293_; lean_object* v___x_294_; lean_object* v___x_295_; lean_object* v___x_296_; lean_object* v___x_297_; lean_object* v___x_298_; lean_object* v___x_299_; lean_object* v___x_300_; lean_object* v___x_301_; lean_object* v___x_302_; lean_object* v___x_303_; lean_object* v___x_304_; lean_object* v___x_305_; lean_object* v___x_306_; lean_object* v___x_307_; lean_object* v___x_308_; lean_object* v___x_309_; lean_object* v___x_310_; lean_object* v___x_311_; lean_object* v___x_312_; lean_object* v___x_313_; lean_object* v___x_314_; lean_object* v___x_315_; lean_object* v___x_316_; lean_object* v___x_317_; lean_object* v___x_318_; lean_object* v___x_319_; lean_object* v___x_320_; lean_object* v___x_321_; lean_object* v___x_322_; lean_object* v___x_323_; lean_object* v___x_324_; lean_object* v___x_325_; lean_object* v___x_326_; lean_object* v___x_327_; lean_object* v___x_328_; lean_object* v___x_329_; lean_object* v___x_330_; 
v_epoch_253_ = lean_ctor_get(v_x_252_, 0);
lean_inc(v_epoch_253_);
v_node__id_254_ = lean_ctor_get(v_x_252_, 1);
lean_inc(v_node__id_254_);
v_base__addr_255_ = lean_ctor_get(v_x_252_, 2);
lean_inc(v_base__addr_255_);
v_byte__length_256_ = lean_ctor_get(v_x_252_, 3);
lean_inc(v_byte__length_256_);
v_is__committed__read_257_ = lean_ctor_get_uint8(v_x_252_, sizeof(void*)*4);
v_memory__domain_258_ = lean_ctor_get_uint8(v_x_252_, sizeof(void*)*4 + 1);
lean_dec_ref(v_x_252_);
v___x_259_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_260_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__6));
v___x_261_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7);
v___x_262_ = l_Nat_reprFast(v_epoch_253_);
v___x_263_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_263_, 0, v___x_262_);
v___x_264_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_264_, 0, v___x_261_);
lean_ctor_set(v___x_264_, 1, v___x_263_);
v___x_265_ = 0;
v___x_266_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_266_, 0, v___x_264_);
lean_ctor_set_uint8(v___x_266_, sizeof(void*)*1, v___x_265_);
v___x_267_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_267_, 0, v___x_260_);
lean_ctor_set(v___x_267_, 1, v___x_266_);
v___x_268_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_269_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_269_, 0, v___x_267_);
lean_ctor_set(v___x_269_, 1, v___x_268_);
v___x_270_ = lean_box(1);
v___x_271_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_271_, 0, v___x_269_);
lean_ctor_set(v___x_271_, 1, v___x_270_);
v___x_272_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__11));
v___x_273_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_273_, 0, v___x_271_);
lean_ctor_set(v___x_273_, 1, v___x_272_);
v___x_274_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_274_, 0, v___x_273_);
lean_ctor_set(v___x_274_, 1, v___x_259_);
v___x_275_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12);
v___x_276_ = l_Nat_reprFast(v_node__id_254_);
v___x_277_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_277_, 0, v___x_276_);
v___x_278_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_278_, 0, v___x_275_);
lean_ctor_set(v___x_278_, 1, v___x_277_);
v___x_279_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_279_, 0, v___x_278_);
lean_ctor_set_uint8(v___x_279_, sizeof(void*)*1, v___x_265_);
v___x_280_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_280_, 0, v___x_274_);
lean_ctor_set(v___x_280_, 1, v___x_279_);
v___x_281_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_281_, 0, v___x_280_);
lean_ctor_set(v___x_281_, 1, v___x_268_);
v___x_282_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_282_, 0, v___x_281_);
lean_ctor_set(v___x_282_, 1, v___x_270_);
v___x_283_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__14));
v___x_284_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_284_, 0, v___x_282_);
lean_ctor_set(v___x_284_, 1, v___x_283_);
v___x_285_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_285_, 0, v___x_284_);
lean_ctor_set(v___x_285_, 1, v___x_259_);
v___x_286_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15);
v___x_287_ = l_Nat_reprFast(v_base__addr_255_);
v___x_288_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_288_, 0, v___x_287_);
v___x_289_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_289_, 0, v___x_286_);
lean_ctor_set(v___x_289_, 1, v___x_288_);
v___x_290_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_290_, 0, v___x_289_);
lean_ctor_set_uint8(v___x_290_, sizeof(void*)*1, v___x_265_);
v___x_291_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_291_, 0, v___x_285_);
lean_ctor_set(v___x_291_, 1, v___x_290_);
v___x_292_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_292_, 0, v___x_291_);
lean_ctor_set(v___x_292_, 1, v___x_268_);
v___x_293_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_293_, 0, v___x_292_);
lean_ctor_set(v___x_293_, 1, v___x_270_);
v___x_294_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__17));
v___x_295_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_295_, 0, v___x_293_);
lean_ctor_set(v___x_295_, 1, v___x_294_);
v___x_296_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_296_, 0, v___x_295_);
lean_ctor_set(v___x_296_, 1, v___x_259_);
v___x_297_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18);
v___x_298_ = l_Nat_reprFast(v_byte__length_256_);
v___x_299_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_299_, 0, v___x_298_);
v___x_300_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_300_, 0, v___x_297_);
lean_ctor_set(v___x_300_, 1, v___x_299_);
v___x_301_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_301_, 0, v___x_300_);
lean_ctor_set_uint8(v___x_301_, sizeof(void*)*1, v___x_265_);
v___x_302_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_302_, 0, v___x_296_);
lean_ctor_set(v___x_302_, 1, v___x_301_);
v___x_303_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_303_, 0, v___x_302_);
lean_ctor_set(v___x_303_, 1, v___x_268_);
v___x_304_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_304_, 0, v___x_303_);
lean_ctor_set(v___x_304_, 1, v___x_270_);
v___x_305_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__20));
v___x_306_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_306_, 0, v___x_304_);
lean_ctor_set(v___x_306_, 1, v___x_305_);
v___x_307_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_307_, 0, v___x_306_);
lean_ctor_set(v___x_307_, 1, v___x_259_);
v___x_308_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__21);
v___x_309_ = lean_unsigned_to_nat(0u);
v___x_310_ = l_Bool_repr___redArg(v_is__committed__read_257_);
v___x_311_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_311_, 0, v___x_308_);
lean_ctor_set(v___x_311_, 1, v___x_310_);
v___x_312_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_312_, 0, v___x_311_);
lean_ctor_set_uint8(v___x_312_, sizeof(void*)*1, v___x_265_);
v___x_313_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_313_, 0, v___x_307_);
lean_ctor_set(v___x_313_, 1, v___x_312_);
v___x_314_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_314_, 0, v___x_313_);
lean_ctor_set(v___x_314_, 1, v___x_268_);
v___x_315_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_315_, 0, v___x_314_);
lean_ctor_set(v___x_315_, 1, v___x_270_);
v___x_316_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__23));
v___x_317_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_317_, 0, v___x_315_);
lean_ctor_set(v___x_317_, 1, v___x_316_);
v___x_318_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_318_, 0, v___x_317_);
lean_ctor_set(v___x_318_, 1, v___x_259_);
v___x_319_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24);
v___x_320_ = l_Polydim_V4_instReprMemoryDomain_repr(v_memory__domain_258_, v___x_309_);
v___x_321_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_321_, 0, v___x_319_);
lean_ctor_set(v___x_321_, 1, v___x_320_);
v___x_322_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_322_, 0, v___x_321_);
lean_ctor_set_uint8(v___x_322_, sizeof(void*)*1, v___x_265_);
v___x_323_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_323_, 0, v___x_318_);
lean_ctor_set(v___x_323_, 1, v___x_322_);
v___x_324_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_325_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_326_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_326_, 0, v___x_325_);
lean_ctor_set(v___x_326_, 1, v___x_323_);
v___x_327_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_328_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_328_, 0, v___x_326_);
lean_ctor_set(v___x_328_, 1, v___x_327_);
v___x_329_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_329_, 0, v___x_324_);
lean_ctor_set(v___x_329_, 1, v___x_328_);
v___x_330_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_330_, 0, v___x_329_);
lean_ctor_set_uint8(v___x_330_, sizeof(void*)*1, v___x_265_);
return v___x_330_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr(lean_object* v_x_331_, lean_object* v_prec_332_){
_start:
{
lean_object* v___x_333_; 
v___x_333_ = l_Polydim_V4_instReprLeaseDescriptor_repr___redArg(v_x_331_);
return v___x_333_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprLeaseDescriptor_repr___boxed(lean_object* v_x_334_, lean_object* v_prec_335_){
_start:
{
lean_object* v_res_336_; 
v_res_336_ = l_Polydim_V4_instReprLeaseDescriptor_repr(v_x_334_, v_prec_335_);
lean_dec(v_prec_335_);
return v_res_336_;
}
}
static lean_object* _init_l_Polydim_V4_subnormal__min__quantum(void){
_start:
{
lean_object* v___x_339_; 
v___x_339_ = lean_unsigned_to_nat(1u);
return v___x_339_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqNeumaierState_decEq(lean_object* v_x_340_, lean_object* v_x_341_){
_start:
{
lean_object* v_sum_342_; lean_object* v_residue_343_; lean_object* v_sum_344_; lean_object* v_residue_345_; uint8_t v___x_346_; 
v_sum_342_ = lean_ctor_get(v_x_340_, 0);
v_residue_343_ = lean_ctor_get(v_x_340_, 1);
v_sum_344_ = lean_ctor_get(v_x_341_, 0);
v_residue_345_ = lean_ctor_get(v_x_341_, 1);
v___x_346_ = lean_nat_dec_eq(v_sum_342_, v_sum_344_);
if (v___x_346_ == 0)
{
return v___x_346_;
}
else
{
uint8_t v___x_347_; 
v___x_347_ = lean_nat_dec_eq(v_residue_343_, v_residue_345_);
return v___x_347_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqNeumaierState_decEq___boxed(lean_object* v_x_348_, lean_object* v_x_349_){
_start:
{
uint8_t v_res_350_; lean_object* v_r_351_; 
v_res_350_ = l_Polydim_V4_instDecidableEqNeumaierState_decEq(v_x_348_, v_x_349_);
lean_dec_ref(v_x_349_);
lean_dec_ref(v_x_348_);
v_r_351_ = lean_box(v_res_350_);
return v_r_351_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqNeumaierState(lean_object* v_x_352_, lean_object* v_x_353_){
_start:
{
uint8_t v___x_354_; 
v___x_354_ = l_Polydim_V4_instDecidableEqNeumaierState_decEq(v_x_352_, v_x_353_);
return v___x_354_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqNeumaierState___boxed(lean_object* v_x_355_, lean_object* v_x_356_){
_start:
{
uint8_t v_res_357_; lean_object* v_r_358_; 
v_res_357_ = l_Polydim_V4_instDecidableEqNeumaierState(v_x_355_, v_x_356_);
lean_dec_ref(v_x_356_);
lean_dec_ref(v_x_355_);
v_r_358_ = lean_box(v_res_357_);
return v_r_358_;
}
}
static lean_object* _init_l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_368_; lean_object* v___x_369_; 
v___x_368_ = lean_unsigned_to_nat(7u);
v___x_369_ = lean_nat_to_int(v___x_368_);
return v___x_369_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr___redArg(lean_object* v_x_373_){
_start:
{
lean_object* v_sum_374_; lean_object* v_residue_375_; lean_object* v___x_377_; uint8_t v_isShared_378_; uint8_t v_isSharedCheck_410_; 
v_sum_374_ = lean_ctor_get(v_x_373_, 0);
v_residue_375_ = lean_ctor_get(v_x_373_, 1);
v_isSharedCheck_410_ = !lean_is_exclusive(v_x_373_);
if (v_isSharedCheck_410_ == 0)
{
v___x_377_ = v_x_373_;
v_isShared_378_ = v_isSharedCheck_410_;
goto v_resetjp_376_;
}
else
{
lean_inc(v_residue_375_);
lean_inc(v_sum_374_);
lean_dec(v_x_373_);
v___x_377_ = lean_box(0);
v_isShared_378_ = v_isSharedCheck_410_;
goto v_resetjp_376_;
}
v_resetjp_376_:
{
lean_object* v___x_379_; lean_object* v___x_380_; lean_object* v___x_381_; lean_object* v___x_382_; lean_object* v___x_383_; lean_object* v___x_385_; 
v___x_379_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_380_ = ((lean_object*)(l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__3));
v___x_381_ = lean_obj_once(&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4, &l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4_once, _init_l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4);
v___x_382_ = l_Nat_reprFast(v_sum_374_);
v___x_383_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_383_, 0, v___x_382_);
if (v_isShared_378_ == 0)
{
lean_ctor_set_tag(v___x_377_, 4);
lean_ctor_set(v___x_377_, 1, v___x_383_);
lean_ctor_set(v___x_377_, 0, v___x_381_);
v___x_385_ = v___x_377_;
goto v_reusejp_384_;
}
else
{
lean_object* v_reuseFailAlloc_409_; 
v_reuseFailAlloc_409_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_409_, 0, v___x_381_);
lean_ctor_set(v_reuseFailAlloc_409_, 1, v___x_383_);
v___x_385_ = v_reuseFailAlloc_409_;
goto v_reusejp_384_;
}
v_reusejp_384_:
{
uint8_t v___x_386_; lean_object* v___x_387_; lean_object* v___x_388_; lean_object* v___x_389_; lean_object* v___x_390_; lean_object* v___x_391_; lean_object* v___x_392_; lean_object* v___x_393_; lean_object* v___x_394_; lean_object* v___x_395_; lean_object* v___x_396_; lean_object* v___x_397_; lean_object* v___x_398_; lean_object* v___x_399_; lean_object* v___x_400_; lean_object* v___x_401_; lean_object* v___x_402_; lean_object* v___x_403_; lean_object* v___x_404_; lean_object* v___x_405_; lean_object* v___x_406_; lean_object* v___x_407_; lean_object* v___x_408_; 
v___x_386_ = 0;
v___x_387_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_387_, 0, v___x_385_);
lean_ctor_set_uint8(v___x_387_, sizeof(void*)*1, v___x_386_);
v___x_388_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_388_, 0, v___x_380_);
lean_ctor_set(v___x_388_, 1, v___x_387_);
v___x_389_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_390_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_390_, 0, v___x_388_);
lean_ctor_set(v___x_390_, 1, v___x_389_);
v___x_391_ = lean_box(1);
v___x_392_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_392_, 0, v___x_390_);
lean_ctor_set(v___x_392_, 1, v___x_391_);
v___x_393_ = ((lean_object*)(l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__6));
v___x_394_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_394_, 0, v___x_392_);
lean_ctor_set(v___x_394_, 1, v___x_393_);
v___x_395_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_395_, 0, v___x_394_);
lean_ctor_set(v___x_395_, 1, v___x_379_);
v___x_396_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12);
v___x_397_ = l_Nat_reprFast(v_residue_375_);
v___x_398_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_398_, 0, v___x_397_);
v___x_399_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_399_, 0, v___x_396_);
lean_ctor_set(v___x_399_, 1, v___x_398_);
v___x_400_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_400_, 0, v___x_399_);
lean_ctor_set_uint8(v___x_400_, sizeof(void*)*1, v___x_386_);
v___x_401_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_401_, 0, v___x_395_);
lean_ctor_set(v___x_401_, 1, v___x_400_);
v___x_402_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_403_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_404_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_404_, 0, v___x_403_);
lean_ctor_set(v___x_404_, 1, v___x_401_);
v___x_405_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_406_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_406_, 0, v___x_404_);
lean_ctor_set(v___x_406_, 1, v___x_405_);
v___x_407_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_407_, 0, v___x_402_);
lean_ctor_set(v___x_407_, 1, v___x_406_);
v___x_408_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_408_, 0, v___x_407_);
lean_ctor_set_uint8(v___x_408_, sizeof(void*)*1, v___x_386_);
return v___x_408_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr(lean_object* v_x_411_, lean_object* v_prec_412_){
_start:
{
lean_object* v___x_413_; 
v___x_413_ = l_Polydim_V4_instReprNeumaierState_repr___redArg(v_x_411_);
return v___x_413_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprNeumaierState_repr___boxed(lean_object* v_x_414_, lean_object* v_prec_415_){
_start:
{
lean_object* v_res_416_; 
v_res_416_ = l_Polydim_V4_instReprNeumaierState_repr(v_x_414_, v_prec_415_);
lean_dec(v_prec_415_);
return v_res_416_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_NeumaierState_effective__energy(lean_object* v_s_419_){
_start:
{
lean_object* v_sum_420_; lean_object* v_residue_421_; lean_object* v___x_422_; 
v_sum_420_ = lean_ctor_get(v_s_419_, 0);
v_residue_421_ = lean_ctor_get(v_s_419_, 1);
v___x_422_ = lean_nat_add(v_sum_420_, v_residue_421_);
return v___x_422_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_NeumaierState_effective__energy___boxed(lean_object* v_s_423_){
_start:
{
lean_object* v_res_424_; 
v_res_424_ = l_Polydim_V4_NeumaierState_effective__energy(v_s_423_);
lean_dec_ref(v_s_423_);
return v_res_424_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqRcuReader_decEq(lean_object* v_x_425_, lean_object* v_x_426_){
_start:
{
lean_object* v_reader__id_427_; lean_object* v_observed__epoch_428_; uint8_t v_is__active_429_; lean_object* v_reader__id_430_; lean_object* v_observed__epoch_431_; uint8_t v_is__active_432_; uint8_t v___x_433_; 
v_reader__id_427_ = lean_ctor_get(v_x_425_, 0);
v_observed__epoch_428_ = lean_ctor_get(v_x_425_, 1);
v_is__active_429_ = lean_ctor_get_uint8(v_x_425_, sizeof(void*)*2);
v_reader__id_430_ = lean_ctor_get(v_x_426_, 0);
v_observed__epoch_431_ = lean_ctor_get(v_x_426_, 1);
v_is__active_432_ = lean_ctor_get_uint8(v_x_426_, sizeof(void*)*2);
v___x_433_ = lean_nat_dec_eq(v_reader__id_427_, v_reader__id_430_);
if (v___x_433_ == 0)
{
return v___x_433_;
}
else
{
uint8_t v___x_434_; 
v___x_434_ = lean_nat_dec_eq(v_observed__epoch_428_, v_observed__epoch_431_);
if (v___x_434_ == 0)
{
return v___x_434_;
}
else
{
if (v_is__active_429_ == 0)
{
if (v_is__active_432_ == 0)
{
return v___x_434_;
}
else
{
return v_is__active_429_;
}
}
else
{
return v_is__active_432_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqRcuReader_decEq___boxed(lean_object* v_x_435_, lean_object* v_x_436_){
_start:
{
uint8_t v_res_437_; lean_object* v_r_438_; 
v_res_437_ = l_Polydim_V4_instDecidableEqRcuReader_decEq(v_x_435_, v_x_436_);
lean_dec_ref(v_x_436_);
lean_dec_ref(v_x_435_);
v_r_438_ = lean_box(v_res_437_);
return v_r_438_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqRcuReader(lean_object* v_x_439_, lean_object* v_x_440_){
_start:
{
uint8_t v___x_441_; 
v___x_441_ = l_Polydim_V4_instDecidableEqRcuReader_decEq(v_x_439_, v_x_440_);
return v___x_441_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqRcuReader___boxed(lean_object* v_x_442_, lean_object* v_x_443_){
_start:
{
uint8_t v_res_444_; lean_object* v_r_445_; 
v_res_444_ = l_Polydim_V4_instDecidableEqRcuReader(v_x_442_, v_x_443_);
lean_dec_ref(v_x_443_);
lean_dec_ref(v_x_442_);
v_r_445_ = lean_box(v_res_444_);
return v_r_445_;
}
}
static lean_object* _init_l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6(void){
_start:
{
lean_object* v___x_458_; lean_object* v___x_459_; 
v___x_458_ = lean_unsigned_to_nat(18u);
v___x_459_ = lean_nat_to_int(v___x_458_);
return v___x_459_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr___redArg(lean_object* v_x_463_){
_start:
{
lean_object* v_reader__id_464_; lean_object* v_observed__epoch_465_; uint8_t v_is__active_466_; lean_object* v___x_467_; lean_object* v___x_468_; lean_object* v___x_469_; lean_object* v___x_470_; lean_object* v___x_471_; lean_object* v___x_472_; uint8_t v___x_473_; lean_object* v___x_474_; lean_object* v___x_475_; lean_object* v___x_476_; lean_object* v___x_477_; lean_object* v___x_478_; lean_object* v___x_479_; lean_object* v___x_480_; lean_object* v___x_481_; lean_object* v___x_482_; lean_object* v___x_483_; lean_object* v___x_484_; lean_object* v___x_485_; lean_object* v___x_486_; lean_object* v___x_487_; lean_object* v___x_488_; lean_object* v___x_489_; lean_object* v___x_490_; lean_object* v___x_491_; lean_object* v___x_492_; lean_object* v___x_493_; lean_object* v___x_494_; lean_object* v___x_495_; lean_object* v___x_496_; lean_object* v___x_497_; lean_object* v___x_498_; lean_object* v___x_499_; lean_object* v___x_500_; lean_object* v___x_501_; lean_object* v___x_502_; lean_object* v___x_503_; lean_object* v___x_504_; 
v_reader__id_464_ = lean_ctor_get(v_x_463_, 0);
lean_inc(v_reader__id_464_);
v_observed__epoch_465_ = lean_ctor_get(v_x_463_, 1);
lean_inc(v_observed__epoch_465_);
v_is__active_466_ = lean_ctor_get_uint8(v_x_463_, sizeof(void*)*2);
lean_dec_ref(v_x_463_);
v___x_467_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_468_ = ((lean_object*)(l_Polydim_V4_instReprRcuReader_repr___redArg___closed__3));
v___x_469_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15);
v___x_470_ = l_Nat_reprFast(v_reader__id_464_);
v___x_471_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_471_, 0, v___x_470_);
v___x_472_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_472_, 0, v___x_469_);
lean_ctor_set(v___x_472_, 1, v___x_471_);
v___x_473_ = 0;
v___x_474_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_474_, 0, v___x_472_);
lean_ctor_set_uint8(v___x_474_, sizeof(void*)*1, v___x_473_);
v___x_475_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_475_, 0, v___x_468_);
lean_ctor_set(v___x_475_, 1, v___x_474_);
v___x_476_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_477_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_477_, 0, v___x_475_);
lean_ctor_set(v___x_477_, 1, v___x_476_);
v___x_478_ = lean_box(1);
v___x_479_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_479_, 0, v___x_477_);
lean_ctor_set(v___x_479_, 1, v___x_478_);
v___x_480_ = ((lean_object*)(l_Polydim_V4_instReprRcuReader_repr___redArg___closed__5));
v___x_481_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_481_, 0, v___x_479_);
lean_ctor_set(v___x_481_, 1, v___x_480_);
v___x_482_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_482_, 0, v___x_481_);
lean_ctor_set(v___x_482_, 1, v___x_467_);
v___x_483_ = lean_obj_once(&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6, &l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6_once, _init_l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6);
v___x_484_ = l_Nat_reprFast(v_observed__epoch_465_);
v___x_485_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_485_, 0, v___x_484_);
v___x_486_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_486_, 0, v___x_483_);
lean_ctor_set(v___x_486_, 1, v___x_485_);
v___x_487_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_487_, 0, v___x_486_);
lean_ctor_set_uint8(v___x_487_, sizeof(void*)*1, v___x_473_);
v___x_488_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_488_, 0, v___x_482_);
lean_ctor_set(v___x_488_, 1, v___x_487_);
v___x_489_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_489_, 0, v___x_488_);
lean_ctor_set(v___x_489_, 1, v___x_476_);
v___x_490_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_490_, 0, v___x_489_);
lean_ctor_set(v___x_490_, 1, v___x_478_);
v___x_491_ = ((lean_object*)(l_Polydim_V4_instReprRcuReader_repr___redArg___closed__8));
v___x_492_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_492_, 0, v___x_490_);
lean_ctor_set(v___x_492_, 1, v___x_491_);
v___x_493_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_493_, 0, v___x_492_);
lean_ctor_set(v___x_493_, 1, v___x_467_);
v___x_494_ = l_Bool_repr___redArg(v_is__active_466_);
v___x_495_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_495_, 0, v___x_469_);
lean_ctor_set(v___x_495_, 1, v___x_494_);
v___x_496_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_496_, 0, v___x_495_);
lean_ctor_set_uint8(v___x_496_, sizeof(void*)*1, v___x_473_);
v___x_497_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_497_, 0, v___x_493_);
lean_ctor_set(v___x_497_, 1, v___x_496_);
v___x_498_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_499_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_500_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_500_, 0, v___x_499_);
lean_ctor_set(v___x_500_, 1, v___x_497_);
v___x_501_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_502_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_502_, 0, v___x_500_);
lean_ctor_set(v___x_502_, 1, v___x_501_);
v___x_503_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_503_, 0, v___x_498_);
lean_ctor_set(v___x_503_, 1, v___x_502_);
v___x_504_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_504_, 0, v___x_503_);
lean_ctor_set_uint8(v___x_504_, sizeof(void*)*1, v___x_473_);
return v___x_504_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr(lean_object* v_x_505_, lean_object* v_prec_506_){
_start:
{
lean_object* v___x_507_; 
v___x_507_ = l_Polydim_V4_instReprRcuReader_repr___redArg(v_x_505_);
return v___x_507_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuReader_repr___boxed(lean_object* v_x_508_, lean_object* v_prec_509_){
_start:
{
lean_object* v_res_510_; 
v_res_510_ = l_Polydim_V4_instReprRcuReader_repr(v_x_508_, v_prec_509_);
lean_dec(v_prec_509_);
return v_res_510_;
}
}
LEAN_EXPORT lean_object* l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1_spec__2(lean_object* v_x_513_, lean_object* v_x_514_, lean_object* v_x_515_){
_start:
{
if (lean_obj_tag(v_x_515_) == 0)
{
lean_dec(v_x_513_);
return v_x_514_;
}
else
{
lean_object* v_head_516_; lean_object* v_tail_517_; lean_object* v___x_519_; uint8_t v_isShared_520_; uint8_t v_isSharedCheck_527_; 
v_head_516_ = lean_ctor_get(v_x_515_, 0);
v_tail_517_ = lean_ctor_get(v_x_515_, 1);
v_isSharedCheck_527_ = !lean_is_exclusive(v_x_515_);
if (v_isSharedCheck_527_ == 0)
{
v___x_519_ = v_x_515_;
v_isShared_520_ = v_isSharedCheck_527_;
goto v_resetjp_518_;
}
else
{
lean_inc(v_tail_517_);
lean_inc(v_head_516_);
lean_dec(v_x_515_);
v___x_519_ = lean_box(0);
v_isShared_520_ = v_isSharedCheck_527_;
goto v_resetjp_518_;
}
v_resetjp_518_:
{
lean_object* v___x_522_; 
lean_inc(v_x_513_);
if (v_isShared_520_ == 0)
{
lean_ctor_set_tag(v___x_519_, 5);
lean_ctor_set(v___x_519_, 1, v_x_513_);
lean_ctor_set(v___x_519_, 0, v_x_514_);
v___x_522_ = v___x_519_;
goto v_reusejp_521_;
}
else
{
lean_object* v_reuseFailAlloc_526_; 
v_reuseFailAlloc_526_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v_reuseFailAlloc_526_, 0, v_x_514_);
lean_ctor_set(v_reuseFailAlloc_526_, 1, v_x_513_);
v___x_522_ = v_reuseFailAlloc_526_;
goto v_reusejp_521_;
}
v_reusejp_521_:
{
lean_object* v___x_523_; lean_object* v___x_524_; 
v___x_523_ = l_Polydim_V4_instReprRcuReader_repr___redArg(v_head_516_);
v___x_524_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_524_, 0, v___x_522_);
lean_ctor_set(v___x_524_, 1, v___x_523_);
v_x_514_ = v___x_524_;
v_x_515_ = v_tail_517_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1(lean_object* v_x_528_, lean_object* v_x_529_, lean_object* v_x_530_){
_start:
{
if (lean_obj_tag(v_x_530_) == 0)
{
lean_dec(v_x_528_);
return v_x_529_;
}
else
{
lean_object* v_head_531_; lean_object* v_tail_532_; lean_object* v___x_534_; uint8_t v_isShared_535_; uint8_t v_isSharedCheck_542_; 
v_head_531_ = lean_ctor_get(v_x_530_, 0);
v_tail_532_ = lean_ctor_get(v_x_530_, 1);
v_isSharedCheck_542_ = !lean_is_exclusive(v_x_530_);
if (v_isSharedCheck_542_ == 0)
{
v___x_534_ = v_x_530_;
v_isShared_535_ = v_isSharedCheck_542_;
goto v_resetjp_533_;
}
else
{
lean_inc(v_tail_532_);
lean_inc(v_head_531_);
lean_dec(v_x_530_);
v___x_534_ = lean_box(0);
v_isShared_535_ = v_isSharedCheck_542_;
goto v_resetjp_533_;
}
v_resetjp_533_:
{
lean_object* v___x_537_; 
lean_inc(v_x_528_);
if (v_isShared_535_ == 0)
{
lean_ctor_set_tag(v___x_534_, 5);
lean_ctor_set(v___x_534_, 1, v_x_528_);
lean_ctor_set(v___x_534_, 0, v_x_529_);
v___x_537_ = v___x_534_;
goto v_reusejp_536_;
}
else
{
lean_object* v_reuseFailAlloc_541_; 
v_reuseFailAlloc_541_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v_reuseFailAlloc_541_, 0, v_x_529_);
lean_ctor_set(v_reuseFailAlloc_541_, 1, v_x_528_);
v___x_537_ = v_reuseFailAlloc_541_;
goto v_reusejp_536_;
}
v_reusejp_536_:
{
lean_object* v___x_538_; lean_object* v___x_539_; lean_object* v___x_540_; 
v___x_538_ = l_Polydim_V4_instReprRcuReader_repr___redArg(v_head_531_);
v___x_539_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_539_, 0, v___x_537_);
lean_ctor_set(v___x_539_, 1, v___x_538_);
v___x_540_ = l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1_spec__2(v_x_528_, v___x_539_, v_tail_532_);
return v___x_540_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0(lean_object* v_x_543_, lean_object* v_x_544_){
_start:
{
if (lean_obj_tag(v_x_543_) == 0)
{
lean_object* v___x_545_; 
lean_dec(v_x_544_);
v___x_545_ = lean_box(0);
return v___x_545_;
}
else
{
lean_object* v_tail_546_; 
v_tail_546_ = lean_ctor_get(v_x_543_, 1);
if (lean_obj_tag(v_tail_546_) == 0)
{
lean_object* v_head_547_; lean_object* v___x_548_; 
lean_dec(v_x_544_);
v_head_547_ = lean_ctor_get(v_x_543_, 0);
lean_inc(v_head_547_);
lean_dec_ref_known(v_x_543_, 2);
v___x_548_ = l_Polydim_V4_instReprRcuReader_repr___redArg(v_head_547_);
return v___x_548_;
}
else
{
lean_object* v_head_549_; lean_object* v___x_550_; lean_object* v___x_551_; 
lean_inc(v_tail_546_);
v_head_549_ = lean_ctor_get(v_x_543_, 0);
lean_inc(v_head_549_);
lean_dec_ref_known(v_x_543_, 2);
v___x_550_ = l_Polydim_V4_instReprRcuReader_repr___redArg(v_head_549_);
v___x_551_ = l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0_spec__1(v_x_544_, v___x_550_, v_tail_546_);
return v___x_551_;
}
}
}
}
static lean_object* _init_l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5(void){
_start:
{
lean_object* v___x_560_; lean_object* v___x_561_; 
v___x_560_ = ((lean_object*)(l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__2));
v___x_561_ = lean_string_length(v___x_560_);
return v___x_561_;
}
}
static lean_object* _init_l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6(void){
_start:
{
lean_object* v___x_562_; lean_object* v___x_563_; 
v___x_562_ = lean_obj_once(&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5, &l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5_once, _init_l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__5);
v___x_563_ = lean_nat_to_int(v___x_562_);
return v___x_563_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg(lean_object* v_a_568_){
_start:
{
if (lean_obj_tag(v_a_568_) == 0)
{
lean_object* v___x_569_; 
v___x_569_ = ((lean_object*)(l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__1));
return v___x_569_;
}
else
{
lean_object* v___x_570_; lean_object* v___x_571_; lean_object* v___x_572_; lean_object* v___x_573_; lean_object* v___x_574_; lean_object* v___x_575_; lean_object* v___x_576_; lean_object* v___x_577_; uint8_t v___x_578_; lean_object* v___x_579_; 
v___x_570_ = ((lean_object*)(l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__3));
v___x_571_ = l_Std_Format_joinSep___at___00List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0_spec__0(v_a_568_, v___x_570_);
v___x_572_ = lean_obj_once(&l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6, &l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6_once, _init_l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__6);
v___x_573_ = ((lean_object*)(l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__7));
v___x_574_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_574_, 0, v___x_573_);
lean_ctor_set(v___x_574_, 1, v___x_571_);
v___x_575_ = ((lean_object*)(l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg___closed__8));
v___x_576_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_576_, 0, v___x_574_);
lean_ctor_set(v___x_576_, 1, v___x_575_);
v___x_577_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_577_, 0, v___x_572_);
lean_ctor_set(v___x_577_, 1, v___x_576_);
v___x_578_ = 0;
v___x_579_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_579_, 0, v___x_577_);
lean_ctor_set_uint8(v___x_579_, sizeof(void*)*1, v___x_578_);
return v___x_579_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___redArg(lean_object* v_x_592_){
_start:
{
lean_object* v_current__epoch_593_; lean_object* v_readers_594_; lean_object* v___x_596_; uint8_t v_isShared_597_; uint8_t v_isSharedCheck_628_; 
v_current__epoch_593_ = lean_ctor_get(v_x_592_, 0);
v_readers_594_ = lean_ctor_get(v_x_592_, 1);
v_isSharedCheck_628_ = !lean_is_exclusive(v_x_592_);
if (v_isSharedCheck_628_ == 0)
{
v___x_596_ = v_x_592_;
v_isShared_597_ = v_isSharedCheck_628_;
goto v_resetjp_595_;
}
else
{
lean_inc(v_readers_594_);
lean_inc(v_current__epoch_593_);
lean_dec(v_x_592_);
v___x_596_ = lean_box(0);
v_isShared_597_ = v_isSharedCheck_628_;
goto v_resetjp_595_;
}
v_resetjp_595_:
{
lean_object* v___x_598_; lean_object* v___x_599_; lean_object* v___x_600_; lean_object* v___x_601_; lean_object* v___x_602_; lean_object* v___x_604_; 
v___x_598_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_599_ = ((lean_object*)(l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__3));
v___x_600_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24);
v___x_601_ = l_Nat_reprFast(v_current__epoch_593_);
v___x_602_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_602_, 0, v___x_601_);
if (v_isShared_597_ == 0)
{
lean_ctor_set_tag(v___x_596_, 4);
lean_ctor_set(v___x_596_, 1, v___x_602_);
lean_ctor_set(v___x_596_, 0, v___x_600_);
v___x_604_ = v___x_596_;
goto v_reusejp_603_;
}
else
{
lean_object* v_reuseFailAlloc_627_; 
v_reuseFailAlloc_627_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_627_, 0, v___x_600_);
lean_ctor_set(v_reuseFailAlloc_627_, 1, v___x_602_);
v___x_604_ = v_reuseFailAlloc_627_;
goto v_reusejp_603_;
}
v_reusejp_603_:
{
uint8_t v___x_605_; lean_object* v___x_606_; lean_object* v___x_607_; lean_object* v___x_608_; lean_object* v___x_609_; lean_object* v___x_610_; lean_object* v___x_611_; lean_object* v___x_612_; lean_object* v___x_613_; lean_object* v___x_614_; lean_object* v___x_615_; lean_object* v___x_616_; lean_object* v___x_617_; lean_object* v___x_618_; lean_object* v___x_619_; lean_object* v___x_620_; lean_object* v___x_621_; lean_object* v___x_622_; lean_object* v___x_623_; lean_object* v___x_624_; lean_object* v___x_625_; lean_object* v___x_626_; 
v___x_605_ = 0;
v___x_606_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_606_, 0, v___x_604_);
lean_ctor_set_uint8(v___x_606_, sizeof(void*)*1, v___x_605_);
v___x_607_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_607_, 0, v___x_599_);
lean_ctor_set(v___x_607_, 1, v___x_606_);
v___x_608_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_609_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_609_, 0, v___x_607_);
lean_ctor_set(v___x_609_, 1, v___x_608_);
v___x_610_ = lean_box(1);
v___x_611_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_611_, 0, v___x_609_);
lean_ctor_set(v___x_611_, 1, v___x_610_);
v___x_612_ = ((lean_object*)(l_Polydim_V4_instReprRcuRingBuffer_repr___redArg___closed__5));
v___x_613_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_613_, 0, v___x_611_);
lean_ctor_set(v___x_613_, 1, v___x_612_);
v___x_614_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_614_, 0, v___x_613_);
lean_ctor_set(v___x_614_, 1, v___x_598_);
v___x_615_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12);
v___x_616_ = l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg(v_readers_594_);
v___x_617_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_617_, 0, v___x_615_);
lean_ctor_set(v___x_617_, 1, v___x_616_);
v___x_618_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_618_, 0, v___x_617_);
lean_ctor_set_uint8(v___x_618_, sizeof(void*)*1, v___x_605_);
v___x_619_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_619_, 0, v___x_614_);
lean_ctor_set(v___x_619_, 1, v___x_618_);
v___x_620_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_621_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_622_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_622_, 0, v___x_621_);
lean_ctor_set(v___x_622_, 1, v___x_619_);
v___x_623_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_624_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_624_, 0, v___x_622_);
lean_ctor_set(v___x_624_, 1, v___x_623_);
v___x_625_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_625_, 0, v___x_620_);
lean_ctor_set(v___x_625_, 1, v___x_624_);
v___x_626_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_626_, 0, v___x_625_);
lean_ctor_set_uint8(v___x_626_, sizeof(void*)*1, v___x_605_);
return v___x_626_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr(lean_object* v_x_629_, lean_object* v_prec_630_){
_start:
{
lean_object* v___x_631_; 
v___x_631_ = l_Polydim_V4_instReprRcuRingBuffer_repr___redArg(v_x_629_);
return v___x_631_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprRcuRingBuffer_repr___boxed(lean_object* v_x_632_, lean_object* v_prec_633_){
_start:
{
lean_object* v_res_634_; 
v_res_634_ = l_Polydim_V4_instReprRcuRingBuffer_repr(v_x_632_, v_prec_633_);
lean_dec(v_prec_633_);
return v_res_634_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0(lean_object* v_a_635_, lean_object* v_n_636_){
_start:
{
lean_object* v___x_637_; 
v___x_637_ = l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___redArg(v_a_635_);
return v___x_637_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0___boxed(lean_object* v_a_638_, lean_object* v_n_639_){
_start:
{
lean_object* v_res_640_; 
v_res_640_ = l_List_repr___at___00Polydim_V4_instReprRcuRingBuffer_repr_spec__0(v_a_638_, v_n_639_);
lean_dec(v_n_639_);
return v_res_640_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqWire128_decEq(lean_object* v_x_643_, lean_object* v_x_644_){
_start:
{
lean_object* v_high__64_645_; lean_object* v_low__64_646_; lean_object* v_high__64_647_; lean_object* v_low__64_648_; uint8_t v___x_649_; 
v_high__64_645_ = lean_ctor_get(v_x_643_, 0);
v_low__64_646_ = lean_ctor_get(v_x_643_, 1);
v_high__64_647_ = lean_ctor_get(v_x_644_, 0);
v_low__64_648_ = lean_ctor_get(v_x_644_, 1);
v___x_649_ = lean_nat_dec_eq(v_high__64_645_, v_high__64_647_);
if (v___x_649_ == 0)
{
return v___x_649_;
}
else
{
uint8_t v___x_650_; 
v___x_650_ = lean_nat_dec_eq(v_low__64_646_, v_low__64_648_);
return v___x_650_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqWire128_decEq___boxed(lean_object* v_x_651_, lean_object* v_x_652_){
_start:
{
uint8_t v_res_653_; lean_object* v_r_654_; 
v_res_653_ = l_Polydim_V4_instDecidableEqWire128_decEq(v_x_651_, v_x_652_);
lean_dec_ref(v_x_652_);
lean_dec_ref(v_x_651_);
v_r_654_ = lean_box(v_res_653_);
return v_r_654_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqWire128(lean_object* v_x_655_, lean_object* v_x_656_){
_start:
{
uint8_t v___x_657_; 
v___x_657_ = l_Polydim_V4_instDecidableEqWire128_decEq(v_x_655_, v_x_656_);
return v___x_657_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqWire128___boxed(lean_object* v_x_658_, lean_object* v_x_659_){
_start:
{
uint8_t v_res_660_; lean_object* v_r_661_; 
v_res_660_ = l_Polydim_V4_instDecidableEqWire128(v_x_658_, v_x_659_);
lean_dec_ref(v_x_659_);
lean_dec_ref(v_x_658_);
v_r_661_ = lean_box(v_res_660_);
return v_r_661_;
}
}
static lean_object* _init_l_Polydim_V4_instReprWire128_repr___redArg___closed__6(void){
_start:
{
lean_object* v___x_674_; lean_object* v___x_675_; 
v___x_674_ = lean_unsigned_to_nat(10u);
v___x_675_ = lean_nat_to_int(v___x_674_);
return v___x_675_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr___redArg(lean_object* v_x_676_){
_start:
{
lean_object* v_high__64_677_; lean_object* v_low__64_678_; lean_object* v___x_680_; uint8_t v_isShared_681_; uint8_t v_isSharedCheck_713_; 
v_high__64_677_ = lean_ctor_get(v_x_676_, 0);
v_low__64_678_ = lean_ctor_get(v_x_676_, 1);
v_isSharedCheck_713_ = !lean_is_exclusive(v_x_676_);
if (v_isSharedCheck_713_ == 0)
{
v___x_680_ = v_x_676_;
v_isShared_681_ = v_isSharedCheck_713_;
goto v_resetjp_679_;
}
else
{
lean_inc(v_low__64_678_);
lean_inc(v_high__64_677_);
lean_dec(v_x_676_);
v___x_680_ = lean_box(0);
v_isShared_681_ = v_isSharedCheck_713_;
goto v_resetjp_679_;
}
v_resetjp_679_:
{
lean_object* v___x_682_; lean_object* v___x_683_; lean_object* v___x_684_; lean_object* v___x_685_; lean_object* v___x_686_; lean_object* v___x_688_; 
v___x_682_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_683_ = ((lean_object*)(l_Polydim_V4_instReprWire128_repr___redArg___closed__3));
v___x_684_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__12);
v___x_685_ = l_Nat_reprFast(v_high__64_677_);
v___x_686_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_686_, 0, v___x_685_);
if (v_isShared_681_ == 0)
{
lean_ctor_set_tag(v___x_680_, 4);
lean_ctor_set(v___x_680_, 1, v___x_686_);
lean_ctor_set(v___x_680_, 0, v___x_684_);
v___x_688_ = v___x_680_;
goto v_reusejp_687_;
}
else
{
lean_object* v_reuseFailAlloc_712_; 
v_reuseFailAlloc_712_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_712_, 0, v___x_684_);
lean_ctor_set(v_reuseFailAlloc_712_, 1, v___x_686_);
v___x_688_ = v_reuseFailAlloc_712_;
goto v_reusejp_687_;
}
v_reusejp_687_:
{
uint8_t v___x_689_; lean_object* v___x_690_; lean_object* v___x_691_; lean_object* v___x_692_; lean_object* v___x_693_; lean_object* v___x_694_; lean_object* v___x_695_; lean_object* v___x_696_; lean_object* v___x_697_; lean_object* v___x_698_; lean_object* v___x_699_; lean_object* v___x_700_; lean_object* v___x_701_; lean_object* v___x_702_; lean_object* v___x_703_; lean_object* v___x_704_; lean_object* v___x_705_; lean_object* v___x_706_; lean_object* v___x_707_; lean_object* v___x_708_; lean_object* v___x_709_; lean_object* v___x_710_; lean_object* v___x_711_; 
v___x_689_ = 0;
v___x_690_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_690_, 0, v___x_688_);
lean_ctor_set_uint8(v___x_690_, sizeof(void*)*1, v___x_689_);
v___x_691_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_691_, 0, v___x_683_);
lean_ctor_set(v___x_691_, 1, v___x_690_);
v___x_692_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_693_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_693_, 0, v___x_691_);
lean_ctor_set(v___x_693_, 1, v___x_692_);
v___x_694_ = lean_box(1);
v___x_695_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_695_, 0, v___x_693_);
lean_ctor_set(v___x_695_, 1, v___x_694_);
v___x_696_ = ((lean_object*)(l_Polydim_V4_instReprWire128_repr___redArg___closed__5));
v___x_697_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_697_, 0, v___x_695_);
lean_ctor_set(v___x_697_, 1, v___x_696_);
v___x_698_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_698_, 0, v___x_697_);
lean_ctor_set(v___x_698_, 1, v___x_682_);
v___x_699_ = lean_obj_once(&l_Polydim_V4_instReprWire128_repr___redArg___closed__6, &l_Polydim_V4_instReprWire128_repr___redArg___closed__6_once, _init_l_Polydim_V4_instReprWire128_repr___redArg___closed__6);
v___x_700_ = l_Nat_reprFast(v_low__64_678_);
v___x_701_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_701_, 0, v___x_700_);
v___x_702_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_702_, 0, v___x_699_);
lean_ctor_set(v___x_702_, 1, v___x_701_);
v___x_703_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_703_, 0, v___x_702_);
lean_ctor_set_uint8(v___x_703_, sizeof(void*)*1, v___x_689_);
v___x_704_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_704_, 0, v___x_698_);
lean_ctor_set(v___x_704_, 1, v___x_703_);
v___x_705_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_706_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_707_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_707_, 0, v___x_706_);
lean_ctor_set(v___x_707_, 1, v___x_704_);
v___x_708_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_709_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_709_, 0, v___x_707_);
lean_ctor_set(v___x_709_, 1, v___x_708_);
v___x_710_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_710_, 0, v___x_705_);
lean_ctor_set(v___x_710_, 1, v___x_709_);
v___x_711_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_711_, 0, v___x_710_);
lean_ctor_set_uint8(v___x_711_, sizeof(void*)*1, v___x_689_);
return v___x_711_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr(lean_object* v_x_714_, lean_object* v_prec_715_){
_start:
{
lean_object* v___x_716_; 
v___x_716_ = l_Polydim_V4_instReprWire128_repr___redArg(v_x_714_);
return v___x_716_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprWire128_repr___boxed(lean_object* v_x_717_, lean_object* v_prec_718_){
_start:
{
lean_object* v_res_719_; 
v_res_719_ = l_Polydim_V4_instReprWire128_repr(v_x_717_, v_prec_718_);
lean_dec(v_prec_718_);
return v_res_719_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqTensorDescriptor_decEq(lean_object* v_x_722_, lean_object* v_x_723_){
_start:
{
lean_object* v_epoch_724_; lean_object* v_domain__id_725_; lean_object* v_buffer__addr_726_; lean_object* v_byte__size_727_; lean_object* v_epoch_728_; lean_object* v_domain__id_729_; lean_object* v_buffer__addr_730_; lean_object* v_byte__size_731_; uint8_t v___x_732_; 
v_epoch_724_ = lean_ctor_get(v_x_722_, 0);
v_domain__id_725_ = lean_ctor_get(v_x_722_, 1);
v_buffer__addr_726_ = lean_ctor_get(v_x_722_, 2);
v_byte__size_727_ = lean_ctor_get(v_x_722_, 3);
v_epoch_728_ = lean_ctor_get(v_x_723_, 0);
v_domain__id_729_ = lean_ctor_get(v_x_723_, 1);
v_buffer__addr_730_ = lean_ctor_get(v_x_723_, 2);
v_byte__size_731_ = lean_ctor_get(v_x_723_, 3);
v___x_732_ = lean_nat_dec_eq(v_epoch_724_, v_epoch_728_);
if (v___x_732_ == 0)
{
return v___x_732_;
}
else
{
uint8_t v___x_733_; 
v___x_733_ = lean_nat_dec_eq(v_domain__id_725_, v_domain__id_729_);
if (v___x_733_ == 0)
{
return v___x_733_;
}
else
{
uint8_t v___x_734_; 
v___x_734_ = lean_nat_dec_eq(v_buffer__addr_726_, v_buffer__addr_730_);
if (v___x_734_ == 0)
{
return v___x_734_;
}
else
{
uint8_t v___x_735_; 
v___x_735_ = lean_nat_dec_eq(v_byte__size_727_, v_byte__size_731_);
return v___x_735_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqTensorDescriptor_decEq___boxed(lean_object* v_x_736_, lean_object* v_x_737_){
_start:
{
uint8_t v_res_738_; lean_object* v_r_739_; 
v_res_738_ = l_Polydim_V4_instDecidableEqTensorDescriptor_decEq(v_x_736_, v_x_737_);
lean_dec_ref(v_x_737_);
lean_dec_ref(v_x_736_);
v_r_739_ = lean_box(v_res_738_);
return v_r_739_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqTensorDescriptor(lean_object* v_x_740_, lean_object* v_x_741_){
_start:
{
uint8_t v___x_742_; 
v___x_742_ = l_Polydim_V4_instDecidableEqTensorDescriptor_decEq(v_x_740_, v_x_741_);
return v___x_742_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqTensorDescriptor___boxed(lean_object* v_x_743_, lean_object* v_x_744_){
_start:
{
uint8_t v_res_745_; lean_object* v_r_746_; 
v_res_745_ = l_Polydim_V4_instDecidableEqTensorDescriptor(v_x_743_, v_x_744_);
lean_dec_ref(v_x_744_);
lean_dec_ref(v_x_743_);
v_r_746_ = lean_box(v_res_745_);
return v_r_746_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___redArg(lean_object* v_x_756_){
_start:
{
lean_object* v_epoch_757_; lean_object* v_domain__id_758_; lean_object* v_buffer__addr_759_; lean_object* v_byte__size_760_; lean_object* v___x_761_; lean_object* v___x_762_; lean_object* v___x_763_; lean_object* v___x_764_; lean_object* v___x_765_; lean_object* v___x_766_; uint8_t v___x_767_; lean_object* v___x_768_; lean_object* v___x_769_; lean_object* v___x_770_; lean_object* v___x_771_; lean_object* v___x_772_; lean_object* v___x_773_; lean_object* v___x_774_; lean_object* v___x_775_; lean_object* v___x_776_; lean_object* v___x_777_; lean_object* v___x_778_; lean_object* v___x_779_; lean_object* v___x_780_; lean_object* v___x_781_; lean_object* v___x_782_; lean_object* v___x_783_; lean_object* v___x_784_; lean_object* v___x_785_; lean_object* v___x_786_; lean_object* v___x_787_; lean_object* v___x_788_; lean_object* v___x_789_; lean_object* v___x_790_; lean_object* v___x_791_; lean_object* v___x_792_; lean_object* v___x_793_; lean_object* v___x_794_; lean_object* v___x_795_; lean_object* v___x_796_; lean_object* v___x_797_; lean_object* v___x_798_; lean_object* v___x_799_; lean_object* v___x_800_; lean_object* v___x_801_; lean_object* v___x_802_; lean_object* v___x_803_; lean_object* v___x_804_; lean_object* v___x_805_; lean_object* v___x_806_; lean_object* v___x_807_; lean_object* v___x_808_; lean_object* v___x_809_; lean_object* v___x_810_; 
v_epoch_757_ = lean_ctor_get(v_x_756_, 0);
lean_inc(v_epoch_757_);
v_domain__id_758_ = lean_ctor_get(v_x_756_, 1);
lean_inc(v_domain__id_758_);
v_buffer__addr_759_ = lean_ctor_get(v_x_756_, 2);
lean_inc(v_buffer__addr_759_);
v_byte__size_760_ = lean_ctor_get(v_x_756_, 3);
lean_inc(v_byte__size_760_);
lean_dec_ref(v_x_756_);
v___x_761_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_762_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__6));
v___x_763_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__7);
v___x_764_ = l_Nat_reprFast(v_epoch_757_);
v___x_765_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_765_, 0, v___x_764_);
v___x_766_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_766_, 0, v___x_763_);
lean_ctor_set(v___x_766_, 1, v___x_765_);
v___x_767_ = 0;
v___x_768_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_768_, 0, v___x_766_);
lean_ctor_set_uint8(v___x_768_, sizeof(void*)*1, v___x_767_);
v___x_769_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_769_, 0, v___x_762_);
lean_ctor_set(v___x_769_, 1, v___x_768_);
v___x_770_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_771_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_771_, 0, v___x_769_);
lean_ctor_set(v___x_771_, 1, v___x_770_);
v___x_772_ = lean_box(1);
v___x_773_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_773_, 0, v___x_771_);
lean_ctor_set(v___x_773_, 1, v___x_772_);
v___x_774_ = ((lean_object*)(l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__1));
v___x_775_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_775_, 0, v___x_773_);
lean_ctor_set(v___x_775_, 1, v___x_774_);
v___x_776_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_776_, 0, v___x_775_);
lean_ctor_set(v___x_776_, 1, v___x_761_);
v___x_777_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15);
v___x_778_ = l_Nat_reprFast(v_domain__id_758_);
v___x_779_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_779_, 0, v___x_778_);
v___x_780_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_780_, 0, v___x_777_);
lean_ctor_set(v___x_780_, 1, v___x_779_);
v___x_781_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_781_, 0, v___x_780_);
lean_ctor_set_uint8(v___x_781_, sizeof(void*)*1, v___x_767_);
v___x_782_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_782_, 0, v___x_776_);
lean_ctor_set(v___x_782_, 1, v___x_781_);
v___x_783_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_783_, 0, v___x_782_);
lean_ctor_set(v___x_783_, 1, v___x_770_);
v___x_784_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_784_, 0, v___x_783_);
lean_ctor_set(v___x_784_, 1, v___x_772_);
v___x_785_ = ((lean_object*)(l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__3));
v___x_786_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_786_, 0, v___x_784_);
lean_ctor_set(v___x_786_, 1, v___x_785_);
v___x_787_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_787_, 0, v___x_786_);
lean_ctor_set(v___x_787_, 1, v___x_761_);
v___x_788_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__18);
v___x_789_ = l_Nat_reprFast(v_buffer__addr_759_);
v___x_790_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_790_, 0, v___x_789_);
v___x_791_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_791_, 0, v___x_788_);
lean_ctor_set(v___x_791_, 1, v___x_790_);
v___x_792_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_792_, 0, v___x_791_);
lean_ctor_set_uint8(v___x_792_, sizeof(void*)*1, v___x_767_);
v___x_793_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_793_, 0, v___x_787_);
lean_ctor_set(v___x_793_, 1, v___x_792_);
v___x_794_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_794_, 0, v___x_793_);
lean_ctor_set(v___x_794_, 1, v___x_770_);
v___x_795_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_795_, 0, v___x_794_);
lean_ctor_set(v___x_795_, 1, v___x_772_);
v___x_796_ = ((lean_object*)(l_Polydim_V4_instReprTensorDescriptor_repr___redArg___closed__5));
v___x_797_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_797_, 0, v___x_795_);
lean_ctor_set(v___x_797_, 1, v___x_796_);
v___x_798_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_798_, 0, v___x_797_);
lean_ctor_set(v___x_798_, 1, v___x_761_);
v___x_799_ = l_Nat_reprFast(v_byte__size_760_);
v___x_800_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_800_, 0, v___x_799_);
v___x_801_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_801_, 0, v___x_777_);
lean_ctor_set(v___x_801_, 1, v___x_800_);
v___x_802_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_802_, 0, v___x_801_);
lean_ctor_set_uint8(v___x_802_, sizeof(void*)*1, v___x_767_);
v___x_803_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_803_, 0, v___x_798_);
lean_ctor_set(v___x_803_, 1, v___x_802_);
v___x_804_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_805_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_806_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_806_, 0, v___x_805_);
lean_ctor_set(v___x_806_, 1, v___x_803_);
v___x_807_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_808_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_808_, 0, v___x_806_);
lean_ctor_set(v___x_808_, 1, v___x_807_);
v___x_809_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_809_, 0, v___x_804_);
lean_ctor_set(v___x_809_, 1, v___x_808_);
v___x_810_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_810_, 0, v___x_809_);
lean_ctor_set_uint8(v___x_810_, sizeof(void*)*1, v___x_767_);
return v___x_810_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr(lean_object* v_x_811_, lean_object* v_prec_812_){
_start:
{
lean_object* v___x_813_; 
v___x_813_ = l_Polydim_V4_instReprTensorDescriptor_repr___redArg(v_x_811_);
return v___x_813_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprTensorDescriptor_repr___boxed(lean_object* v_x_814_, lean_object* v_prec_815_){
_start:
{
lean_object* v_res_816_; 
v_res_816_ = l_Polydim_V4_instReprTensorDescriptor_repr(v_x_814_, v_prec_815_);
lean_dec(v_prec_815_);
return v_res_816_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq(lean_object* v_x_819_, lean_object* v_x_820_){
_start:
{
lean_object* v_rank__K_821_; lean_object* v_ambient__D_822_; lean_object* v_rank__K_823_; lean_object* v_ambient__D_824_; uint8_t v___x_825_; 
v_rank__K_821_ = lean_ctor_get(v_x_819_, 0);
v_ambient__D_822_ = lean_ctor_get(v_x_819_, 1);
v_rank__K_823_ = lean_ctor_get(v_x_820_, 0);
v_ambient__D_824_ = lean_ctor_get(v_x_820_, 1);
v___x_825_ = lean_nat_dec_eq(v_rank__K_821_, v_rank__K_823_);
if (v___x_825_ == 0)
{
return v___x_825_;
}
else
{
uint8_t v___x_826_; 
v___x_826_ = lean_nat_dec_eq(v_ambient__D_822_, v_ambient__D_824_);
return v___x_826_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq___boxed(lean_object* v_x_827_, lean_object* v_x_828_){
_start:
{
uint8_t v_res_829_; lean_object* v_r_830_; 
v_res_829_ = l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq(v_x_827_, v_x_828_);
lean_dec_ref(v_x_828_);
lean_dec_ref(v_x_827_);
v_r_830_ = lean_box(v_res_829_);
return v_r_830_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqGrassmannProjectorCert(lean_object* v_x_831_, lean_object* v_x_832_){
_start:
{
uint8_t v___x_833_; 
v___x_833_ = l_Polydim_V4_instDecidableEqGrassmannProjectorCert_decEq(v_x_831_, v_x_832_);
return v___x_833_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqGrassmannProjectorCert___boxed(lean_object* v_x_834_, lean_object* v_x_835_){
_start:
{
uint8_t v_res_836_; lean_object* v_r_837_; 
v_res_836_ = l_Polydim_V4_instDecidableEqGrassmannProjectorCert(v_x_834_, v_x_835_);
lean_dec_ref(v_x_835_);
lean_dec_ref(v_x_834_);
v_r_837_ = lean_box(v_res_836_);
return v_r_837_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg(lean_object* v_x_859_){
_start:
{
lean_object* v_rank__K_860_; lean_object* v_ambient__D_861_; lean_object* v___x_863_; uint8_t v_isShared_864_; uint8_t v_isSharedCheck_909_; 
v_rank__K_860_ = lean_ctor_get(v_x_859_, 0);
v_ambient__D_861_ = lean_ctor_get(v_x_859_, 1);
v_isSharedCheck_909_ = !lean_is_exclusive(v_x_859_);
if (v_isSharedCheck_909_ == 0)
{
v___x_863_ = v_x_859_;
v_isShared_864_ = v_isSharedCheck_909_;
goto v_resetjp_862_;
}
else
{
lean_inc(v_ambient__D_861_);
lean_inc(v_rank__K_860_);
lean_dec(v_x_859_);
v___x_863_ = lean_box(0);
v_isShared_864_ = v_isSharedCheck_909_;
goto v_resetjp_862_;
}
v_resetjp_862_:
{
lean_object* v___x_865_; lean_object* v___x_866_; lean_object* v___x_867_; lean_object* v___x_868_; lean_object* v___x_869_; lean_object* v___x_871_; 
v___x_865_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_866_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__3));
v___x_867_ = lean_obj_once(&l_Polydim_V4_instReprWire128_repr___redArg___closed__6, &l_Polydim_V4_instReprWire128_repr___redArg___closed__6_once, _init_l_Polydim_V4_instReprWire128_repr___redArg___closed__6);
v___x_868_ = l_Nat_reprFast(v_rank__K_860_);
v___x_869_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_869_, 0, v___x_868_);
if (v_isShared_864_ == 0)
{
lean_ctor_set_tag(v___x_863_, 4);
lean_ctor_set(v___x_863_, 1, v___x_869_);
lean_ctor_set(v___x_863_, 0, v___x_867_);
v___x_871_ = v___x_863_;
goto v_reusejp_870_;
}
else
{
lean_object* v_reuseFailAlloc_908_; 
v_reuseFailAlloc_908_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_908_, 0, v___x_867_);
lean_ctor_set(v_reuseFailAlloc_908_, 1, v___x_869_);
v___x_871_ = v_reuseFailAlloc_908_;
goto v_reusejp_870_;
}
v_reusejp_870_:
{
uint8_t v___x_872_; lean_object* v___x_873_; lean_object* v___x_874_; lean_object* v___x_875_; lean_object* v___x_876_; lean_object* v___x_877_; lean_object* v___x_878_; lean_object* v___x_879_; lean_object* v___x_880_; lean_object* v___x_881_; lean_object* v___x_882_; lean_object* v___x_883_; lean_object* v___x_884_; lean_object* v___x_885_; lean_object* v___x_886_; lean_object* v___x_887_; lean_object* v___x_888_; lean_object* v___x_889_; lean_object* v___x_890_; lean_object* v___x_891_; lean_object* v___x_892_; lean_object* v___x_893_; lean_object* v___x_894_; lean_object* v___x_895_; lean_object* v___x_896_; lean_object* v___x_897_; lean_object* v___x_898_; lean_object* v___x_899_; lean_object* v___x_900_; lean_object* v___x_901_; lean_object* v___x_902_; lean_object* v___x_903_; lean_object* v___x_904_; lean_object* v___x_905_; lean_object* v___x_906_; lean_object* v___x_907_; 
v___x_872_ = 0;
v___x_873_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_873_, 0, v___x_871_);
lean_ctor_set_uint8(v___x_873_, sizeof(void*)*1, v___x_872_);
v___x_874_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_874_, 0, v___x_866_);
lean_ctor_set(v___x_874_, 1, v___x_873_);
v___x_875_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_876_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_876_, 0, v___x_874_);
lean_ctor_set(v___x_876_, 1, v___x_875_);
v___x_877_ = lean_box(1);
v___x_878_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_878_, 0, v___x_876_);
lean_ctor_set(v___x_878_, 1, v___x_877_);
v___x_879_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__5));
v___x_880_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_880_, 0, v___x_878_);
lean_ctor_set(v___x_880_, 1, v___x_879_);
v___x_881_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_881_, 0, v___x_880_);
lean_ctor_set(v___x_881_, 1, v___x_865_);
v___x_882_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15);
v___x_883_ = l_Nat_reprFast(v_ambient__D_861_);
v___x_884_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_884_, 0, v___x_883_);
v___x_885_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_885_, 0, v___x_882_);
lean_ctor_set(v___x_885_, 1, v___x_884_);
v___x_886_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_886_, 0, v___x_885_);
lean_ctor_set_uint8(v___x_886_, sizeof(void*)*1, v___x_872_);
v___x_887_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_887_, 0, v___x_881_);
lean_ctor_set(v___x_887_, 1, v___x_886_);
v___x_888_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_888_, 0, v___x_887_);
lean_ctor_set(v___x_888_, 1, v___x_875_);
v___x_889_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_889_, 0, v___x_888_);
lean_ctor_set(v___x_889_, 1, v___x_877_);
v___x_890_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__7));
v___x_891_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_891_, 0, v___x_889_);
lean_ctor_set(v___x_891_, 1, v___x_890_);
v___x_892_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_892_, 0, v___x_891_);
lean_ctor_set(v___x_892_, 1, v___x_865_);
v___x_893_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9));
v___x_894_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_894_, 0, v___x_892_);
lean_ctor_set(v___x_894_, 1, v___x_893_);
v___x_895_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_895_, 0, v___x_894_);
lean_ctor_set(v___x_895_, 1, v___x_875_);
v___x_896_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_896_, 0, v___x_895_);
lean_ctor_set(v___x_896_, 1, v___x_877_);
v___x_897_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__11));
v___x_898_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_898_, 0, v___x_896_);
lean_ctor_set(v___x_898_, 1, v___x_897_);
v___x_899_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_899_, 0, v___x_898_);
lean_ctor_set(v___x_899_, 1, v___x_865_);
v___x_900_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_900_, 0, v___x_899_);
lean_ctor_set(v___x_900_, 1, v___x_893_);
v___x_901_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_902_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_903_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_903_, 0, v___x_902_);
lean_ctor_set(v___x_903_, 1, v___x_900_);
v___x_904_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_905_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_905_, 0, v___x_903_);
lean_ctor_set(v___x_905_, 1, v___x_904_);
v___x_906_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_906_, 0, v___x_901_);
lean_ctor_set(v___x_906_, 1, v___x_905_);
v___x_907_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_907_, 0, v___x_906_);
lean_ctor_set_uint8(v___x_907_, sizeof(void*)*1, v___x_872_);
return v___x_907_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr(lean_object* v_x_910_, lean_object* v_prec_911_){
_start:
{
lean_object* v___x_912_; 
v___x_912_ = l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg(v_x_910_);
return v___x_912_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannProjectorCert_repr___boxed(lean_object* v_x_913_, lean_object* v_prec_914_){
_start:
{
lean_object* v_res_915_; 
v_res_915_ = l_Polydim_V4_instReprGrassmannProjectorCert_repr(v_x_913_, v_prec_914_);
lean_dec(v_prec_914_);
return v_res_915_;
}
}
static lean_object* _init_l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_927_; lean_object* v___x_928_; 
v___x_927_ = lean_unsigned_to_nat(22u);
v___x_928_ = lean_nat_to_int(v___x_927_);
return v___x_928_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___redArg(lean_object* v_x_935_){
_start:
{
lean_object* v___x_936_; lean_object* v___x_937_; lean_object* v___x_938_; lean_object* v___x_939_; lean_object* v___x_940_; lean_object* v___x_941_; uint8_t v___x_942_; lean_object* v___x_943_; lean_object* v___x_944_; lean_object* v___x_945_; lean_object* v___x_946_; lean_object* v___x_947_; lean_object* v___x_948_; lean_object* v___x_949_; lean_object* v___x_950_; lean_object* v___x_951_; lean_object* v___x_952_; lean_object* v___x_953_; lean_object* v___x_954_; lean_object* v___x_955_; lean_object* v___x_956_; lean_object* v___x_957_; lean_object* v___x_958_; lean_object* v___x_959_; lean_object* v___x_960_; lean_object* v___x_961_; lean_object* v___x_962_; lean_object* v___x_963_; lean_object* v___x_964_; lean_object* v___x_965_; lean_object* v___x_966_; 
v___x_936_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_937_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__3));
v___x_938_ = lean_obj_once(&l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4, &l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4_once, _init_l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__4);
v___x_939_ = l_Nat_reprFast(v_x_935_);
v___x_940_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_940_, 0, v___x_939_);
v___x_941_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_941_, 0, v___x_938_);
lean_ctor_set(v___x_941_, 1, v___x_940_);
v___x_942_ = 0;
v___x_943_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_943_, 0, v___x_941_);
lean_ctor_set_uint8(v___x_943_, sizeof(void*)*1, v___x_942_);
v___x_944_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_944_, 0, v___x_937_);
lean_ctor_set(v___x_944_, 1, v___x_943_);
v___x_945_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_946_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_946_, 0, v___x_944_);
lean_ctor_set(v___x_946_, 1, v___x_945_);
v___x_947_ = lean_box(1);
v___x_948_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_948_, 0, v___x_946_);
lean_ctor_set(v___x_948_, 1, v___x_947_);
v___x_949_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__6));
v___x_950_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_950_, 0, v___x_948_);
lean_ctor_set(v___x_950_, 1, v___x_949_);
v___x_951_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_951_, 0, v___x_950_);
lean_ctor_set(v___x_951_, 1, v___x_936_);
v___x_952_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9));
v___x_953_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_953_, 0, v___x_951_);
lean_ctor_set(v___x_953_, 1, v___x_952_);
v___x_954_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_954_, 0, v___x_953_);
lean_ctor_set(v___x_954_, 1, v___x_945_);
v___x_955_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_955_, 0, v___x_954_);
lean_ctor_set(v___x_955_, 1, v___x_947_);
v___x_956_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannPairCert_repr___redArg___closed__8));
v___x_957_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_957_, 0, v___x_955_);
lean_ctor_set(v___x_957_, 1, v___x_956_);
v___x_958_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_958_, 0, v___x_957_);
lean_ctor_set(v___x_958_, 1, v___x_936_);
v___x_959_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_959_, 0, v___x_958_);
lean_ctor_set(v___x_959_, 1, v___x_952_);
v___x_960_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_961_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_962_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_962_, 0, v___x_961_);
lean_ctor_set(v___x_962_, 1, v___x_959_);
v___x_963_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_964_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_964_, 0, v___x_962_);
lean_ctor_set(v___x_964_, 1, v___x_963_);
v___x_965_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_965_, 0, v___x_960_);
lean_ctor_set(v___x_965_, 1, v___x_964_);
v___x_966_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_966_, 0, v___x_965_);
lean_ctor_set_uint8(v___x_966_, sizeof(void*)*1, v___x_942_);
return v___x_966_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr(lean_object* v_px_967_, lean_object* v_py_968_, lean_object* v_x_969_, lean_object* v_prec_970_){
_start:
{
lean_object* v___x_971_; 
v___x_971_ = l_Polydim_V4_instReprGrassmannPairCert_repr___redArg(v_x_969_);
return v___x_971_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert_repr___boxed(lean_object* v_px_972_, lean_object* v_py_973_, lean_object* v_x_974_, lean_object* v_prec_975_){
_start:
{
lean_object* v_res_976_; 
v_res_976_ = l_Polydim_V4_instReprGrassmannPairCert_repr(v_px_972_, v_py_973_, v_x_974_, v_prec_975_);
lean_dec(v_prec_975_);
lean_dec_ref(v_py_973_);
lean_dec_ref(v_px_972_);
return v_res_976_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprGrassmannPairCert(lean_object* v_px_977_, lean_object* v_py_978_){
_start:
{
lean_object* v___x_979_; 
v___x_979_ = lean_alloc_closure((void*)(l_Polydim_V4_instReprGrassmannPairCert_repr___boxed), 4, 2);
lean_closure_set(v___x_979_, 0, v_px_977_);
lean_closure_set(v___x_979_, 1, v_py_978_);
return v___x_979_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___redArg(lean_object* v_px_980_, lean_object* v_pair_981_){
_start:
{
lean_object* v_rank__K_982_; lean_object* v___x_983_; 
v_rank__K_982_ = lean_ctor_get(v_px_980_, 0);
v___x_983_ = lean_nat_sub(v_rank__K_982_, v_pair_981_);
return v___x_983_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___redArg___boxed(lean_object* v_px_984_, lean_object* v_pair_985_){
_start:
{
lean_object* v_res_986_; 
v_res_986_ = l_Polydim_V4_grassmann__chordal__sq___redArg(v_px_984_, v_pair_985_);
lean_dec(v_pair_985_);
lean_dec_ref(v_px_984_);
return v_res_986_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq(lean_object* v_px_987_, lean_object* v_py_988_, lean_object* v_pair_989_){
_start:
{
lean_object* v___x_990_; 
v___x_990_ = l_Polydim_V4_grassmann__chordal__sq___redArg(v_px_987_, v_pair_989_);
return v___x_990_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_grassmann__chordal__sq___boxed(lean_object* v_px_991_, lean_object* v_py_992_, lean_object* v_pair_993_){
_start:
{
lean_object* v_res_994_; 
v_res_994_ = l_Polydim_V4_grassmann__chordal__sq(v_px_991_, v_py_992_, v_pair_993_);
lean_dec(v_pair_993_);
lean_dec_ref(v_py_992_);
lean_dec_ref(v_px_991_);
return v_res_994_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorIdx(uint8_t v_x_995_){
_start:
{
if (v_x_995_ == 0)
{
lean_object* v___x_996_; 
v___x_996_ = lean_unsigned_to_nat(0u);
return v___x_996_;
}
else
{
lean_object* v___x_997_; 
v___x_997_ = lean_unsigned_to_nat(1u);
return v___x_997_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorIdx___boxed(lean_object* v_x_998_){
_start:
{
uint8_t v_x_boxed_999_; lean_object* v_res_1000_; 
v_x_boxed_999_ = lean_unbox(v_x_998_);
v_res_1000_ = l_Polydim_V4_CayleySpectralDecomp_ctorIdx(v_x_boxed_999_);
return v_res_1000_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___redArg(lean_object* v_k_1001_){
_start:
{
lean_inc(v_k_1001_);
return v_k_1001_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___redArg___boxed(lean_object* v_k_1002_){
_start:
{
lean_object* v_res_1003_; 
v_res_1003_ = l_Polydim_V4_CayleySpectralDecomp_ctorElim___redArg(v_k_1002_);
lean_dec(v_k_1002_);
return v_res_1003_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim(lean_object* v_motive_1004_, lean_object* v_ctorIdx_1005_, uint8_t v_t_1006_, lean_object* v_h_1007_, lean_object* v_k_1008_){
_start:
{
lean_inc(v_k_1008_);
return v_k_1008_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ctorElim___boxed(lean_object* v_motive_1009_, lean_object* v_ctorIdx_1010_, lean_object* v_t_1011_, lean_object* v_h_1012_, lean_object* v_k_1013_){
_start:
{
uint8_t v_t_boxed_1014_; lean_object* v_res_1015_; 
v_t_boxed_1014_ = lean_unbox(v_t_1011_);
v_res_1015_ = l_Polydim_V4_CayleySpectralDecomp_ctorElim(v_motive_1009_, v_ctorIdx_1010_, v_t_boxed_1014_, v_h_1012_, v_k_1013_);
lean_dec(v_k_1013_);
lean_dec(v_ctorIdx_1010_);
return v_res_1015_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___redArg(lean_object* v_in__kernel_1016_){
_start:
{
lean_inc(v_in__kernel_1016_);
return v_in__kernel_1016_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___redArg___boxed(lean_object* v_in__kernel_1017_){
_start:
{
lean_object* v_res_1018_; 
v_res_1018_ = l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___redArg(v_in__kernel_1017_);
lean_dec(v_in__kernel_1017_);
return v_res_1018_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim(lean_object* v_motive_1019_, uint8_t v_t_1020_, lean_object* v_h_1021_, lean_object* v_in__kernel_1022_){
_start:
{
lean_inc(v_in__kernel_1022_);
return v_in__kernel_1022_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim___boxed(lean_object* v_motive_1023_, lean_object* v_t_1024_, lean_object* v_h_1025_, lean_object* v_in__kernel_1026_){
_start:
{
uint8_t v_t_boxed_1027_; lean_object* v_res_1028_; 
v_t_boxed_1027_ = lean_unbox(v_t_1024_);
v_res_1028_ = l_Polydim_V4_CayleySpectralDecomp_in__kernel_elim(v_motive_1023_, v_t_boxed_1027_, v_h_1025_, v_in__kernel_1026_);
lean_dec(v_in__kernel_1026_);
return v_res_1028_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___redArg(lean_object* v_in__range_1029_){
_start:
{
lean_inc(v_in__range_1029_);
return v_in__range_1029_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___redArg___boxed(lean_object* v_in__range_1030_){
_start:
{
lean_object* v_res_1031_; 
v_res_1031_ = l_Polydim_V4_CayleySpectralDecomp_in__range_elim___redArg(v_in__range_1030_);
lean_dec(v_in__range_1030_);
return v_res_1031_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim(lean_object* v_motive_1032_, uint8_t v_t_1033_, lean_object* v_h_1034_, lean_object* v_in__range_1035_){
_start:
{
lean_inc(v_in__range_1035_);
return v_in__range_1035_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_in__range_elim___boxed(lean_object* v_motive_1036_, lean_object* v_t_1037_, lean_object* v_h_1038_, lean_object* v_in__range_1039_){
_start:
{
uint8_t v_t_boxed_1040_; lean_object* v_res_1041_; 
v_t_boxed_1040_ = lean_unbox(v_t_1037_);
v_res_1041_ = l_Polydim_V4_CayleySpectralDecomp_in__range_elim(v_motive_1036_, v_t_boxed_1040_, v_h_1038_, v_in__range_1039_);
lean_dec(v_in__range_1039_);
return v_res_1041_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_CayleySpectralDecomp_ofNat(lean_object* v_n_1042_){
_start:
{
lean_object* v___x_1043_; uint8_t v___x_1044_; 
v___x_1043_ = lean_unsigned_to_nat(0u);
v___x_1044_ = lean_nat_dec_le(v_n_1042_, v___x_1043_);
if (v___x_1044_ == 0)
{
uint8_t v___x_1045_; 
v___x_1045_ = 1;
return v___x_1045_;
}
else
{
uint8_t v___x_1046_; 
v___x_1046_ = 0;
return v___x_1046_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_CayleySpectralDecomp_ofNat___boxed(lean_object* v_n_1047_){
_start:
{
uint8_t v_res_1048_; lean_object* v_r_1049_; 
v_res_1048_ = l_Polydim_V4_CayleySpectralDecomp_ofNat(v_n_1047_);
lean_dec(v_n_1047_);
v_r_1049_ = lean_box(v_res_1048_);
return v_r_1049_;
}
}
LEAN_EXPORT uint8_t l_Polydim_V4_instDecidableEqCayleySpectralDecomp(uint8_t v_x_1050_, uint8_t v_y_1051_){
_start:
{
lean_object* v___x_1052_; lean_object* v___x_1053_; uint8_t v___x_1054_; 
v___x_1052_ = l_Polydim_V4_CayleySpectralDecomp_ctorIdx(v_x_1050_);
v___x_1053_ = l_Polydim_V4_CayleySpectralDecomp_ctorIdx(v_y_1051_);
v___x_1054_ = lean_nat_dec_eq(v___x_1052_, v___x_1053_);
lean_dec(v___x_1053_);
lean_dec(v___x_1052_);
return v___x_1054_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instDecidableEqCayleySpectralDecomp___boxed(lean_object* v_x_1055_, lean_object* v_y_1056_){
_start:
{
uint8_t v_x_13__boxed_1057_; uint8_t v_y_14__boxed_1058_; uint8_t v_res_1059_; lean_object* v_r_1060_; 
v_x_13__boxed_1057_ = lean_unbox(v_x_1055_);
v_y_14__boxed_1058_ = lean_unbox(v_y_1056_);
v_res_1059_ = l_Polydim_V4_instDecidableEqCayleySpectralDecomp(v_x_13__boxed_1057_, v_y_14__boxed_1058_);
v_r_1060_ = lean_box(v_res_1059_);
return v_r_1060_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr(uint8_t v_x_1067_, lean_object* v_prec_1068_){
_start:
{
lean_object* v___y_1070_; lean_object* v___y_1077_; 
if (v_x_1067_ == 0)
{
lean_object* v___x_1083_; uint8_t v___x_1084_; 
v___x_1083_ = lean_unsigned_to_nat(1024u);
v___x_1084_ = lean_nat_dec_le(v___x_1083_, v_prec_1068_);
if (v___x_1084_ == 0)
{
lean_object* v___x_1085_; 
v___x_1085_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_1070_ = v___x_1085_;
goto v___jp_1069_;
}
else
{
lean_object* v___x_1086_; 
v___x_1086_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_1070_ = v___x_1086_;
goto v___jp_1069_;
}
}
else
{
lean_object* v___x_1087_; uint8_t v___x_1088_; 
v___x_1087_ = lean_unsigned_to_nat(1024u);
v___x_1088_ = lean_nat_dec_le(v___x_1087_, v_prec_1068_);
if (v___x_1088_ == 0)
{
lean_object* v___x_1089_; 
v___x_1089_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__8, &l_Polydim_V4_instReprMemoryDomain_repr___closed__8_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__8);
v___y_1077_ = v___x_1089_;
goto v___jp_1076_;
}
else
{
lean_object* v___x_1090_; 
v___x_1090_ = lean_obj_once(&l_Polydim_V4_instReprMemoryDomain_repr___closed__9, &l_Polydim_V4_instReprMemoryDomain_repr___closed__9_once, _init_l_Polydim_V4_instReprMemoryDomain_repr___closed__9);
v___y_1077_ = v___x_1090_;
goto v___jp_1076_;
}
}
v___jp_1069_:
{
lean_object* v___x_1071_; lean_object* v___x_1072_; uint8_t v___x_1073_; lean_object* v___x_1074_; lean_object* v___x_1075_; 
v___x_1071_ = ((lean_object*)(l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__1));
lean_inc(v___y_1070_);
v___x_1072_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1072_, 0, v___y_1070_);
lean_ctor_set(v___x_1072_, 1, v___x_1071_);
v___x_1073_ = 0;
v___x_1074_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1074_, 0, v___x_1072_);
lean_ctor_set_uint8(v___x_1074_, sizeof(void*)*1, v___x_1073_);
v___x_1075_ = l_Repr_addAppParen(v___x_1074_, v_prec_1068_);
return v___x_1075_;
}
v___jp_1076_:
{
lean_object* v___x_1078_; lean_object* v___x_1079_; uint8_t v___x_1080_; lean_object* v___x_1081_; lean_object* v___x_1082_; 
v___x_1078_ = ((lean_object*)(l_Polydim_V4_instReprCayleySpectralDecomp_repr___closed__3));
lean_inc(v___y_1077_);
v___x_1079_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1079_, 0, v___y_1077_);
lean_ctor_set(v___x_1079_, 1, v___x_1078_);
v___x_1080_ = 0;
v___x_1081_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1081_, 0, v___x_1079_);
lean_ctor_set_uint8(v___x_1081_, sizeof(void*)*1, v___x_1080_);
v___x_1082_ = l_Repr_addAppParen(v___x_1081_, v_prec_1068_);
return v___x_1082_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleySpectralDecomp_repr___boxed(lean_object* v_x_1091_, lean_object* v_prec_1092_){
_start:
{
uint8_t v_x_117__boxed_1093_; lean_object* v_res_1094_; 
v_x_117__boxed_1093_ = lean_unbox(v_x_1091_);
v_res_1094_ = l_Polydim_V4_instReprCayleySpectralDecomp_repr(v_x_117__boxed_1093_, v_prec_1092_);
lean_dec(v_prec_1092_);
return v_res_1094_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg(lean_object* v_x_1118_){
_start:
{
lean_object* v_dim_1119_; lean_object* v_input__norm__sq_1120_; lean_object* v_output__norm__sq_1121_; lean_object* v___x_1122_; lean_object* v___x_1123_; lean_object* v___x_1124_; lean_object* v___x_1125_; lean_object* v___x_1126_; lean_object* v___x_1127_; uint8_t v___x_1128_; lean_object* v___x_1129_; lean_object* v___x_1130_; lean_object* v___x_1131_; lean_object* v___x_1132_; lean_object* v___x_1133_; lean_object* v___x_1134_; lean_object* v___x_1135_; lean_object* v___x_1136_; lean_object* v___x_1137_; lean_object* v___x_1138_; lean_object* v___x_1139_; lean_object* v___x_1140_; lean_object* v___x_1141_; lean_object* v___x_1142_; lean_object* v___x_1143_; lean_object* v___x_1144_; lean_object* v___x_1145_; lean_object* v___x_1146_; lean_object* v___x_1147_; lean_object* v___x_1148_; lean_object* v___x_1149_; lean_object* v___x_1150_; lean_object* v___x_1151_; lean_object* v___x_1152_; lean_object* v___x_1153_; lean_object* v___x_1154_; lean_object* v___x_1155_; lean_object* v___x_1156_; lean_object* v___x_1157_; lean_object* v___x_1158_; lean_object* v___x_1159_; lean_object* v___x_1160_; lean_object* v___x_1161_; lean_object* v___x_1162_; lean_object* v___x_1163_; lean_object* v___x_1164_; lean_object* v___x_1165_; lean_object* v___x_1166_; lean_object* v___x_1167_; lean_object* v___x_1168_; lean_object* v___x_1169_; lean_object* v___x_1170_; lean_object* v___x_1171_; lean_object* v___x_1172_; lean_object* v___x_1173_; lean_object* v___x_1174_; 
v_dim_1119_ = lean_ctor_get(v_x_1118_, 0);
lean_inc(v_dim_1119_);
v_input__norm__sq_1120_ = lean_ctor_get(v_x_1118_, 1);
lean_inc(v_input__norm__sq_1120_);
v_output__norm__sq_1121_ = lean_ctor_get(v_x_1118_, 2);
lean_inc(v_output__norm__sq_1121_);
lean_dec_ref(v_x_1118_);
v___x_1122_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_1123_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__3));
v___x_1124_ = lean_obj_once(&l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4, &l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4_once, _init_l_Polydim_V4_instReprNeumaierState_repr___redArg___closed__4);
v___x_1125_ = l_Nat_reprFast(v_dim_1119_);
v___x_1126_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1126_, 0, v___x_1125_);
v___x_1127_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1127_, 0, v___x_1124_);
lean_ctor_set(v___x_1127_, 1, v___x_1126_);
v___x_1128_ = 0;
v___x_1129_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1129_, 0, v___x_1127_);
lean_ctor_set_uint8(v___x_1129_, sizeof(void*)*1, v___x_1128_);
v___x_1130_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1130_, 0, v___x_1123_);
lean_ctor_set(v___x_1130_, 1, v___x_1129_);
v___x_1131_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_1132_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1132_, 0, v___x_1130_);
lean_ctor_set(v___x_1132_, 1, v___x_1131_);
v___x_1133_ = lean_box(1);
v___x_1134_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1134_, 0, v___x_1132_);
lean_ctor_set(v___x_1134_, 1, v___x_1133_);
v___x_1135_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__5));
v___x_1136_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1136_, 0, v___x_1134_);
lean_ctor_set(v___x_1136_, 1, v___x_1135_);
v___x_1137_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1137_, 0, v___x_1136_);
lean_ctor_set(v___x_1137_, 1, v___x_1122_);
v___x_1138_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9));
v___x_1139_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1139_, 0, v___x_1137_);
lean_ctor_set(v___x_1139_, 1, v___x_1138_);
v___x_1140_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1140_, 0, v___x_1139_);
lean_ctor_set(v___x_1140_, 1, v___x_1131_);
v___x_1141_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1141_, 0, v___x_1140_);
lean_ctor_set(v___x_1141_, 1, v___x_1133_);
v___x_1142_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__7));
v___x_1143_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1143_, 0, v___x_1141_);
lean_ctor_set(v___x_1143_, 1, v___x_1142_);
v___x_1144_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1144_, 0, v___x_1143_);
lean_ctor_set(v___x_1144_, 1, v___x_1122_);
v___x_1145_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__24);
v___x_1146_ = l_Nat_reprFast(v_input__norm__sq_1120_);
v___x_1147_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1147_, 0, v___x_1146_);
v___x_1148_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1148_, 0, v___x_1145_);
lean_ctor_set(v___x_1148_, 1, v___x_1147_);
v___x_1149_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1149_, 0, v___x_1148_);
lean_ctor_set_uint8(v___x_1149_, sizeof(void*)*1, v___x_1128_);
v___x_1150_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1150_, 0, v___x_1144_);
lean_ctor_set(v___x_1150_, 1, v___x_1149_);
v___x_1151_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1151_, 0, v___x_1150_);
lean_ctor_set(v___x_1151_, 1, v___x_1131_);
v___x_1152_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1152_, 0, v___x_1151_);
lean_ctor_set(v___x_1152_, 1, v___x_1133_);
v___x_1153_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__9));
v___x_1154_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1154_, 0, v___x_1152_);
lean_ctor_set(v___x_1154_, 1, v___x_1153_);
v___x_1155_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1155_, 0, v___x_1154_);
lean_ctor_set(v___x_1155_, 1, v___x_1122_);
v___x_1156_ = lean_obj_once(&l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6, &l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6_once, _init_l_Polydim_V4_instReprRcuReader_repr___redArg___closed__6);
v___x_1157_ = l_Nat_reprFast(v_output__norm__sq_1121_);
v___x_1158_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1158_, 0, v___x_1157_);
v___x_1159_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1159_, 0, v___x_1156_);
lean_ctor_set(v___x_1159_, 1, v___x_1158_);
v___x_1160_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1160_, 0, v___x_1159_);
lean_ctor_set_uint8(v___x_1160_, sizeof(void*)*1, v___x_1128_);
v___x_1161_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1161_, 0, v___x_1155_);
lean_ctor_set(v___x_1161_, 1, v___x_1160_);
v___x_1162_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1162_, 0, v___x_1161_);
lean_ctor_set(v___x_1162_, 1, v___x_1131_);
v___x_1163_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1163_, 0, v___x_1162_);
lean_ctor_set(v___x_1163_, 1, v___x_1133_);
v___x_1164_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__11));
v___x_1165_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1165_, 0, v___x_1163_);
lean_ctor_set(v___x_1165_, 1, v___x_1164_);
v___x_1166_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1166_, 0, v___x_1165_);
lean_ctor_set(v___x_1166_, 1, v___x_1122_);
v___x_1167_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1167_, 0, v___x_1166_);
lean_ctor_set(v___x_1167_, 1, v___x_1138_);
v___x_1168_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_1169_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_1170_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1170_, 0, v___x_1169_);
lean_ctor_set(v___x_1170_, 1, v___x_1167_);
v___x_1171_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_1172_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1172_, 0, v___x_1170_);
lean_ctor_set(v___x_1172_, 1, v___x_1171_);
v___x_1173_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1173_, 0, v___x_1168_);
lean_ctor_set(v___x_1173_, 1, v___x_1172_);
v___x_1174_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1174_, 0, v___x_1173_);
lean_ctor_set_uint8(v___x_1174_, sizeof(void*)*1, v___x_1128_);
return v___x_1174_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr(lean_object* v_x_1175_, lean_object* v_prec_1176_){
_start:
{
lean_object* v___x_1177_; 
v___x_1177_ = l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg(v_x_1175_);
return v___x_1177_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___boxed(lean_object* v_x_1178_, lean_object* v_prec_1179_){
_start:
{
lean_object* v_res_1180_; 
v_res_1180_ = l_Polydim_V4_instReprCayleyOrthogonalityCert_repr(v_x_1178_, v_prec_1179_);
lean_dec(v_prec_1179_);
return v_res_1180_;
}
}
static lean_object* _init_l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_1192_; lean_object* v___x_1193_; 
v___x_1192_ = lean_unsigned_to_nat(14u);
v___x_1193_ = lean_nat_to_int(v___x_1192_);
return v___x_1193_;
}
}
static lean_object* _init_l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19(void){
_start:
{
lean_object* v___x_1215_; lean_object* v___x_1216_; 
v___x_1215_ = lean_unsigned_to_nat(0u);
v___x_1216_ = lean_nat_to_int(v___x_1215_);
return v___x_1216_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg(lean_object* v_x_1217_){
_start:
{
lean_object* v_dim__kernel_1218_; lean_object* v_dim__range_1219_; lean_object* v_dim__total_1220_; lean_object* v_eig__kernel_1221_; lean_object* v_eig__range_1222_; lean_object* v___x_1223_; lean_object* v___x_1224_; lean_object* v___x_1225_; lean_object* v___x_1226_; lean_object* v___x_1227_; lean_object* v___x_1228_; uint8_t v___x_1229_; lean_object* v___x_1230_; lean_object* v___x_1231_; lean_object* v___x_1232_; lean_object* v___x_1233_; lean_object* v___x_1234_; lean_object* v___x_1235_; lean_object* v___x_1236_; lean_object* v___x_1237_; lean_object* v___x_1238_; lean_object* v___x_1239_; lean_object* v___x_1240_; lean_object* v___x_1241_; lean_object* v___x_1242_; lean_object* v___x_1243_; lean_object* v___x_1244_; lean_object* v___x_1245_; lean_object* v___x_1246_; lean_object* v___x_1247_; lean_object* v___x_1248_; lean_object* v___x_1249_; lean_object* v___x_1250_; lean_object* v___x_1251_; lean_object* v___x_1252_; lean_object* v___x_1253_; lean_object* v___x_1254_; lean_object* v___x_1255_; lean_object* v___x_1256_; lean_object* v___x_1257_; lean_object* v___x_1258_; lean_object* v___x_1259_; lean_object* v___x_1260_; lean_object* v___y_1262_; lean_object* v___y_1263_; lean_object* v___x_1286_; lean_object* v___x_1287_; lean_object* v___x_1288_; lean_object* v___x_1289_; lean_object* v___x_1290_; lean_object* v___x_1291_; lean_object* v___x_1292_; lean_object* v___x_1293_; lean_object* v___x_1294_; lean_object* v___x_1295_; lean_object* v___x_1296_; lean_object* v___x_1297_; lean_object* v___y_1299_; lean_object* v___x_1316_; lean_object* v___x_1317_; uint8_t v___x_1318_; 
v_dim__kernel_1218_ = lean_ctor_get(v_x_1217_, 0);
lean_inc(v_dim__kernel_1218_);
v_dim__range_1219_ = lean_ctor_get(v_x_1217_, 1);
lean_inc(v_dim__range_1219_);
v_dim__total_1220_ = lean_ctor_get(v_x_1217_, 2);
lean_inc(v_dim__total_1220_);
v_eig__kernel_1221_ = lean_ctor_get(v_x_1217_, 3);
lean_inc(v_eig__kernel_1221_);
v_eig__range_1222_ = lean_ctor_get(v_x_1217_, 4);
lean_inc(v_eig__range_1222_);
lean_dec_ref(v_x_1217_);
v___x_1223_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__5));
v___x_1224_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__3));
v___x_1225_ = lean_obj_once(&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4, &l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4_once, _init_l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__4);
v___x_1226_ = l_Nat_reprFast(v_dim__kernel_1218_);
v___x_1227_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1227_, 0, v___x_1226_);
v___x_1228_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1228_, 0, v___x_1225_);
lean_ctor_set(v___x_1228_, 1, v___x_1227_);
v___x_1229_ = 0;
v___x_1230_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1230_, 0, v___x_1228_);
lean_ctor_set_uint8(v___x_1230_, sizeof(void*)*1, v___x_1229_);
v___x_1231_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1231_, 0, v___x_1224_);
lean_ctor_set(v___x_1231_, 1, v___x_1230_);
v___x_1232_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__9));
v___x_1233_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1233_, 0, v___x_1231_);
lean_ctor_set(v___x_1233_, 1, v___x_1232_);
v___x_1234_ = lean_box(1);
v___x_1235_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1235_, 0, v___x_1233_);
lean_ctor_set(v___x_1235_, 1, v___x_1234_);
v___x_1236_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__6));
v___x_1237_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1237_, 0, v___x_1235_);
lean_ctor_set(v___x_1237_, 1, v___x_1236_);
v___x_1238_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1238_, 0, v___x_1237_);
lean_ctor_set(v___x_1238_, 1, v___x_1223_);
v___x_1239_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__15);
v___x_1240_ = l_Nat_reprFast(v_dim__range_1219_);
v___x_1241_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1241_, 0, v___x_1240_);
v___x_1242_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1242_, 0, v___x_1239_);
lean_ctor_set(v___x_1242_, 1, v___x_1241_);
v___x_1243_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1243_, 0, v___x_1242_);
lean_ctor_set_uint8(v___x_1243_, sizeof(void*)*1, v___x_1229_);
v___x_1244_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1244_, 0, v___x_1238_);
lean_ctor_set(v___x_1244_, 1, v___x_1243_);
v___x_1245_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1245_, 0, v___x_1244_);
lean_ctor_set(v___x_1245_, 1, v___x_1232_);
v___x_1246_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1246_, 0, v___x_1245_);
lean_ctor_set(v___x_1246_, 1, v___x_1234_);
v___x_1247_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__8));
v___x_1248_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1248_, 0, v___x_1246_);
lean_ctor_set(v___x_1248_, 1, v___x_1247_);
v___x_1249_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1249_, 0, v___x_1248_);
lean_ctor_set(v___x_1249_, 1, v___x_1223_);
v___x_1250_ = l_Nat_reprFast(v_dim__total_1220_);
v___x_1251_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1251_, 0, v___x_1250_);
v___x_1252_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1252_, 0, v___x_1239_);
lean_ctor_set(v___x_1252_, 1, v___x_1251_);
v___x_1253_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1253_, 0, v___x_1252_);
lean_ctor_set_uint8(v___x_1253_, sizeof(void*)*1, v___x_1229_);
v___x_1254_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1254_, 0, v___x_1249_);
lean_ctor_set(v___x_1254_, 1, v___x_1253_);
v___x_1255_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1255_, 0, v___x_1254_);
lean_ctor_set(v___x_1255_, 1, v___x_1232_);
v___x_1256_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1256_, 0, v___x_1255_);
lean_ctor_set(v___x_1256_, 1, v___x_1234_);
v___x_1257_ = ((lean_object*)(l_Polydim_V4_instReprCayleyOrthogonalityCert_repr___redArg___closed__5));
v___x_1258_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1258_, 0, v___x_1256_);
lean_ctor_set(v___x_1258_, 1, v___x_1257_);
v___x_1259_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1259_, 0, v___x_1258_);
lean_ctor_set(v___x_1259_, 1, v___x_1223_);
v___x_1260_ = ((lean_object*)(l_Polydim_V4_instReprGrassmannProjectorCert_repr___redArg___closed__9));
v___x_1286_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1286_, 0, v___x_1259_);
lean_ctor_set(v___x_1286_, 1, v___x_1260_);
v___x_1287_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1287_, 0, v___x_1286_);
lean_ctor_set(v___x_1287_, 1, v___x_1232_);
v___x_1288_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1288_, 0, v___x_1287_);
lean_ctor_set(v___x_1288_, 1, v___x_1234_);
v___x_1289_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__14));
v___x_1290_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1290_, 0, v___x_1288_);
lean_ctor_set(v___x_1290_, 1, v___x_1289_);
v___x_1291_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1291_, 0, v___x_1290_);
lean_ctor_set(v___x_1291_, 1, v___x_1223_);
v___x_1292_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1292_, 0, v___x_1291_);
lean_ctor_set(v___x_1292_, 1, v___x_1260_);
v___x_1293_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1293_, 0, v___x_1292_);
lean_ctor_set(v___x_1293_, 1, v___x_1232_);
v___x_1294_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1294_, 0, v___x_1293_);
lean_ctor_set(v___x_1294_, 1, v___x_1234_);
v___x_1295_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__16));
v___x_1296_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1296_, 0, v___x_1294_);
lean_ctor_set(v___x_1296_, 1, v___x_1295_);
v___x_1297_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1297_, 0, v___x_1296_);
lean_ctor_set(v___x_1297_, 1, v___x_1223_);
v___x_1316_ = lean_unsigned_to_nat(0u);
v___x_1317_ = lean_obj_once(&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19, &l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19_once, _init_l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19);
v___x_1318_ = lean_int_dec_lt(v_eig__kernel_1221_, v___x_1317_);
if (v___x_1318_ == 0)
{
lean_object* v___x_1319_; lean_object* v___x_1320_; 
v___x_1319_ = l_Int_repr(v_eig__kernel_1221_);
lean_dec(v_eig__kernel_1221_);
v___x_1320_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1320_, 0, v___x_1319_);
v___y_1299_ = v___x_1320_;
goto v___jp_1298_;
}
else
{
lean_object* v___x_1321_; lean_object* v___x_1322_; lean_object* v___x_1323_; 
v___x_1321_ = l_Int_repr(v_eig__kernel_1221_);
lean_dec(v_eig__kernel_1221_);
v___x_1322_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1322_, 0, v___x_1321_);
v___x_1323_ = l_Repr_addAppParen(v___x_1322_, v___x_1316_);
v___y_1299_ = v___x_1323_;
goto v___jp_1298_;
}
v___jp_1261_:
{
lean_object* v___x_1264_; lean_object* v___x_1265_; lean_object* v___x_1266_; lean_object* v___x_1267_; lean_object* v___x_1268_; lean_object* v___x_1269_; lean_object* v___x_1270_; lean_object* v___x_1271_; lean_object* v___x_1272_; lean_object* v___x_1273_; lean_object* v___x_1274_; lean_object* v___x_1275_; lean_object* v___x_1276_; lean_object* v___x_1277_; lean_object* v___x_1278_; lean_object* v___x_1279_; lean_object* v___x_1280_; lean_object* v___x_1281_; lean_object* v___x_1282_; lean_object* v___x_1283_; lean_object* v___x_1284_; lean_object* v___x_1285_; 
v___x_1264_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1264_, 0, v___x_1239_);
lean_ctor_set(v___x_1264_, 1, v___y_1263_);
v___x_1265_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1265_, 0, v___x_1264_);
lean_ctor_set_uint8(v___x_1265_, sizeof(void*)*1, v___x_1229_);
v___x_1266_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1266_, 0, v___y_1262_);
lean_ctor_set(v___x_1266_, 1, v___x_1265_);
v___x_1267_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1267_, 0, v___x_1266_);
lean_ctor_set(v___x_1267_, 1, v___x_1232_);
v___x_1268_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1268_, 0, v___x_1267_);
lean_ctor_set(v___x_1268_, 1, v___x_1234_);
v___x_1269_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__10));
v___x_1270_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1270_, 0, v___x_1268_);
lean_ctor_set(v___x_1270_, 1, v___x_1269_);
v___x_1271_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1271_, 0, v___x_1270_);
lean_ctor_set(v___x_1271_, 1, v___x_1223_);
v___x_1272_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1272_, 0, v___x_1271_);
lean_ctor_set(v___x_1272_, 1, v___x_1260_);
v___x_1273_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1273_, 0, v___x_1272_);
lean_ctor_set(v___x_1273_, 1, v___x_1232_);
v___x_1274_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1274_, 0, v___x_1273_);
lean_ctor_set(v___x_1274_, 1, v___x_1234_);
v___x_1275_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__12));
v___x_1276_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1276_, 0, v___x_1274_);
lean_ctor_set(v___x_1276_, 1, v___x_1275_);
v___x_1277_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1277_, 0, v___x_1276_);
lean_ctor_set(v___x_1277_, 1, v___x_1223_);
v___x_1278_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1278_, 0, v___x_1277_);
lean_ctor_set(v___x_1278_, 1, v___x_1260_);
v___x_1279_ = lean_obj_once(&l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27, &l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27_once, _init_l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__27);
v___x_1280_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__28));
v___x_1281_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1281_, 0, v___x_1280_);
lean_ctor_set(v___x_1281_, 1, v___x_1278_);
v___x_1282_ = ((lean_object*)(l_Polydim_V4_instReprLeaseDescriptor_repr___redArg___closed__29));
v___x_1283_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1283_, 0, v___x_1281_);
lean_ctor_set(v___x_1283_, 1, v___x_1282_);
v___x_1284_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1284_, 0, v___x_1279_);
lean_ctor_set(v___x_1284_, 1, v___x_1283_);
v___x_1285_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1285_, 0, v___x_1284_);
lean_ctor_set_uint8(v___x_1285_, sizeof(void*)*1, v___x_1229_);
return v___x_1285_;
}
v___jp_1298_:
{
lean_object* v___x_1300_; lean_object* v___x_1301_; lean_object* v___x_1302_; lean_object* v___x_1303_; lean_object* v___x_1304_; lean_object* v___x_1305_; lean_object* v___x_1306_; lean_object* v___x_1307_; lean_object* v___x_1308_; lean_object* v___x_1309_; uint8_t v___x_1310_; 
v___x_1300_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1300_, 0, v___x_1225_);
lean_ctor_set(v___x_1300_, 1, v___y_1299_);
v___x_1301_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1301_, 0, v___x_1300_);
lean_ctor_set_uint8(v___x_1301_, sizeof(void*)*1, v___x_1229_);
v___x_1302_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1302_, 0, v___x_1297_);
lean_ctor_set(v___x_1302_, 1, v___x_1301_);
v___x_1303_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1303_, 0, v___x_1302_);
lean_ctor_set(v___x_1303_, 1, v___x_1232_);
v___x_1304_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1304_, 0, v___x_1303_);
lean_ctor_set(v___x_1304_, 1, v___x_1234_);
v___x_1305_ = ((lean_object*)(l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__18));
v___x_1306_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1306_, 0, v___x_1304_);
lean_ctor_set(v___x_1306_, 1, v___x_1305_);
v___x_1307_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1307_, 0, v___x_1306_);
lean_ctor_set(v___x_1307_, 1, v___x_1223_);
v___x_1308_ = lean_unsigned_to_nat(0u);
v___x_1309_ = lean_obj_once(&l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19, &l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19_once, _init_l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg___closed__19);
v___x_1310_ = lean_int_dec_lt(v_eig__range_1222_, v___x_1309_);
if (v___x_1310_ == 0)
{
lean_object* v___x_1311_; lean_object* v___x_1312_; 
v___x_1311_ = l_Int_repr(v_eig__range_1222_);
lean_dec(v_eig__range_1222_);
v___x_1312_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1312_, 0, v___x_1311_);
v___y_1262_ = v___x_1307_;
v___y_1263_ = v___x_1312_;
goto v___jp_1261_;
}
else
{
lean_object* v___x_1313_; lean_object* v___x_1314_; lean_object* v___x_1315_; 
v___x_1313_ = l_Int_repr(v_eig__range_1222_);
lean_dec(v_eig__range_1222_);
v___x_1314_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1314_, 0, v___x_1313_);
v___x_1315_ = l_Repr_addAppParen(v___x_1314_, v___x_1308_);
v___y_1262_ = v___x_1307_;
v___y_1263_ = v___x_1315_;
goto v___jp_1261_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr(lean_object* v_x_1324_, lean_object* v_prec_1325_){
_start:
{
lean_object* v___x_1326_; 
v___x_1326_ = l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___redArg(v_x_1324_);
return v___x_1326_;
}
}
LEAN_EXPORT lean_object* l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr___boxed(lean_object* v_x_1327_, lean_object* v_prec_1328_){
_start:
{
lean_object* v_res_1329_; 
v_res_1329_ = l_Polydim_V4_instReprCayleyAsymptoticReflectorCert_repr(v_x_1327_, v_prec_1328_);
lean_dec(v_prec_1328_);
return v_res_1329_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__fraction__lattice__bits(void){
_start:
{
lean_object* v___x_1332_; 
v___x_1332_ = lean_unsigned_to_nat(2148u);
return v___x_1332_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__integer__exponent__bits(void){
_start:
{
lean_object* v___x_1333_; 
v___x_1333_ = lean_unsigned_to_nat(2048u);
return v___x_1333_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__term__growth__bits(void){
_start:
{
lean_object* v___x_1334_; 
v___x_1334_ = lean_unsigned_to_nat(64u);
return v___x_1334_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__sign__bit(void){
_start:
{
lean_object* v___x_1335_; 
v___x_1335_ = lean_unsigned_to_nat(1u);
return v___x_1335_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__word__size(void){
_start:
{
lean_object* v___x_1336_; 
v___x_1336_ = lean_unsigned_to_nat(64u);
return v___x_1336_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__num__gpr__words(void){
_start:
{
lean_object* v___x_1337_; 
v___x_1337_ = lean_unsigned_to_nat(67u);
return v___x_1337_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__minimal__signed__width(void){
_start:
{
lean_object* v___x_1338_; 
v___x_1338_ = lean_unsigned_to_nat(4261u);
return v___x_1338_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__implementation__width(void){
_start:
{
lean_object* v___x_1339_; 
v___x_1339_ = lean_unsigned_to_nat(4288u);
return v___x_1339_;
}
}
static lean_object* _init_l_Polydim_V4_kulisch__implementation__guard__margin(void){
_start:
{
lean_object* v___x_1340_; 
v___x_1340_ = lean_unsigned_to_nat(27u);
return v___x_1340_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_PMTP__V4__CORE_pmtp__v4__axioms(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
lean_initialize_runtime_module();
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
l_Polydim_V4_subnormal__min__quantum = _init_l_Polydim_V4_subnormal__min__quantum();
lean_mark_persistent(l_Polydim_V4_subnormal__min__quantum);
l_Polydim_V4_kulisch__fraction__lattice__bits = _init_l_Polydim_V4_kulisch__fraction__lattice__bits();
lean_mark_persistent(l_Polydim_V4_kulisch__fraction__lattice__bits);
l_Polydim_V4_kulisch__integer__exponent__bits = _init_l_Polydim_V4_kulisch__integer__exponent__bits();
lean_mark_persistent(l_Polydim_V4_kulisch__integer__exponent__bits);
l_Polydim_V4_kulisch__term__growth__bits = _init_l_Polydim_V4_kulisch__term__growth__bits();
lean_mark_persistent(l_Polydim_V4_kulisch__term__growth__bits);
l_Polydim_V4_kulisch__sign__bit = _init_l_Polydim_V4_kulisch__sign__bit();
lean_mark_persistent(l_Polydim_V4_kulisch__sign__bit);
l_Polydim_V4_kulisch__word__size = _init_l_Polydim_V4_kulisch__word__size();
lean_mark_persistent(l_Polydim_V4_kulisch__word__size);
l_Polydim_V4_kulisch__num__gpr__words = _init_l_Polydim_V4_kulisch__num__gpr__words();
lean_mark_persistent(l_Polydim_V4_kulisch__num__gpr__words);
l_Polydim_V4_kulisch__minimal__signed__width = _init_l_Polydim_V4_kulisch__minimal__signed__width();
lean_mark_persistent(l_Polydim_V4_kulisch__minimal__signed__width);
l_Polydim_V4_kulisch__implementation__width = _init_l_Polydim_V4_kulisch__implementation__width();
lean_mark_persistent(l_Polydim_V4_kulisch__implementation__width);
l_Polydim_V4_kulisch__implementation__guard__margin = _init_l_Polydim_V4_kulisch__implementation__guard__margin();
lean_mark_persistent(l_Polydim_V4_kulisch__implementation__guard__margin);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
