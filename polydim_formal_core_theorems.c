// Lean compiler output
// Module: polydim_formal_core_theorems
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
lean_object* l_Lean_mkAtom(lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
lean_object* lean_array_push(lean_object*, lean_object*);
lean_object* l_Lean_Name_mkStr4(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_Lean_Name_mkStr1(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqMetricSignature_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqMetricSignature_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqMetricSignature(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqMetricSignature___boxed(lean_object*, lean_object*);
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__0_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "p"};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__2_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__3_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__6_value;
static lean_once_cell_t l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "q"};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__11_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "dim_pos"};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__12 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__12_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__12_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__13 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__13_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "_"};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__14 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__14_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__14_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15_value;
static const lean_string_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__16 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__16_value;
static lean_once_cell_t l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17;
static lean_once_cell_t l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19_value;
static const lean_ctor_object l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__16_value)}};
static const lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Polydim_Formal_instReprMetricSignature___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Polydim_Formal_instReprMetricSignature_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Polydim_Formal_instReprMetricSignature___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature___closed__0_value;
LEAN_EXPORT const lean_object* l_Polydim_Formal_instReprMetricSignature = (const lean_object*)&l_Polydim_Formal_instReprMetricSignature___closed__0_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_MetricSignature_dim(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_MetricSignature_dim___boxed(lean_object*);
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "Lean"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "Parser"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "Tactic"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "tacticSeq"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__3 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__3_value;
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_0 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0_value),LEAN_SCALAR_PTR_LITERAL(70, 193, 83, 126, 233, 67, 208, 165)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_1 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_0),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1_value),LEAN_SCALAR_PTR_LITERAL(103, 136, 125, 166, 167, 98, 71, 111)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_2 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_1),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2_value),LEAN_SCALAR_PTR_LITERAL(166, 58, 35, 182, 187, 130, 147, 254)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value_aux_2),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__3_value),LEAN_SCALAR_PTR_LITERAL(212, 140, 85, 215, 241, 69, 7, 118)}};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4_value;
static const lean_array_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "tacticSeq1Indented"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__6 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__6_value;
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_0 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0_value),LEAN_SCALAR_PTR_LITERAL(70, 193, 83, 126, 233, 67, 208, 165)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_1 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_0),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1_value),LEAN_SCALAR_PTR_LITERAL(103, 136, 125, 166, 167, 98, 71, 111)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_2 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_1),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2_value),LEAN_SCALAR_PTR_LITERAL(166, 58, 35, 182, 187, 130, 147, 254)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value_aux_2),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__6_value),LEAN_SCALAR_PTR_LITERAL(223, 90, 160, 238, 133, 180, 23, 239)}};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "null"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__8 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__8_value),LEAN_SCALAR_PTR_LITERAL(24, 58, 49, 223, 146, 207, 197, 136)}};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__9 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__9_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "tacticRfl"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__10 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_0 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__0_value),LEAN_SCALAR_PTR_LITERAL(70, 193, 83, 126, 233, 67, 208, 165)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_1 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_0),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__1_value),LEAN_SCALAR_PTR_LITERAL(103, 136, 125, 166, 167, 98, 71, 111)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_2 = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_1),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__2_value),LEAN_SCALAR_PTR_LITERAL(166, 58, 35, 182, 187, 130, 147, 254)}};
static const lean_ctor_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 8, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value_aux_2),((lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__10_value),LEAN_SCALAR_PTR_LITERAL(201, 188, 173, 198, 169, 252, 183, 45)}};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11_value;
static const lean_string_object l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "rfl"};
static const lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__12 = (const lean_object*)&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__12_value;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20;
static lean_once_cell_t l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21;
LEAN_EXPORT lean_object* l_Polydim_Formal_Hypersphere_h__dim___autoParam;
static const lean_string_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "dim_ambient"};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4;
static const lean_string_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "dim_sphere"};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__6_value;
static lean_once_cell_t l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7;
static const lean_string_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "h_dim"};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__9_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere(lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState_decEq(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState___boxed(lean_object*, lean_object*, lean_object*);
static const lean_string_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "state_id"};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4;
static const lean_string_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "norm_sq"};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__6_value;
static lean_once_cell_t l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7;
static const lean_string_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "is_unit"};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__9_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "grade"};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4;
static const lean_string_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "h_grade"};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__6_value;
static const lean_string_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "blade_norm_sq"};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__7_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__7_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__8_value;
static lean_once_cell_t l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9;
static const lean_string_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "h_bounded"};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__11_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade(lean_object*, lean_object*);
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__13_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__0_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__1_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__3_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__3_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__4_value;
static const lean_string_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "H_X"};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__6_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__4_value),((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__6_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__7_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__7_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__8_value;
static lean_once_cell_t l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9;
static const lean_string_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "I_XY"};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__11_value;
static lean_once_cell_t l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12;
static const lean_string_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "geom_bound"};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__13 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__13_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__13_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__14 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__14_value;
static const lean_string_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "info_pos"};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__15 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__15_value;
static const lean_ctor_object l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__15_value)}};
static const lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__16 = (const lean_object*)&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__16_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor(lean_object*);
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "vocab_size"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vocab_ge_two"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__5_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "seq_length"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__6_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__6_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__7_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "seq_pos"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "bits_per_token"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__11_value;
static lean_once_cell_t l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "C_token"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__13 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__13_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__13_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__14 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__14_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "h_capacity"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__15 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__15_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__15_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__16 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__16_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "bottleneck_info"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__17 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__17_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__17_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__18 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__18_value;
static const lean_string_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "bottleneck_entropy"};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__19 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__19_value;
static const lean_ctor_object l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__19_value)}};
static const lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__20 = (const lean_object*)&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__20_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer(lean_object*, lean_object*);
static const lean_string_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "I_TY"};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__3_value;
static const lean_string_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "dpi_upper_bound"};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__4 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__4_value;
static const lean_ctor_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__4_value)}};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__5_value;
static const lean_string_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 17, .m_capacity = 17, .m_length = 16, .m_data = "dpi_source_bound"};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__6_value;
static const lean_ctor_object l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__6_value)}};
static const lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__7 = (const lean_object*)&l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__7_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel(lean_object*, lean_object*, lean_object*);
static const lean_string_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 17, .m_capacity = 17, .m_length = 16, .m_data = "mutual_info_pmtp"};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__0 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__0_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__0_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__1 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__1_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__1_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__2 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__2_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__2_value),((lean_object*)&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__3 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__3_value;
static lean_once_cell_t l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4;
static const lean_string_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "entropy_destruction"};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__5 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__5_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__5_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__6 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__6_value;
static lean_once_cell_t l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7;
static const lean_string_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "h_pmtp_info"};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__8 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__8_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__8_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__9 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__9_value;
static const lean_string_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 17, .m_capacity = 17, .m_length = 16, .m_data = "h_pmtp_zero_loss"};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__10 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__10_value;
static const lean_ctor_object l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__10_value)}};
static const lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__11 = (const lean_object*)&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__11_value;
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqMetricSignature_decEq(lean_object* v_x_1_, lean_object* v_x_2_){
_start:
{
lean_object* v_p_3_; lean_object* v_q_4_; lean_object* v_p_5_; lean_object* v_q_6_; uint8_t v___x_7_; 
v_p_3_ = lean_ctor_get(v_x_1_, 0);
v_q_4_ = lean_ctor_get(v_x_1_, 1);
v_p_5_ = lean_ctor_get(v_x_2_, 0);
v_q_6_ = lean_ctor_get(v_x_2_, 1);
v___x_7_ = lean_nat_dec_eq(v_p_3_, v_p_5_);
if (v___x_7_ == 0)
{
return v___x_7_;
}
else
{
uint8_t v___x_8_; 
v___x_8_ = lean_nat_dec_eq(v_q_4_, v_q_6_);
return v___x_8_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqMetricSignature_decEq___boxed(lean_object* v_x_9_, lean_object* v_x_10_){
_start:
{
uint8_t v_res_11_; lean_object* v_r_12_; 
v_res_11_ = l_Polydim_Formal_instDecidableEqMetricSignature_decEq(v_x_9_, v_x_10_);
lean_dec_ref(v_x_10_);
lean_dec_ref(v_x_9_);
v_r_12_ = lean_box(v_res_11_);
return v_r_12_;
}
}
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqMetricSignature(lean_object* v_x_13_, lean_object* v_x_14_){
_start:
{
uint8_t v___x_15_; 
v___x_15_ = l_Polydim_Formal_instDecidableEqMetricSignature_decEq(v_x_13_, v_x_14_);
return v___x_15_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqMetricSignature___boxed(lean_object* v_x_16_, lean_object* v_x_17_){
_start:
{
uint8_t v_res_18_; lean_object* v_r_19_; 
v_res_18_ = l_Polydim_Formal_instDecidableEqMetricSignature(v_x_16_, v_x_17_);
lean_dec_ref(v_x_17_);
lean_dec_ref(v_x_16_);
v_r_19_ = lean_box(v_res_18_);
return v_r_19_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_33_; lean_object* v___x_34_; 
v___x_33_ = lean_unsigned_to_nat(5u);
v___x_34_ = lean_nat_to_int(v___x_33_);
return v___x_34_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17(void){
_start:
{
lean_object* v___x_48_; lean_object* v___x_49_; 
v___x_48_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__0));
v___x_49_ = lean_string_length(v___x_48_);
return v___x_49_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18(void){
_start:
{
lean_object* v___x_50_; lean_object* v___x_51_; 
v___x_50_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__17);
v___x_51_ = lean_nat_to_int(v___x_50_);
return v___x_51_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr___redArg(lean_object* v_x_56_){
_start:
{
lean_object* v_p_57_; lean_object* v_q_58_; lean_object* v___x_60_; uint8_t v_isShared_61_; uint8_t v_isSharedCheck_99_; 
v_p_57_ = lean_ctor_get(v_x_56_, 0);
v_q_58_ = lean_ctor_get(v_x_56_, 1);
v_isSharedCheck_99_ = !lean_is_exclusive(v_x_56_);
if (v_isSharedCheck_99_ == 0)
{
v___x_60_ = v_x_56_;
v_isShared_61_ = v_isSharedCheck_99_;
goto v_resetjp_59_;
}
else
{
lean_inc(v_q_58_);
lean_inc(v_p_57_);
lean_dec(v_x_56_);
v___x_60_ = lean_box(0);
v_isShared_61_ = v_isSharedCheck_99_;
goto v_resetjp_59_;
}
v_resetjp_59_:
{
lean_object* v___x_62_; lean_object* v___x_63_; lean_object* v___x_64_; lean_object* v___x_65_; lean_object* v___x_66_; lean_object* v___x_68_; 
v___x_62_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_63_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__6));
v___x_64_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__7);
v___x_65_ = l_Nat_reprFast(v_p_57_);
v___x_66_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_66_, 0, v___x_65_);
if (v_isShared_61_ == 0)
{
lean_ctor_set_tag(v___x_60_, 4);
lean_ctor_set(v___x_60_, 1, v___x_66_);
lean_ctor_set(v___x_60_, 0, v___x_64_);
v___x_68_ = v___x_60_;
goto v_reusejp_67_;
}
else
{
lean_object* v_reuseFailAlloc_98_; 
v_reuseFailAlloc_98_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_98_, 0, v___x_64_);
lean_ctor_set(v_reuseFailAlloc_98_, 1, v___x_66_);
v___x_68_ = v_reuseFailAlloc_98_;
goto v_reusejp_67_;
}
v_reusejp_67_:
{
uint8_t v___x_69_; lean_object* v___x_70_; lean_object* v___x_71_; lean_object* v___x_72_; lean_object* v___x_73_; lean_object* v___x_74_; lean_object* v___x_75_; lean_object* v___x_76_; lean_object* v___x_77_; lean_object* v___x_78_; lean_object* v___x_79_; lean_object* v___x_80_; lean_object* v___x_81_; lean_object* v___x_82_; lean_object* v___x_83_; lean_object* v___x_84_; lean_object* v___x_85_; lean_object* v___x_86_; lean_object* v___x_87_; lean_object* v___x_88_; lean_object* v___x_89_; lean_object* v___x_90_; lean_object* v___x_91_; lean_object* v___x_92_; lean_object* v___x_93_; lean_object* v___x_94_; lean_object* v___x_95_; lean_object* v___x_96_; lean_object* v___x_97_; 
v___x_69_ = 0;
v___x_70_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_70_, 0, v___x_68_);
lean_ctor_set_uint8(v___x_70_, sizeof(void*)*1, v___x_69_);
v___x_71_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_71_, 0, v___x_63_);
lean_ctor_set(v___x_71_, 1, v___x_70_);
v___x_72_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_73_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_73_, 0, v___x_71_);
lean_ctor_set(v___x_73_, 1, v___x_72_);
v___x_74_ = lean_box(1);
v___x_75_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_75_, 0, v___x_73_);
lean_ctor_set(v___x_75_, 1, v___x_74_);
v___x_76_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__11));
v___x_77_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_77_, 0, v___x_75_);
lean_ctor_set(v___x_77_, 1, v___x_76_);
v___x_78_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_78_, 0, v___x_77_);
lean_ctor_set(v___x_78_, 1, v___x_62_);
v___x_79_ = l_Nat_reprFast(v_q_58_);
v___x_80_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_80_, 0, v___x_79_);
v___x_81_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_81_, 0, v___x_64_);
lean_ctor_set(v___x_81_, 1, v___x_80_);
v___x_82_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_82_, 0, v___x_81_);
lean_ctor_set_uint8(v___x_82_, sizeof(void*)*1, v___x_69_);
v___x_83_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_83_, 0, v___x_78_);
lean_ctor_set(v___x_83_, 1, v___x_82_);
v___x_84_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_84_, 0, v___x_83_);
lean_ctor_set(v___x_84_, 1, v___x_72_);
v___x_85_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_85_, 0, v___x_84_);
lean_ctor_set(v___x_85_, 1, v___x_74_);
v___x_86_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__13));
v___x_87_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_87_, 0, v___x_85_);
lean_ctor_set(v___x_87_, 1, v___x_86_);
v___x_88_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_88_, 0, v___x_87_);
lean_ctor_set(v___x_88_, 1, v___x_62_);
v___x_89_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_90_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_90_, 0, v___x_88_);
lean_ctor_set(v___x_90_, 1, v___x_89_);
v___x_91_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_92_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_93_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_93_, 0, v___x_92_);
lean_ctor_set(v___x_93_, 1, v___x_90_);
v___x_94_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_95_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_95_, 0, v___x_93_);
lean_ctor_set(v___x_95_, 1, v___x_94_);
v___x_96_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_96_, 0, v___x_91_);
lean_ctor_set(v___x_96_, 1, v___x_95_);
v___x_97_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_97_, 0, v___x_96_);
lean_ctor_set_uint8(v___x_97_, sizeof(void*)*1, v___x_69_);
return v___x_97_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr(lean_object* v_x_100_, lean_object* v_prec_101_){
_start:
{
lean_object* v___x_102_; 
v___x_102_ = l_Polydim_Formal_instReprMetricSignature_repr___redArg(v_x_100_);
return v___x_102_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprMetricSignature_repr___boxed(lean_object* v_x_103_, lean_object* v_prec_104_){
_start:
{
lean_object* v_res_105_; 
v_res_105_ = l_Polydim_Formal_instReprMetricSignature_repr(v_x_103_, v_prec_104_);
lean_dec(v_prec_104_);
return v_res_105_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_MetricSignature_dim(lean_object* v_sig_108_){
_start:
{
lean_object* v_p_109_; lean_object* v_q_110_; lean_object* v___x_111_; 
v_p_109_ = lean_ctor_get(v_sig_108_, 0);
v_q_110_ = lean_ctor_get(v_sig_108_, 1);
v___x_111_ = lean_nat_add(v_p_109_, v_q_110_);
return v___x_111_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_MetricSignature_dim___boxed(lean_object* v_sig_112_){
_start:
{
lean_object* v_res_113_; 
v_res_113_ = l_Polydim_Formal_MetricSignature_dim(v_sig_112_);
lean_dec_ref(v_sig_112_);
return v_res_113_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13(void){
_start:
{
lean_object* v___x_141_; lean_object* v___x_142_; 
v___x_141_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__12));
v___x_142_ = l_Lean_mkAtom(v___x_141_);
return v___x_142_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14(void){
_start:
{
lean_object* v___x_143_; lean_object* v___x_144_; lean_object* v___x_145_; 
v___x_143_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__13);
v___x_144_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5));
v___x_145_ = lean_array_push(v___x_144_, v___x_143_);
return v___x_145_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15(void){
_start:
{
lean_object* v___x_146_; lean_object* v___x_147_; lean_object* v___x_148_; lean_object* v___x_149_; 
v___x_146_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__14);
v___x_147_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__11));
v___x_148_ = lean_box(2);
v___x_149_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_149_, 0, v___x_148_);
lean_ctor_set(v___x_149_, 1, v___x_147_);
lean_ctor_set(v___x_149_, 2, v___x_146_);
return v___x_149_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16(void){
_start:
{
lean_object* v___x_150_; lean_object* v___x_151_; lean_object* v___x_152_; 
v___x_150_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__15);
v___x_151_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5));
v___x_152_ = lean_array_push(v___x_151_, v___x_150_);
return v___x_152_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17(void){
_start:
{
lean_object* v___x_153_; lean_object* v___x_154_; lean_object* v___x_155_; lean_object* v___x_156_; 
v___x_153_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__16);
v___x_154_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__9));
v___x_155_ = lean_box(2);
v___x_156_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_156_, 0, v___x_155_);
lean_ctor_set(v___x_156_, 1, v___x_154_);
lean_ctor_set(v___x_156_, 2, v___x_153_);
return v___x_156_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18(void){
_start:
{
lean_object* v___x_157_; lean_object* v___x_158_; lean_object* v___x_159_; 
v___x_157_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__17);
v___x_158_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5));
v___x_159_ = lean_array_push(v___x_158_, v___x_157_);
return v___x_159_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19(void){
_start:
{
lean_object* v___x_160_; lean_object* v___x_161_; lean_object* v___x_162_; lean_object* v___x_163_; 
v___x_160_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__18);
v___x_161_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__7));
v___x_162_ = lean_box(2);
v___x_163_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_163_, 0, v___x_162_);
lean_ctor_set(v___x_163_, 1, v___x_161_);
lean_ctor_set(v___x_163_, 2, v___x_160_);
return v___x_163_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20(void){
_start:
{
lean_object* v___x_164_; lean_object* v___x_165_; lean_object* v___x_166_; 
v___x_164_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__19);
v___x_165_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__5));
v___x_166_ = lean_array_push(v___x_165_, v___x_164_);
return v___x_166_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21(void){
_start:
{
lean_object* v___x_167_; lean_object* v___x_168_; lean_object* v___x_169_; lean_object* v___x_170_; 
v___x_167_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__20);
v___x_168_ = ((lean_object*)(l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__4));
v___x_169_ = lean_box(2);
v___x_170_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_170_, 0, v___x_169_);
lean_ctor_set(v___x_170_, 1, v___x_168_);
lean_ctor_set(v___x_170_, 2, v___x_167_);
return v___x_170_;
}
}
static lean_object* _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam(void){
_start:
{
lean_object* v___x_171_; 
v___x_171_ = lean_obj_once(&l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21, &l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21_once, _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam___closed__21);
return v___x_171_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_181_; lean_object* v___x_182_; 
v___x_181_ = lean_unsigned_to_nat(15u);
v___x_182_ = lean_nat_to_int(v___x_181_);
return v___x_182_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_186_; lean_object* v___x_187_; 
v___x_186_ = lean_unsigned_to_nat(14u);
v___x_187_ = lean_nat_to_int(v___x_186_);
return v___x_187_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr___redArg(lean_object* v_x_191_){
_start:
{
lean_object* v_dim__ambient_192_; lean_object* v_dim__sphere_193_; lean_object* v___x_195_; uint8_t v_isShared_196_; uint8_t v_isSharedCheck_235_; 
v_dim__ambient_192_ = lean_ctor_get(v_x_191_, 0);
v_dim__sphere_193_ = lean_ctor_get(v_x_191_, 1);
v_isSharedCheck_235_ = !lean_is_exclusive(v_x_191_);
if (v_isSharedCheck_235_ == 0)
{
v___x_195_ = v_x_191_;
v_isShared_196_ = v_isSharedCheck_235_;
goto v_resetjp_194_;
}
else
{
lean_inc(v_dim__sphere_193_);
lean_inc(v_dim__ambient_192_);
lean_dec(v_x_191_);
v___x_195_ = lean_box(0);
v_isShared_196_ = v_isSharedCheck_235_;
goto v_resetjp_194_;
}
v_resetjp_194_:
{
lean_object* v___x_197_; lean_object* v___x_198_; lean_object* v___x_199_; lean_object* v___x_200_; lean_object* v___x_201_; lean_object* v___x_203_; 
v___x_197_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_198_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__3));
v___x_199_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4, &l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4_once, _init_l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__4);
v___x_200_ = l_Nat_reprFast(v_dim__ambient_192_);
v___x_201_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_201_, 0, v___x_200_);
if (v_isShared_196_ == 0)
{
lean_ctor_set_tag(v___x_195_, 4);
lean_ctor_set(v___x_195_, 1, v___x_201_);
lean_ctor_set(v___x_195_, 0, v___x_199_);
v___x_203_ = v___x_195_;
goto v_reusejp_202_;
}
else
{
lean_object* v_reuseFailAlloc_234_; 
v_reuseFailAlloc_234_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_234_, 0, v___x_199_);
lean_ctor_set(v_reuseFailAlloc_234_, 1, v___x_201_);
v___x_203_ = v_reuseFailAlloc_234_;
goto v_reusejp_202_;
}
v_reusejp_202_:
{
uint8_t v___x_204_; lean_object* v___x_205_; lean_object* v___x_206_; lean_object* v___x_207_; lean_object* v___x_208_; lean_object* v___x_209_; lean_object* v___x_210_; lean_object* v___x_211_; lean_object* v___x_212_; lean_object* v___x_213_; lean_object* v___x_214_; lean_object* v___x_215_; lean_object* v___x_216_; lean_object* v___x_217_; lean_object* v___x_218_; lean_object* v___x_219_; lean_object* v___x_220_; lean_object* v___x_221_; lean_object* v___x_222_; lean_object* v___x_223_; lean_object* v___x_224_; lean_object* v___x_225_; lean_object* v___x_226_; lean_object* v___x_227_; lean_object* v___x_228_; lean_object* v___x_229_; lean_object* v___x_230_; lean_object* v___x_231_; lean_object* v___x_232_; lean_object* v___x_233_; 
v___x_204_ = 0;
v___x_205_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_205_, 0, v___x_203_);
lean_ctor_set_uint8(v___x_205_, sizeof(void*)*1, v___x_204_);
v___x_206_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_206_, 0, v___x_198_);
lean_ctor_set(v___x_206_, 1, v___x_205_);
v___x_207_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_208_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_208_, 0, v___x_206_);
lean_ctor_set(v___x_208_, 1, v___x_207_);
v___x_209_ = lean_box(1);
v___x_210_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_210_, 0, v___x_208_);
lean_ctor_set(v___x_210_, 1, v___x_209_);
v___x_211_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__6));
v___x_212_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_212_, 0, v___x_210_);
lean_ctor_set(v___x_212_, 1, v___x_211_);
v___x_213_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_213_, 0, v___x_212_);
lean_ctor_set(v___x_213_, 1, v___x_197_);
v___x_214_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7, &l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7);
v___x_215_ = l_Nat_reprFast(v_dim__sphere_193_);
v___x_216_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_216_, 0, v___x_215_);
v___x_217_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_217_, 0, v___x_214_);
lean_ctor_set(v___x_217_, 1, v___x_216_);
v___x_218_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_218_, 0, v___x_217_);
lean_ctor_set_uint8(v___x_218_, sizeof(void*)*1, v___x_204_);
v___x_219_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_219_, 0, v___x_213_);
lean_ctor_set(v___x_219_, 1, v___x_218_);
v___x_220_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_220_, 0, v___x_219_);
lean_ctor_set(v___x_220_, 1, v___x_207_);
v___x_221_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_221_, 0, v___x_220_);
lean_ctor_set(v___x_221_, 1, v___x_209_);
v___x_222_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__9));
v___x_223_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_223_, 0, v___x_221_);
lean_ctor_set(v___x_223_, 1, v___x_222_);
v___x_224_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_224_, 0, v___x_223_);
lean_ctor_set(v___x_224_, 1, v___x_197_);
v___x_225_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_226_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_226_, 0, v___x_224_);
lean_ctor_set(v___x_226_, 1, v___x_225_);
v___x_227_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_228_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_229_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_229_, 0, v___x_228_);
lean_ctor_set(v___x_229_, 1, v___x_226_);
v___x_230_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_231_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_231_, 0, v___x_229_);
lean_ctor_set(v___x_231_, 1, v___x_230_);
v___x_232_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_232_, 0, v___x_227_);
lean_ctor_set(v___x_232_, 1, v___x_231_);
v___x_233_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_233_, 0, v___x_232_);
lean_ctor_set_uint8(v___x_233_, sizeof(void*)*1, v___x_204_);
return v___x_233_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr(lean_object* v_sig_236_, lean_object* v_x_237_, lean_object* v_prec_238_){
_start:
{
lean_object* v___x_239_; 
v___x_239_ = l_Polydim_Formal_instReprHypersphere_repr___redArg(v_x_237_);
return v___x_239_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere_repr___boxed(lean_object* v_sig_240_, lean_object* v_x_241_, lean_object* v_prec_242_){
_start:
{
lean_object* v_res_243_; 
v_res_243_ = l_Polydim_Formal_instReprHypersphere_repr(v_sig_240_, v_x_241_, v_prec_242_);
lean_dec(v_prec_242_);
lean_dec_ref(v_sig_240_);
return v_res_243_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphere(lean_object* v_sig_244_){
_start:
{
lean_object* v___x_245_; 
v___x_245_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprHypersphere_repr___boxed), 3, 1);
lean_closure_set(v___x_245_, 0, v_sig_244_);
return v___x_245_;
}
}
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(lean_object* v_x_246_, lean_object* v_x_247_){
_start:
{
lean_object* v_state__id_248_; lean_object* v_norm__sq_249_; lean_object* v_state__id_250_; lean_object* v_norm__sq_251_; uint8_t v___x_252_; 
v_state__id_248_ = lean_ctor_get(v_x_246_, 0);
v_norm__sq_249_ = lean_ctor_get(v_x_246_, 1);
v_state__id_250_ = lean_ctor_get(v_x_247_, 0);
v_norm__sq_251_ = lean_ctor_get(v_x_247_, 1);
v___x_252_ = lean_nat_dec_eq(v_state__id_248_, v_state__id_250_);
if (v___x_252_ == 0)
{
return v___x_252_;
}
else
{
uint8_t v___x_253_; 
v___x_253_ = lean_nat_dec_eq(v_norm__sq_249_, v_norm__sq_251_);
return v___x_253_;
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg___boxed(lean_object* v_x_254_, lean_object* v_x_255_){
_start:
{
uint8_t v_res_256_; lean_object* v_r_257_; 
v_res_256_ = l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(v_x_254_, v_x_255_);
lean_dec_ref(v_x_255_);
lean_dec_ref(v_x_254_);
v_r_257_ = lean_box(v_res_256_);
return v_r_257_;
}
}
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState_decEq(lean_object* v_sig_258_, lean_object* v_x_259_, lean_object* v_x_260_){
_start:
{
uint8_t v___x_261_; 
v___x_261_ = l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(v_x_259_, v_x_260_);
return v___x_261_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___boxed(lean_object* v_sig_262_, lean_object* v_x_263_, lean_object* v_x_264_){
_start:
{
uint8_t v_res_265_; lean_object* v_r_266_; 
v_res_265_ = l_Polydim_Formal_instDecidableEqHypersphericalState_decEq(v_sig_262_, v_x_263_, v_x_264_);
lean_dec_ref(v_x_264_);
lean_dec_ref(v_x_263_);
lean_dec_ref(v_sig_262_);
v_r_266_ = lean_box(v_res_265_);
return v_r_266_;
}
}
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState___redArg(lean_object* v_x_267_, lean_object* v_x_268_){
_start:
{
uint8_t v___x_269_; 
v___x_269_ = l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(v_x_267_, v_x_268_);
return v___x_269_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState___redArg___boxed(lean_object* v_x_270_, lean_object* v_x_271_){
_start:
{
uint8_t v_res_272_; lean_object* v_r_273_; 
v_res_272_ = l_Polydim_Formal_instDecidableEqHypersphericalState___redArg(v_x_270_, v_x_271_);
lean_dec_ref(v_x_271_);
lean_dec_ref(v_x_270_);
v_r_273_ = lean_box(v_res_272_);
return v_r_273_;
}
}
LEAN_EXPORT uint8_t l_Polydim_Formal_instDecidableEqHypersphericalState(lean_object* v_sig_274_, lean_object* v_x_275_, lean_object* v_x_276_){
_start:
{
uint8_t v___x_277_; 
v___x_277_ = l_Polydim_Formal_instDecidableEqHypersphericalState_decEq___redArg(v_x_275_, v_x_276_);
return v___x_277_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instDecidableEqHypersphericalState___boxed(lean_object* v_sig_278_, lean_object* v_x_279_, lean_object* v_x_280_){
_start:
{
uint8_t v_res_281_; lean_object* v_r_282_; 
v_res_281_ = l_Polydim_Formal_instDecidableEqHypersphericalState(v_sig_278_, v_x_279_, v_x_280_);
lean_dec_ref(v_x_280_);
lean_dec_ref(v_x_279_);
lean_dec_ref(v_sig_278_);
v_r_282_ = lean_box(v_res_281_);
return v_r_282_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_292_; lean_object* v___x_293_; 
v___x_292_ = lean_unsigned_to_nat(12u);
v___x_293_ = lean_nat_to_int(v___x_292_);
return v___x_293_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_297_; lean_object* v___x_298_; 
v___x_297_ = lean_unsigned_to_nat(11u);
v___x_298_ = lean_nat_to_int(v___x_297_);
return v___x_298_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___redArg(lean_object* v_x_302_){
_start:
{
lean_object* v_state__id_303_; lean_object* v_norm__sq_304_; lean_object* v___x_306_; uint8_t v_isShared_307_; uint8_t v_isSharedCheck_346_; 
v_state__id_303_ = lean_ctor_get(v_x_302_, 0);
v_norm__sq_304_ = lean_ctor_get(v_x_302_, 1);
v_isSharedCheck_346_ = !lean_is_exclusive(v_x_302_);
if (v_isSharedCheck_346_ == 0)
{
v___x_306_ = v_x_302_;
v_isShared_307_ = v_isSharedCheck_346_;
goto v_resetjp_305_;
}
else
{
lean_inc(v_norm__sq_304_);
lean_inc(v_state__id_303_);
lean_dec(v_x_302_);
v___x_306_ = lean_box(0);
v_isShared_307_ = v_isSharedCheck_346_;
goto v_resetjp_305_;
}
v_resetjp_305_:
{
lean_object* v___x_308_; lean_object* v___x_309_; lean_object* v___x_310_; lean_object* v___x_311_; lean_object* v___x_312_; lean_object* v___x_314_; 
v___x_308_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_309_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__3));
v___x_310_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4, &l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4_once, _init_l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__4);
v___x_311_ = l_Nat_reprFast(v_state__id_303_);
v___x_312_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_312_, 0, v___x_311_);
if (v_isShared_307_ == 0)
{
lean_ctor_set_tag(v___x_306_, 4);
lean_ctor_set(v___x_306_, 1, v___x_312_);
lean_ctor_set(v___x_306_, 0, v___x_310_);
v___x_314_ = v___x_306_;
goto v_reusejp_313_;
}
else
{
lean_object* v_reuseFailAlloc_345_; 
v_reuseFailAlloc_345_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_345_, 0, v___x_310_);
lean_ctor_set(v_reuseFailAlloc_345_, 1, v___x_312_);
v___x_314_ = v_reuseFailAlloc_345_;
goto v_reusejp_313_;
}
v_reusejp_313_:
{
uint8_t v___x_315_; lean_object* v___x_316_; lean_object* v___x_317_; lean_object* v___x_318_; lean_object* v___x_319_; lean_object* v___x_320_; lean_object* v___x_321_; lean_object* v___x_322_; lean_object* v___x_323_; lean_object* v___x_324_; lean_object* v___x_325_; lean_object* v___x_326_; lean_object* v___x_327_; lean_object* v___x_328_; lean_object* v___x_329_; lean_object* v___x_330_; lean_object* v___x_331_; lean_object* v___x_332_; lean_object* v___x_333_; lean_object* v___x_334_; lean_object* v___x_335_; lean_object* v___x_336_; lean_object* v___x_337_; lean_object* v___x_338_; lean_object* v___x_339_; lean_object* v___x_340_; lean_object* v___x_341_; lean_object* v___x_342_; lean_object* v___x_343_; lean_object* v___x_344_; 
v___x_315_ = 0;
v___x_316_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_316_, 0, v___x_314_);
lean_ctor_set_uint8(v___x_316_, sizeof(void*)*1, v___x_315_);
v___x_317_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_317_, 0, v___x_309_);
lean_ctor_set(v___x_317_, 1, v___x_316_);
v___x_318_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_319_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_319_, 0, v___x_317_);
lean_ctor_set(v___x_319_, 1, v___x_318_);
v___x_320_ = lean_box(1);
v___x_321_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_321_, 0, v___x_319_);
lean_ctor_set(v___x_321_, 1, v___x_320_);
v___x_322_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__6));
v___x_323_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_323_, 0, v___x_321_);
lean_ctor_set(v___x_323_, 1, v___x_322_);
v___x_324_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_324_, 0, v___x_323_);
lean_ctor_set(v___x_324_, 1, v___x_308_);
v___x_325_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7, &l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7);
v___x_326_ = l_Nat_reprFast(v_norm__sq_304_);
v___x_327_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_327_, 0, v___x_326_);
v___x_328_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_328_, 0, v___x_325_);
lean_ctor_set(v___x_328_, 1, v___x_327_);
v___x_329_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_329_, 0, v___x_328_);
lean_ctor_set_uint8(v___x_329_, sizeof(void*)*1, v___x_315_);
v___x_330_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_330_, 0, v___x_324_);
lean_ctor_set(v___x_330_, 1, v___x_329_);
v___x_331_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_331_, 0, v___x_330_);
lean_ctor_set(v___x_331_, 1, v___x_318_);
v___x_332_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_332_, 0, v___x_331_);
lean_ctor_set(v___x_332_, 1, v___x_320_);
v___x_333_ = ((lean_object*)(l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__9));
v___x_334_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_334_, 0, v___x_332_);
lean_ctor_set(v___x_334_, 1, v___x_333_);
v___x_335_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_335_, 0, v___x_334_);
lean_ctor_set(v___x_335_, 1, v___x_308_);
v___x_336_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_337_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_337_, 0, v___x_335_);
lean_ctor_set(v___x_337_, 1, v___x_336_);
v___x_338_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_339_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_340_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_340_, 0, v___x_339_);
lean_ctor_set(v___x_340_, 1, v___x_337_);
v___x_341_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_342_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_342_, 0, v___x_340_);
lean_ctor_set(v___x_342_, 1, v___x_341_);
v___x_343_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_343_, 0, v___x_338_);
lean_ctor_set(v___x_343_, 1, v___x_342_);
v___x_344_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_344_, 0, v___x_343_);
lean_ctor_set_uint8(v___x_344_, sizeof(void*)*1, v___x_315_);
return v___x_344_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr(lean_object* v_sig_347_, lean_object* v_x_348_, lean_object* v_prec_349_){
_start:
{
lean_object* v___x_350_; 
v___x_350_ = l_Polydim_Formal_instReprHypersphericalState_repr___redArg(v_x_348_);
return v___x_350_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState_repr___boxed(lean_object* v_sig_351_, lean_object* v_x_352_, lean_object* v_prec_353_){
_start:
{
lean_object* v_res_354_; 
v_res_354_ = l_Polydim_Formal_instReprHypersphericalState_repr(v_sig_351_, v_x_352_, v_prec_353_);
lean_dec(v_prec_353_);
lean_dec_ref(v_sig_351_);
return v_res_354_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprHypersphericalState(lean_object* v_sig_355_){
_start:
{
lean_object* v___x_356_; 
v___x_356_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprHypersphericalState_repr___boxed), 3, 1);
lean_closure_set(v___x_356_, 0, v_sig_355_);
return v___x_356_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner___redArg(lean_object* v_cl_357_, lean_object* v_00_u03c8_358_, lean_object* v_00_u03c6_359_){
_start:
{
lean_object* v_mul_360_; lean_object* v_rev_361_; lean_object* v_scalar__part_362_; lean_object* v_embed__vec_363_; lean_object* v___x_364_; lean_object* v___x_365_; lean_object* v___x_366_; lean_object* v___x_367_; lean_object* v___x_368_; 
v_mul_360_ = lean_ctor_get(v_cl_357_, 0);
lean_inc(v_mul_360_);
v_rev_361_ = lean_ctor_get(v_cl_357_, 2);
lean_inc(v_rev_361_);
v_scalar__part_362_ = lean_ctor_get(v_cl_357_, 3);
lean_inc_ref(v_scalar__part_362_);
v_embed__vec_363_ = lean_ctor_get(v_cl_357_, 4);
lean_inc_n(v_embed__vec_363_, 2);
lean_dec_ref(v_cl_357_);
v___x_364_ = lean_apply_1(v_embed__vec_363_, v_00_u03c8_358_);
v___x_365_ = lean_apply_1(v_embed__vec_363_, v_00_u03c6_359_);
v___x_366_ = lean_apply_1(v_rev_361_, v___x_365_);
v___x_367_ = lean_apply_2(v_mul_360_, v___x_364_, v___x_366_);
v___x_368_ = lean_apply_1(v_scalar__part_362_, v___x_367_);
return v___x_368_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner(lean_object* v_sig_369_, lean_object* v_cl_370_, lean_object* v_00_u03c8_371_, lean_object* v_00_u03c6_372_){
_start:
{
lean_object* v___x_373_; 
v___x_373_ = l_Polydim_Formal_CliffordAlgebra_inner___redArg(v_cl_370_, v_00_u03c8_371_, v_00_u03c6_372_);
return v___x_373_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_CliffordAlgebra_inner___boxed(lean_object* v_sig_374_, lean_object* v_cl_375_, lean_object* v_00_u03c8_376_, lean_object* v_00_u03c6_377_){
_start:
{
lean_object* v_res_378_; 
v_res_378_ = l_Polydim_Formal_CliffordAlgebra_inner(v_sig_374_, v_cl_375_, v_00_u03c8_376_, v_00_u03c6_377_);
lean_dec_ref(v_sig_374_);
return v_res_378_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_388_; lean_object* v___x_389_; 
v___x_388_ = lean_unsigned_to_nat(9u);
v___x_389_ = lean_nat_to_int(v___x_388_);
return v___x_389_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9(void){
_start:
{
lean_object* v___x_396_; lean_object* v___x_397_; 
v___x_396_ = lean_unsigned_to_nat(17u);
v___x_397_ = lean_nat_to_int(v___x_396_);
return v___x_397_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___redArg(lean_object* v_x_401_){
_start:
{
lean_object* v_grade_402_; lean_object* v_blade__norm__sq_403_; lean_object* v___x_405_; uint8_t v_isShared_406_; uint8_t v_isSharedCheck_451_; 
v_grade_402_ = lean_ctor_get(v_x_401_, 0);
v_blade__norm__sq_403_ = lean_ctor_get(v_x_401_, 1);
v_isSharedCheck_451_ = !lean_is_exclusive(v_x_401_);
if (v_isSharedCheck_451_ == 0)
{
v___x_405_ = v_x_401_;
v_isShared_406_ = v_isSharedCheck_451_;
goto v_resetjp_404_;
}
else
{
lean_inc(v_blade__norm__sq_403_);
lean_inc(v_grade_402_);
lean_dec(v_x_401_);
v___x_405_ = lean_box(0);
v_isShared_406_ = v_isSharedCheck_451_;
goto v_resetjp_404_;
}
v_resetjp_404_:
{
lean_object* v___x_407_; lean_object* v___x_408_; lean_object* v___x_409_; lean_object* v___x_410_; lean_object* v___x_411_; lean_object* v___x_413_; 
v___x_407_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_408_ = ((lean_object*)(l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__3));
v___x_409_ = lean_obj_once(&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4, &l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4_once, _init_l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__4);
v___x_410_ = l_Nat_reprFast(v_grade_402_);
v___x_411_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_411_, 0, v___x_410_);
if (v_isShared_406_ == 0)
{
lean_ctor_set_tag(v___x_405_, 4);
lean_ctor_set(v___x_405_, 1, v___x_411_);
lean_ctor_set(v___x_405_, 0, v___x_409_);
v___x_413_ = v___x_405_;
goto v_reusejp_412_;
}
else
{
lean_object* v_reuseFailAlloc_450_; 
v_reuseFailAlloc_450_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_450_, 0, v___x_409_);
lean_ctor_set(v_reuseFailAlloc_450_, 1, v___x_411_);
v___x_413_ = v_reuseFailAlloc_450_;
goto v_reusejp_412_;
}
v_reusejp_412_:
{
uint8_t v___x_414_; lean_object* v___x_415_; lean_object* v___x_416_; lean_object* v___x_417_; lean_object* v___x_418_; lean_object* v___x_419_; lean_object* v___x_420_; lean_object* v___x_421_; lean_object* v___x_422_; lean_object* v___x_423_; lean_object* v___x_424_; lean_object* v___x_425_; lean_object* v___x_426_; lean_object* v___x_427_; lean_object* v___x_428_; lean_object* v___x_429_; lean_object* v___x_430_; lean_object* v___x_431_; lean_object* v___x_432_; lean_object* v___x_433_; lean_object* v___x_434_; lean_object* v___x_435_; lean_object* v___x_436_; lean_object* v___x_437_; lean_object* v___x_438_; lean_object* v___x_439_; lean_object* v___x_440_; lean_object* v___x_441_; lean_object* v___x_442_; lean_object* v___x_443_; lean_object* v___x_444_; lean_object* v___x_445_; lean_object* v___x_446_; lean_object* v___x_447_; lean_object* v___x_448_; lean_object* v___x_449_; 
v___x_414_ = 0;
v___x_415_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_415_, 0, v___x_413_);
lean_ctor_set_uint8(v___x_415_, sizeof(void*)*1, v___x_414_);
v___x_416_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_416_, 0, v___x_408_);
lean_ctor_set(v___x_416_, 1, v___x_415_);
v___x_417_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_418_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_418_, 0, v___x_416_);
lean_ctor_set(v___x_418_, 1, v___x_417_);
v___x_419_ = lean_box(1);
v___x_420_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_420_, 0, v___x_418_);
lean_ctor_set(v___x_420_, 1, v___x_419_);
v___x_421_ = ((lean_object*)(l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__6));
v___x_422_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_422_, 0, v___x_420_);
lean_ctor_set(v___x_422_, 1, v___x_421_);
v___x_423_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_423_, 0, v___x_422_);
lean_ctor_set(v___x_423_, 1, v___x_407_);
v___x_424_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_425_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_425_, 0, v___x_423_);
lean_ctor_set(v___x_425_, 1, v___x_424_);
v___x_426_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_426_, 0, v___x_425_);
lean_ctor_set(v___x_426_, 1, v___x_417_);
v___x_427_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_427_, 0, v___x_426_);
lean_ctor_set(v___x_427_, 1, v___x_419_);
v___x_428_ = ((lean_object*)(l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__8));
v___x_429_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_429_, 0, v___x_427_);
lean_ctor_set(v___x_429_, 1, v___x_428_);
v___x_430_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_430_, 0, v___x_429_);
lean_ctor_set(v___x_430_, 1, v___x_407_);
v___x_431_ = lean_obj_once(&l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9, &l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9_once, _init_l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__9);
v___x_432_ = l_Nat_reprFast(v_blade__norm__sq_403_);
v___x_433_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_433_, 0, v___x_432_);
v___x_434_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_434_, 0, v___x_431_);
lean_ctor_set(v___x_434_, 1, v___x_433_);
v___x_435_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_435_, 0, v___x_434_);
lean_ctor_set_uint8(v___x_435_, sizeof(void*)*1, v___x_414_);
v___x_436_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_436_, 0, v___x_430_);
lean_ctor_set(v___x_436_, 1, v___x_435_);
v___x_437_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_437_, 0, v___x_436_);
lean_ctor_set(v___x_437_, 1, v___x_417_);
v___x_438_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_438_, 0, v___x_437_);
lean_ctor_set(v___x_438_, 1, v___x_419_);
v___x_439_ = ((lean_object*)(l_Polydim_Formal_instReprCliffordBlade_repr___redArg___closed__11));
v___x_440_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_440_, 0, v___x_438_);
lean_ctor_set(v___x_440_, 1, v___x_439_);
v___x_441_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_441_, 0, v___x_440_);
lean_ctor_set(v___x_441_, 1, v___x_407_);
v___x_442_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_442_, 0, v___x_441_);
lean_ctor_set(v___x_442_, 1, v___x_424_);
v___x_443_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_444_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_445_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_445_, 0, v___x_444_);
lean_ctor_set(v___x_445_, 1, v___x_442_);
v___x_446_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_447_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_447_, 0, v___x_445_);
lean_ctor_set(v___x_447_, 1, v___x_446_);
v___x_448_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_448_, 0, v___x_443_);
lean_ctor_set(v___x_448_, 1, v___x_447_);
v___x_449_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_449_, 0, v___x_448_);
lean_ctor_set_uint8(v___x_449_, sizeof(void*)*1, v___x_414_);
return v___x_449_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr(lean_object* v_sig_452_, lean_object* v_k_453_, lean_object* v_x_454_, lean_object* v_prec_455_){
_start:
{
lean_object* v___x_456_; 
v___x_456_ = l_Polydim_Formal_instReprCliffordBlade_repr___redArg(v_x_454_);
return v___x_456_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade_repr___boxed(lean_object* v_sig_457_, lean_object* v_k_458_, lean_object* v_x_459_, lean_object* v_prec_460_){
_start:
{
lean_object* v_res_461_; 
v_res_461_ = l_Polydim_Formal_instReprCliffordBlade_repr(v_sig_457_, v_k_458_, v_x_459_, v_prec_460_);
lean_dec(v_prec_460_);
lean_dec(v_k_458_);
lean_dec_ref(v_sig_457_);
return v_res_461_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprCliffordBlade(lean_object* v_sig_462_, lean_object* v_k_463_){
_start:
{
lean_object* v___x_464_; 
v___x_464_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprCliffordBlade_repr___boxed), 4, 2);
lean_closure_set(v___x_464_, 0, v_sig_462_);
lean_closure_set(v___x_464_, 1, v_k_463_);
return v___x_464_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9(void){
_start:
{
lean_object* v___x_489_; lean_object* v___x_490_; 
v___x_489_ = lean_unsigned_to_nat(7u);
v___x_490_ = lean_nat_to_int(v___x_489_);
return v___x_490_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12(void){
_start:
{
lean_object* v___x_494_; lean_object* v___x_495_; 
v___x_494_ = lean_unsigned_to_nat(8u);
v___x_495_ = lean_nat_to_int(v___x_494_);
return v___x_495_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr___redArg(lean_object* v_x_502_){
_start:
{
lean_object* v_H__X_503_; lean_object* v_I__XY_504_; lean_object* v___x_506_; uint8_t v_isShared_507_; uint8_t v_isSharedCheck_552_; 
v_H__X_503_ = lean_ctor_get(v_x_502_, 0);
v_I__XY_504_ = lean_ctor_get(v_x_502_, 1);
v_isSharedCheck_552_ = !lean_is_exclusive(v_x_502_);
if (v_isSharedCheck_552_ == 0)
{
v___x_506_ = v_x_502_;
v_isShared_507_ = v_isSharedCheck_552_;
goto v_resetjp_505_;
}
else
{
lean_inc(v_I__XY_504_);
lean_inc(v_H__X_503_);
lean_dec(v_x_502_);
v___x_506_ = lean_box(0);
v_isShared_507_ = v_isSharedCheck_552_;
goto v_resetjp_505_;
}
v_resetjp_505_:
{
lean_object* v___x_508_; lean_object* v___x_509_; lean_object* v___x_510_; lean_object* v___x_511_; lean_object* v___x_512_; lean_object* v___x_513_; lean_object* v___x_514_; lean_object* v___x_515_; lean_object* v___x_517_; 
v___x_508_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_509_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_510_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_511_ = lean_box(1);
v___x_512_ = ((lean_object*)(l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__8));
v___x_513_ = lean_obj_once(&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9, &l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9_once, _init_l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__9);
v___x_514_ = l_Nat_reprFast(v_H__X_503_);
v___x_515_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_515_, 0, v___x_514_);
if (v_isShared_507_ == 0)
{
lean_ctor_set_tag(v___x_506_, 4);
lean_ctor_set(v___x_506_, 1, v___x_515_);
lean_ctor_set(v___x_506_, 0, v___x_513_);
v___x_517_ = v___x_506_;
goto v_reusejp_516_;
}
else
{
lean_object* v_reuseFailAlloc_551_; 
v_reuseFailAlloc_551_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_551_, 0, v___x_513_);
lean_ctor_set(v_reuseFailAlloc_551_, 1, v___x_515_);
v___x_517_ = v_reuseFailAlloc_551_;
goto v_reusejp_516_;
}
v_reusejp_516_:
{
uint8_t v___x_518_; lean_object* v___x_519_; lean_object* v___x_520_; lean_object* v___x_521_; lean_object* v___x_522_; lean_object* v___x_523_; lean_object* v___x_524_; lean_object* v___x_525_; lean_object* v___x_526_; lean_object* v___x_527_; lean_object* v___x_528_; lean_object* v___x_529_; lean_object* v___x_530_; lean_object* v___x_531_; lean_object* v___x_532_; lean_object* v___x_533_; lean_object* v___x_534_; lean_object* v___x_535_; lean_object* v___x_536_; lean_object* v___x_537_; lean_object* v___x_538_; lean_object* v___x_539_; lean_object* v___x_540_; lean_object* v___x_541_; lean_object* v___x_542_; lean_object* v___x_543_; lean_object* v___x_544_; lean_object* v___x_545_; lean_object* v___x_546_; lean_object* v___x_547_; lean_object* v___x_548_; lean_object* v___x_549_; lean_object* v___x_550_; 
v___x_518_ = 0;
v___x_519_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_519_, 0, v___x_517_);
lean_ctor_set_uint8(v___x_519_, sizeof(void*)*1, v___x_518_);
v___x_520_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_520_, 0, v___x_512_);
lean_ctor_set(v___x_520_, 1, v___x_519_);
v___x_521_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_521_, 0, v___x_520_);
lean_ctor_set(v___x_521_, 1, v___x_510_);
v___x_522_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_522_, 0, v___x_521_);
lean_ctor_set(v___x_522_, 1, v___x_511_);
v___x_523_ = ((lean_object*)(l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__11));
v___x_524_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_524_, 0, v___x_522_);
lean_ctor_set(v___x_524_, 1, v___x_523_);
v___x_525_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_525_, 0, v___x_524_);
lean_ctor_set(v___x_525_, 1, v___x_508_);
v___x_526_ = lean_obj_once(&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12, &l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12_once, _init_l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12);
v___x_527_ = l_Nat_reprFast(v_I__XY_504_);
v___x_528_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_528_, 0, v___x_527_);
v___x_529_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_529_, 0, v___x_526_);
lean_ctor_set(v___x_529_, 1, v___x_528_);
v___x_530_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_530_, 0, v___x_529_);
lean_ctor_set_uint8(v___x_530_, sizeof(void*)*1, v___x_518_);
v___x_531_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_531_, 0, v___x_525_);
lean_ctor_set(v___x_531_, 1, v___x_530_);
v___x_532_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_532_, 0, v___x_531_);
lean_ctor_set(v___x_532_, 1, v___x_510_);
v___x_533_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_533_, 0, v___x_532_);
lean_ctor_set(v___x_533_, 1, v___x_511_);
v___x_534_ = ((lean_object*)(l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__14));
v___x_535_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_535_, 0, v___x_533_);
lean_ctor_set(v___x_535_, 1, v___x_534_);
v___x_536_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_536_, 0, v___x_535_);
lean_ctor_set(v___x_536_, 1, v___x_508_);
v___x_537_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_537_, 0, v___x_536_);
lean_ctor_set(v___x_537_, 1, v___x_509_);
v___x_538_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_538_, 0, v___x_537_);
lean_ctor_set(v___x_538_, 1, v___x_510_);
v___x_539_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_539_, 0, v___x_538_);
lean_ctor_set(v___x_539_, 1, v___x_511_);
v___x_540_ = ((lean_object*)(l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__16));
v___x_541_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_541_, 0, v___x_539_);
lean_ctor_set(v___x_541_, 1, v___x_540_);
v___x_542_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_542_, 0, v___x_541_);
lean_ctor_set(v___x_542_, 1, v___x_508_);
v___x_543_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_543_, 0, v___x_542_);
lean_ctor_set(v___x_543_, 1, v___x_509_);
v___x_544_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_545_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_546_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_546_, 0, v___x_545_);
lean_ctor_set(v___x_546_, 1, v___x_543_);
v___x_547_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_548_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_548_, 0, v___x_546_);
lean_ctor_set(v___x_548_, 1, v___x_547_);
v___x_549_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_549_, 0, v___x_544_);
lean_ctor_set(v___x_549_, 1, v___x_548_);
v___x_550_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_550_, 0, v___x_549_);
lean_ctor_set_uint8(v___x_550_, sizeof(void*)*1, v___x_518_);
return v___x_550_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr(lean_object* v_D_553_, lean_object* v_x_554_, lean_object* v_prec_555_){
_start:
{
lean_object* v___x_556_; 
v___x_556_ = l_Polydim_Formal_instReprLatentTensor_repr___redArg(v_x_554_);
return v___x_556_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor_repr___boxed(lean_object* v_D_557_, lean_object* v_x_558_, lean_object* v_prec_559_){
_start:
{
lean_object* v_res_560_; 
v_res_560_ = l_Polydim_Formal_instReprLatentTensor_repr(v_D_557_, v_x_558_, v_prec_559_);
lean_dec(v_prec_559_);
lean_dec(v_D_557_);
return v_res_560_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprLatentTensor(lean_object* v_D_561_){
_start:
{
lean_object* v___x_562_; 
v___x_562_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprLatentTensor_repr___boxed), 3, 1);
lean_closure_set(v___x_562_, 0, v_D_561_);
return v___x_562_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12(void){
_start:
{
lean_object* v___x_584_; lean_object* v___x_585_; 
v___x_584_ = lean_unsigned_to_nat(18u);
v___x_585_ = lean_nat_to_int(v___x_584_);
return v___x_585_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg(lean_object* v_x_598_){
_start:
{
lean_object* v_vocab__size_599_; lean_object* v_seq__length_600_; lean_object* v_bits__per__token_601_; lean_object* v_C__token_602_; lean_object* v___x_603_; lean_object* v___x_604_; lean_object* v___x_605_; lean_object* v___x_606_; lean_object* v___x_607_; lean_object* v___x_608_; uint8_t v___x_609_; lean_object* v___x_610_; lean_object* v___x_611_; lean_object* v___x_612_; lean_object* v___x_613_; lean_object* v___x_614_; lean_object* v___x_615_; lean_object* v___x_616_; lean_object* v___x_617_; lean_object* v___x_618_; lean_object* v___x_619_; lean_object* v___x_620_; lean_object* v___x_621_; lean_object* v___x_622_; lean_object* v___x_623_; lean_object* v___x_624_; lean_object* v___x_625_; lean_object* v___x_626_; lean_object* v___x_627_; lean_object* v___x_628_; lean_object* v___x_629_; lean_object* v___x_630_; lean_object* v___x_631_; lean_object* v___x_632_; lean_object* v___x_633_; lean_object* v___x_634_; lean_object* v___x_635_; lean_object* v___x_636_; lean_object* v___x_637_; lean_object* v___x_638_; lean_object* v___x_639_; lean_object* v___x_640_; lean_object* v___x_641_; lean_object* v___x_642_; lean_object* v___x_643_; lean_object* v___x_644_; lean_object* v___x_645_; lean_object* v___x_646_; lean_object* v___x_647_; lean_object* v___x_648_; lean_object* v___x_649_; lean_object* v___x_650_; lean_object* v___x_651_; lean_object* v___x_652_; lean_object* v___x_653_; lean_object* v___x_654_; lean_object* v___x_655_; lean_object* v___x_656_; lean_object* v___x_657_; lean_object* v___x_658_; lean_object* v___x_659_; lean_object* v___x_660_; lean_object* v___x_661_; lean_object* v___x_662_; lean_object* v___x_663_; lean_object* v___x_664_; lean_object* v___x_665_; lean_object* v___x_666_; lean_object* v___x_667_; lean_object* v___x_668_; lean_object* v___x_669_; lean_object* v___x_670_; lean_object* v___x_671_; lean_object* v___x_672_; lean_object* v___x_673_; lean_object* v___x_674_; lean_object* v___x_675_; lean_object* v___x_676_; lean_object* v___x_677_; lean_object* v___x_678_; lean_object* v___x_679_; lean_object* v___x_680_; lean_object* v___x_681_; lean_object* v___x_682_; lean_object* v___x_683_; 
v_vocab__size_599_ = lean_ctor_get(v_x_598_, 0);
lean_inc(v_vocab__size_599_);
v_seq__length_600_ = lean_ctor_get(v_x_598_, 1);
lean_inc(v_seq__length_600_);
v_bits__per__token_601_ = lean_ctor_get(v_x_598_, 2);
lean_inc(v_bits__per__token_601_);
v_C__token_602_ = lean_ctor_get(v_x_598_, 3);
lean_inc(v_C__token_602_);
lean_dec_ref(v_x_598_);
v___x_603_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_604_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__3));
v___x_605_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7, &l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprHypersphere_repr___redArg___closed__7);
v___x_606_ = l_Nat_reprFast(v_vocab__size_599_);
v___x_607_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_607_, 0, v___x_606_);
v___x_608_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_608_, 0, v___x_605_);
lean_ctor_set(v___x_608_, 1, v___x_607_);
v___x_609_ = 0;
v___x_610_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_610_, 0, v___x_608_);
lean_ctor_set_uint8(v___x_610_, sizeof(void*)*1, v___x_609_);
v___x_611_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_611_, 0, v___x_604_);
lean_ctor_set(v___x_611_, 1, v___x_610_);
v___x_612_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_613_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_613_, 0, v___x_611_);
lean_ctor_set(v___x_613_, 1, v___x_612_);
v___x_614_ = lean_box(1);
v___x_615_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_615_, 0, v___x_613_);
lean_ctor_set(v___x_615_, 1, v___x_614_);
v___x_616_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__5));
v___x_617_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_617_, 0, v___x_615_);
lean_ctor_set(v___x_617_, 1, v___x_616_);
v___x_618_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_618_, 0, v___x_617_);
lean_ctor_set(v___x_618_, 1, v___x_603_);
v___x_619_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_620_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_620_, 0, v___x_618_);
lean_ctor_set(v___x_620_, 1, v___x_619_);
v___x_621_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_621_, 0, v___x_620_);
lean_ctor_set(v___x_621_, 1, v___x_612_);
v___x_622_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_622_, 0, v___x_621_);
lean_ctor_set(v___x_622_, 1, v___x_614_);
v___x_623_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__7));
v___x_624_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_624_, 0, v___x_622_);
lean_ctor_set(v___x_624_, 1, v___x_623_);
v___x_625_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_625_, 0, v___x_624_);
lean_ctor_set(v___x_625_, 1, v___x_603_);
v___x_626_ = l_Nat_reprFast(v_seq__length_600_);
v___x_627_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_627_, 0, v___x_626_);
v___x_628_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_628_, 0, v___x_605_);
lean_ctor_set(v___x_628_, 1, v___x_627_);
v___x_629_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_629_, 0, v___x_628_);
lean_ctor_set_uint8(v___x_629_, sizeof(void*)*1, v___x_609_);
v___x_630_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_630_, 0, v___x_625_);
lean_ctor_set(v___x_630_, 1, v___x_629_);
v___x_631_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_631_, 0, v___x_630_);
lean_ctor_set(v___x_631_, 1, v___x_612_);
v___x_632_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_632_, 0, v___x_631_);
lean_ctor_set(v___x_632_, 1, v___x_614_);
v___x_633_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__9));
v___x_634_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_634_, 0, v___x_632_);
lean_ctor_set(v___x_634_, 1, v___x_633_);
v___x_635_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_635_, 0, v___x_634_);
lean_ctor_set(v___x_635_, 1, v___x_603_);
v___x_636_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_636_, 0, v___x_635_);
lean_ctor_set(v___x_636_, 1, v___x_619_);
v___x_637_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_637_, 0, v___x_636_);
lean_ctor_set(v___x_637_, 1, v___x_612_);
v___x_638_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_638_, 0, v___x_637_);
lean_ctor_set(v___x_638_, 1, v___x_614_);
v___x_639_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__11));
v___x_640_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_640_, 0, v___x_638_);
lean_ctor_set(v___x_640_, 1, v___x_639_);
v___x_641_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_641_, 0, v___x_640_);
lean_ctor_set(v___x_641_, 1, v___x_603_);
v___x_642_ = lean_obj_once(&l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12, &l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12_once, _init_l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__12);
v___x_643_ = l_Nat_reprFast(v_bits__per__token_601_);
v___x_644_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_644_, 0, v___x_643_);
v___x_645_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_645_, 0, v___x_642_);
lean_ctor_set(v___x_645_, 1, v___x_644_);
v___x_646_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_646_, 0, v___x_645_);
lean_ctor_set_uint8(v___x_646_, sizeof(void*)*1, v___x_609_);
v___x_647_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_647_, 0, v___x_641_);
lean_ctor_set(v___x_647_, 1, v___x_646_);
v___x_648_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_648_, 0, v___x_647_);
lean_ctor_set(v___x_648_, 1, v___x_612_);
v___x_649_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_649_, 0, v___x_648_);
lean_ctor_set(v___x_649_, 1, v___x_614_);
v___x_650_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__14));
v___x_651_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_651_, 0, v___x_649_);
lean_ctor_set(v___x_651_, 1, v___x_650_);
v___x_652_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_652_, 0, v___x_651_);
lean_ctor_set(v___x_652_, 1, v___x_603_);
v___x_653_ = lean_obj_once(&l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7, &l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprHypersphericalState_repr___redArg___closed__7);
v___x_654_ = l_Nat_reprFast(v_C__token_602_);
v___x_655_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_655_, 0, v___x_654_);
v___x_656_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_656_, 0, v___x_653_);
lean_ctor_set(v___x_656_, 1, v___x_655_);
v___x_657_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_657_, 0, v___x_656_);
lean_ctor_set_uint8(v___x_657_, sizeof(void*)*1, v___x_609_);
v___x_658_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_658_, 0, v___x_652_);
lean_ctor_set(v___x_658_, 1, v___x_657_);
v___x_659_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_659_, 0, v___x_658_);
lean_ctor_set(v___x_659_, 1, v___x_612_);
v___x_660_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_660_, 0, v___x_659_);
lean_ctor_set(v___x_660_, 1, v___x_614_);
v___x_661_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__16));
v___x_662_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_662_, 0, v___x_660_);
lean_ctor_set(v___x_662_, 1, v___x_661_);
v___x_663_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_663_, 0, v___x_662_);
lean_ctor_set(v___x_663_, 1, v___x_603_);
v___x_664_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_664_, 0, v___x_663_);
lean_ctor_set(v___x_664_, 1, v___x_619_);
v___x_665_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_665_, 0, v___x_664_);
lean_ctor_set(v___x_665_, 1, v___x_612_);
v___x_666_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_666_, 0, v___x_665_);
lean_ctor_set(v___x_666_, 1, v___x_614_);
v___x_667_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__18));
v___x_668_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_668_, 0, v___x_666_);
lean_ctor_set(v___x_668_, 1, v___x_667_);
v___x_669_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_669_, 0, v___x_668_);
lean_ctor_set(v___x_669_, 1, v___x_603_);
v___x_670_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_670_, 0, v___x_669_);
lean_ctor_set(v___x_670_, 1, v___x_619_);
v___x_671_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_671_, 0, v___x_670_);
lean_ctor_set(v___x_671_, 1, v___x_612_);
v___x_672_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_672_, 0, v___x_671_);
lean_ctor_set(v___x_672_, 1, v___x_614_);
v___x_673_ = ((lean_object*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg___closed__20));
v___x_674_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_674_, 0, v___x_672_);
lean_ctor_set(v___x_674_, 1, v___x_673_);
v___x_675_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_675_, 0, v___x_674_);
lean_ctor_set(v___x_675_, 1, v___x_603_);
v___x_676_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_676_, 0, v___x_675_);
lean_ctor_set(v___x_676_, 1, v___x_619_);
v___x_677_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_678_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_679_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_679_, 0, v___x_678_);
lean_ctor_set(v___x_679_, 1, v___x_676_);
v___x_680_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_681_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_681_, 0, v___x_679_);
lean_ctor_set(v___x_681_, 1, v___x_680_);
v___x_682_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_682_, 0, v___x_677_);
lean_ctor_set(v___x_682_, 1, v___x_681_);
v___x_683_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_683_, 0, v___x_682_);
lean_ctor_set_uint8(v___x_683_, sizeof(void*)*1, v___x_609_);
return v___x_683_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr(lean_object* v_D_684_, lean_object* v_X_685_, lean_object* v_x_686_, lean_object* v_prec_687_){
_start:
{
lean_object* v___x_688_; 
v___x_688_ = l_Polydim_Formal_instReprDiscreteTokenizer_repr___redArg(v_x_686_);
return v___x_688_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer_repr___boxed(lean_object* v_D_689_, lean_object* v_X_690_, lean_object* v_x_691_, lean_object* v_prec_692_){
_start:
{
lean_object* v_res_693_; 
v_res_693_ = l_Polydim_Formal_instReprDiscreteTokenizer_repr(v_D_689_, v_X_690_, v_x_691_, v_prec_692_);
lean_dec(v_prec_692_);
lean_dec_ref(v_X_690_);
lean_dec(v_D_689_);
return v_res_693_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprDiscreteTokenizer(lean_object* v_D_694_, lean_object* v_X_695_){
_start:
{
lean_object* v___x_696_; 
v___x_696_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprDiscreteTokenizer_repr___boxed), 4, 2);
lean_closure_set(v___x_696_, 0, v_D_694_);
lean_closure_set(v___x_696_, 1, v_X_695_);
return v___x_696_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___redArg(lean_object* v_x_712_){
_start:
{
lean_object* v___x_713_; lean_object* v___x_714_; lean_object* v___x_715_; lean_object* v___x_716_; lean_object* v___x_717_; lean_object* v___x_718_; uint8_t v___x_719_; lean_object* v___x_720_; lean_object* v___x_721_; lean_object* v___x_722_; lean_object* v___x_723_; lean_object* v___x_724_; lean_object* v___x_725_; lean_object* v___x_726_; lean_object* v___x_727_; lean_object* v___x_728_; lean_object* v___x_729_; lean_object* v___x_730_; lean_object* v___x_731_; lean_object* v___x_732_; lean_object* v___x_733_; lean_object* v___x_734_; lean_object* v___x_735_; lean_object* v___x_736_; lean_object* v___x_737_; lean_object* v___x_738_; lean_object* v___x_739_; lean_object* v___x_740_; lean_object* v___x_741_; lean_object* v___x_742_; lean_object* v___x_743_; 
v___x_713_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_714_ = ((lean_object*)(l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__3));
v___x_715_ = lean_obj_once(&l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12, &l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12_once, _init_l_Polydim_Formal_instReprLatentTensor_repr___redArg___closed__12);
v___x_716_ = l_Nat_reprFast(v_x_712_);
v___x_717_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_717_, 0, v___x_716_);
v___x_718_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_718_, 0, v___x_715_);
lean_ctor_set(v___x_718_, 1, v___x_717_);
v___x_719_ = 0;
v___x_720_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_720_, 0, v___x_718_);
lean_ctor_set_uint8(v___x_720_, sizeof(void*)*1, v___x_719_);
v___x_721_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_721_, 0, v___x_714_);
lean_ctor_set(v___x_721_, 1, v___x_720_);
v___x_722_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_723_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_723_, 0, v___x_721_);
lean_ctor_set(v___x_723_, 1, v___x_722_);
v___x_724_ = lean_box(1);
v___x_725_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_725_, 0, v___x_723_);
lean_ctor_set(v___x_725_, 1, v___x_724_);
v___x_726_ = ((lean_object*)(l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__5));
v___x_727_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_727_, 0, v___x_725_);
lean_ctor_set(v___x_727_, 1, v___x_726_);
v___x_728_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_728_, 0, v___x_727_);
lean_ctor_set(v___x_728_, 1, v___x_713_);
v___x_729_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_730_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_730_, 0, v___x_728_);
lean_ctor_set(v___x_730_, 1, v___x_729_);
v___x_731_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_731_, 0, v___x_730_);
lean_ctor_set(v___x_731_, 1, v___x_722_);
v___x_732_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_732_, 0, v___x_731_);
lean_ctor_set(v___x_732_, 1, v___x_724_);
v___x_733_ = ((lean_object*)(l_Polydim_Formal_instReprTokenizedChannel_repr___redArg___closed__7));
v___x_734_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_734_, 0, v___x_732_);
lean_ctor_set(v___x_734_, 1, v___x_733_);
v___x_735_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_735_, 0, v___x_734_);
lean_ctor_set(v___x_735_, 1, v___x_713_);
v___x_736_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_736_, 0, v___x_735_);
lean_ctor_set(v___x_736_, 1, v___x_729_);
v___x_737_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_738_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_739_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_739_, 0, v___x_738_);
lean_ctor_set(v___x_739_, 1, v___x_736_);
v___x_740_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_741_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_741_, 0, v___x_739_);
lean_ctor_set(v___x_741_, 1, v___x_740_);
v___x_742_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_742_, 0, v___x_737_);
lean_ctor_set(v___x_742_, 1, v___x_741_);
v___x_743_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_743_, 0, v___x_742_);
lean_ctor_set_uint8(v___x_743_, sizeof(void*)*1, v___x_719_);
return v___x_743_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr(lean_object* v_D_744_, lean_object* v_X_745_, lean_object* v_tok_746_, lean_object* v_x_747_, lean_object* v_prec_748_){
_start:
{
lean_object* v___x_749_; 
v___x_749_ = l_Polydim_Formal_instReprTokenizedChannel_repr___redArg(v_x_747_);
return v___x_749_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel_repr___boxed(lean_object* v_D_750_, lean_object* v_X_751_, lean_object* v_tok_752_, lean_object* v_x_753_, lean_object* v_prec_754_){
_start:
{
lean_object* v_res_755_; 
v_res_755_ = l_Polydim_Formal_instReprTokenizedChannel_repr(v_D_750_, v_X_751_, v_tok_752_, v_x_753_, v_prec_754_);
lean_dec(v_prec_754_);
lean_dec_ref(v_tok_752_);
lean_dec_ref(v_X_751_);
lean_dec(v_D_750_);
return v_res_755_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprTokenizedChannel(lean_object* v_D_756_, lean_object* v_X_757_, lean_object* v_tok_758_){
_start:
{
lean_object* v___x_759_; 
v___x_759_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprTokenizedChannel_repr___boxed), 5, 3);
lean_closure_set(v___x_759_, 0, v_D_756_);
lean_closure_set(v___x_759_, 1, v_X_757_);
lean_closure_set(v___x_759_, 2, v_tok_758_);
return v___x_759_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_769_; lean_object* v___x_770_; 
v___x_769_ = lean_unsigned_to_nat(20u);
v___x_770_ = lean_nat_to_int(v___x_769_);
return v___x_770_;
}
}
static lean_object* _init_l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_774_; lean_object* v___x_775_; 
v___x_774_ = lean_unsigned_to_nat(23u);
v___x_775_ = lean_nat_to_int(v___x_774_);
return v___x_775_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg(lean_object* v_x_782_){
_start:
{
lean_object* v_mutual__info__pmtp_783_; lean_object* v_entropy__destruction_784_; lean_object* v___x_786_; uint8_t v_isShared_787_; uint8_t v_isSharedCheck_832_; 
v_mutual__info__pmtp_783_ = lean_ctor_get(v_x_782_, 0);
v_entropy__destruction_784_ = lean_ctor_get(v_x_782_, 1);
v_isSharedCheck_832_ = !lean_is_exclusive(v_x_782_);
if (v_isSharedCheck_832_ == 0)
{
v___x_786_ = v_x_782_;
v_isShared_787_ = v_isSharedCheck_832_;
goto v_resetjp_785_;
}
else
{
lean_inc(v_entropy__destruction_784_);
lean_inc(v_mutual__info__pmtp_783_);
lean_dec(v_x_782_);
v___x_786_ = lean_box(0);
v_isShared_787_ = v_isSharedCheck_832_;
goto v_resetjp_785_;
}
v_resetjp_785_:
{
lean_object* v___x_788_; lean_object* v___x_789_; lean_object* v___x_790_; lean_object* v___x_791_; lean_object* v___x_792_; lean_object* v___x_794_; 
v___x_788_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__5));
v___x_789_ = ((lean_object*)(l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__3));
v___x_790_ = lean_obj_once(&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4, &l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4_once, _init_l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__4);
v___x_791_ = l_Nat_reprFast(v_mutual__info__pmtp_783_);
v___x_792_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_792_, 0, v___x_791_);
if (v_isShared_787_ == 0)
{
lean_ctor_set_tag(v___x_786_, 4);
lean_ctor_set(v___x_786_, 1, v___x_792_);
lean_ctor_set(v___x_786_, 0, v___x_790_);
v___x_794_ = v___x_786_;
goto v_reusejp_793_;
}
else
{
lean_object* v_reuseFailAlloc_831_; 
v_reuseFailAlloc_831_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_831_, 0, v___x_790_);
lean_ctor_set(v_reuseFailAlloc_831_, 1, v___x_792_);
v___x_794_ = v_reuseFailAlloc_831_;
goto v_reusejp_793_;
}
v_reusejp_793_:
{
uint8_t v___x_795_; lean_object* v___x_796_; lean_object* v___x_797_; lean_object* v___x_798_; lean_object* v___x_799_; lean_object* v___x_800_; lean_object* v___x_801_; lean_object* v___x_802_; lean_object* v___x_803_; lean_object* v___x_804_; lean_object* v___x_805_; lean_object* v___x_806_; lean_object* v___x_807_; lean_object* v___x_808_; lean_object* v___x_809_; lean_object* v___x_810_; lean_object* v___x_811_; lean_object* v___x_812_; lean_object* v___x_813_; lean_object* v___x_814_; lean_object* v___x_815_; lean_object* v___x_816_; lean_object* v___x_817_; lean_object* v___x_818_; lean_object* v___x_819_; lean_object* v___x_820_; lean_object* v___x_821_; lean_object* v___x_822_; lean_object* v___x_823_; lean_object* v___x_824_; lean_object* v___x_825_; lean_object* v___x_826_; lean_object* v___x_827_; lean_object* v___x_828_; lean_object* v___x_829_; lean_object* v___x_830_; 
v___x_795_ = 0;
v___x_796_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_796_, 0, v___x_794_);
lean_ctor_set_uint8(v___x_796_, sizeof(void*)*1, v___x_795_);
v___x_797_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_797_, 0, v___x_789_);
lean_ctor_set(v___x_797_, 1, v___x_796_);
v___x_798_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__9));
v___x_799_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_799_, 0, v___x_797_);
lean_ctor_set(v___x_799_, 1, v___x_798_);
v___x_800_ = lean_box(1);
v___x_801_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_801_, 0, v___x_799_);
lean_ctor_set(v___x_801_, 1, v___x_800_);
v___x_802_ = ((lean_object*)(l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__6));
v___x_803_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_803_, 0, v___x_801_);
lean_ctor_set(v___x_803_, 1, v___x_802_);
v___x_804_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_804_, 0, v___x_803_);
lean_ctor_set(v___x_804_, 1, v___x_788_);
v___x_805_ = lean_obj_once(&l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7, &l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7_once, _init_l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__7);
v___x_806_ = l_Nat_reprFast(v_entropy__destruction_784_);
v___x_807_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_807_, 0, v___x_806_);
v___x_808_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_808_, 0, v___x_805_);
lean_ctor_set(v___x_808_, 1, v___x_807_);
v___x_809_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_809_, 0, v___x_808_);
lean_ctor_set_uint8(v___x_809_, sizeof(void*)*1, v___x_795_);
v___x_810_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_810_, 0, v___x_804_);
lean_ctor_set(v___x_810_, 1, v___x_809_);
v___x_811_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_811_, 0, v___x_810_);
lean_ctor_set(v___x_811_, 1, v___x_798_);
v___x_812_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_812_, 0, v___x_811_);
lean_ctor_set(v___x_812_, 1, v___x_800_);
v___x_813_ = ((lean_object*)(l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__9));
v___x_814_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_814_, 0, v___x_812_);
lean_ctor_set(v___x_814_, 1, v___x_813_);
v___x_815_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_815_, 0, v___x_814_);
lean_ctor_set(v___x_815_, 1, v___x_788_);
v___x_816_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__15));
v___x_817_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_817_, 0, v___x_815_);
lean_ctor_set(v___x_817_, 1, v___x_816_);
v___x_818_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_818_, 0, v___x_817_);
lean_ctor_set(v___x_818_, 1, v___x_798_);
v___x_819_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_819_, 0, v___x_818_);
lean_ctor_set(v___x_819_, 1, v___x_800_);
v___x_820_ = ((lean_object*)(l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg___closed__11));
v___x_821_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_821_, 0, v___x_819_);
lean_ctor_set(v___x_821_, 1, v___x_820_);
v___x_822_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_822_, 0, v___x_821_);
lean_ctor_set(v___x_822_, 1, v___x_788_);
v___x_823_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_823_, 0, v___x_822_);
lean_ctor_set(v___x_823_, 1, v___x_816_);
v___x_824_ = lean_obj_once(&l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18, &l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18_once, _init_l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__18);
v___x_825_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__19));
v___x_826_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_826_, 0, v___x_825_);
lean_ctor_set(v___x_826_, 1, v___x_823_);
v___x_827_ = ((lean_object*)(l_Polydim_Formal_instReprMetricSignature_repr___redArg___closed__20));
v___x_828_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_828_, 0, v___x_826_);
lean_ctor_set(v___x_828_, 1, v___x_827_);
v___x_829_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_829_, 0, v___x_824_);
lean_ctor_set(v___x_829_, 1, v___x_828_);
v___x_830_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_830_, 0, v___x_829_);
lean_ctor_set_uint8(v___x_830_, sizeof(void*)*1, v___x_795_);
return v___x_830_;
}
}
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr(lean_object* v_D_833_, lean_object* v_X_834_, lean_object* v_x_835_, lean_object* v_prec_836_){
_start:
{
lean_object* v___x_837_; 
v___x_837_ = l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___redArg(v_x_835_);
return v___x_837_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___boxed(lean_object* v_D_838_, lean_object* v_X_839_, lean_object* v_x_840_, lean_object* v_prec_841_){
_start:
{
lean_object* v_res_842_; 
v_res_842_ = l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr(v_D_838_, v_X_839_, v_x_840_, v_prec_841_);
lean_dec(v_prec_841_);
lean_dec_ref(v_X_839_);
lean_dec(v_D_838_);
return v_res_842_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_instReprPmtpSharedMemoryChannel(lean_object* v_D_843_, lean_object* v_X_844_){
_start:
{
lean_object* v___x_845_; 
v___x_845_ = lean_alloc_closure((void*)(l_Polydim_Formal_instReprPmtpSharedMemoryChannel_repr___boxed), 4, 2);
lean_closure_set(v___x_845_, 0, v_D_843_);
lean_closure_set(v___x_845_, 1, v_X_844_);
return v___x_845_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___redArg(lean_object* v_X_846_, lean_object* v_tok_847_){
_start:
{
lean_object* v_H__X_848_; lean_object* v_C__token_849_; lean_object* v___x_850_; 
v_H__X_848_ = lean_ctor_get(v_X_846_, 0);
v_C__token_849_ = lean_ctor_get(v_tok_847_, 3);
v___x_850_ = lean_nat_sub(v_H__X_848_, v_C__token_849_);
return v___x_850_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___redArg___boxed(lean_object* v_X_851_, lean_object* v_tok_852_){
_start:
{
lean_object* v_res_853_; 
v_res_853_ = l_Polydim_Formal_entropy__deficit___redArg(v_X_851_, v_tok_852_);
lean_dec_ref(v_tok_852_);
lean_dec_ref(v_X_851_);
return v_res_853_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit(lean_object* v_D_854_, lean_object* v_X_855_, lean_object* v_tok_856_){
_start:
{
lean_object* v___x_857_; 
v___x_857_ = l_Polydim_Formal_entropy__deficit___redArg(v_X_855_, v_tok_856_);
return v___x_857_;
}
}
LEAN_EXPORT lean_object* l_Polydim_Formal_entropy__deficit___boxed(lean_object* v_D_858_, lean_object* v_X_859_, lean_object* v_tok_860_){
_start:
{
lean_object* v_res_861_; 
v_res_861_ = l_Polydim_Formal_entropy__deficit(v_D_858_, v_X_859_, v_tok_860_);
lean_dec_ref(v_tok_860_);
lean_dec_ref(v_X_859_);
lean_dec(v_D_858_);
return v_res_861_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_polydim__formal__core__theorems(uint8_t builtin) {
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
l_Polydim_Formal_Hypersphere_h__dim___autoParam = _init_l_Polydim_Formal_Hypersphere_h__dim___autoParam();
lean_mark_persistent(l_Polydim_Formal_Hypersphere_h__dim___autoParam);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
