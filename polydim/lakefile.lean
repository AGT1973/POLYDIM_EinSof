import Lake
open Lake DSL

package «polydim» where
  version := v!"26.505.0"

@[default_target]
lean_lib «Polydim» where
  roots := #[`Core]
