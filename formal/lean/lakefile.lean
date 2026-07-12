import Lake
open Lake DSL

package Theorems where

@[default_target]
lean_lib Core where
  srcDir := "."

@[default_target]
lean_lib Theorems where
  srcDir := "."
