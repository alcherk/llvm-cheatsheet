# LLVM cheatsheet

## Tools

- `llvm-as`:   `.ll` to `.bc`
- `llvm-dis`:  `.bc` to `.ll`
- `lli`:       Interpret `.ll`
- `llc`:       `.ll` or `.bc` to `.s`
- `llvm-link`: link multiple `.ll` or `.bc`
- `opt`:       Optimizer.

Syntax highlights: *llvm/utils/$YOUR_FAVORATE_EDITOR*

## Intermediate Representation

3 forms: text(`.ll`), bitcode(`.bc`), C++ objects

LangRef: [http://llvm.org/docs/LangRef.html](http://llvm.org/docs/LangRef.html)

### Comments

    %result = mul i32 %x, 8    ; this is a comment

### Identifiers

- Local: `%foo`, `%42`
- Global: `@bar`, `@43`
- Constants: (see below)

### Types

- primitive:
    - Integer: `i1`, `i2`, `i3`, ... `i8`, ... `i16`, ... `i32`, ... `i64`, ...
    - Floating point: `half`, `float`, `double`, `x86_fp80`, `fp128`, `ppc_fp128`
    - X86mmx: `x86mmx`
    - Misc: `void`, `label`, `metadata`
- derived:
    - Array:
        - `[<# elements> x <elementtype>]`
        - e.g. `[40 x i32]`, `[3 x [4 x float]]`
    - Structure:
        - `%T1 = type { <type list> }     ; normal`
        - `%T2 = type <{ <type list> }>   ; packed`
        - e.g. `{ i32, i32, i32 }`, `{ float, i32 (i32) * }`, `<{ i8, i32 }>`
    - Opaque structure:
        - `%X = type opaque`
    - Pointer: 
        - `<type> *`
        - e.g. `i32*`, `i32**`, `[4 x i32]*`, `i32 (i32*) *`, `i32 addrspace(5)*`
    - Vector (for SIMD):
        - `< <# elements> x <elementtype> >`
        - e.g. `<4 x i32>`
    - Function:
        - `<returntype> (<parameter list>)`
        - e.g. `i32 (i32)`, `i32 (i8*, ...)`, `{i32, i32} (i32)`
        - e.g. `float (i16, i32*) *` (**pointer** to a function)

### Constants (literals)
- Boolean: `true`, `false` (`i1` type)
- Integer: `1`, `42`, `-3`, ...
- Floating point: `123.421`, `1.23421e+2`, `1.0`
    - **NOT** `1.3` (not exact binary)
- Pointer: `null`
- Structure: `{ i32 4, float 17.0, i32* @G }`
    - in this example `@G = external global i32`.
- Array: `[ i32 42, i32 11, i32 74 ]` (type is [3 x i32])
    - Number of items is significant.
- Vector: `< i32 42, i32 11, i32 74, i32 100 >`
    - Number of items is significant.
- Zero initialization: `zeroinitializer`
- Metadata node: `metadata !{ i32 0, metadata !"test" }`
- Global variable: `@X`, `@y`, `@func`
- Undefined value: `undef`

### Global variables

Addresses are (link-time) constants. Identifiers have **pointer** type.

    @X = global i32 17
    @Y = global i32 42
    @Z = global [2 x i32*] [ i32* @X, i32* @Y ]

### Binary Operators

- int:     `add` `sub` `mul` `udiv` `sdiv` `urem` `srem`
- float:   `fadd` `fsub` `fmul` `fdiv` `frem`
- bitwise: `shl` `lshr` `ashr` `and` `or` `xor`

`u`=unsigned, `s`=signed
`l`=logical, `a`=arithmetic
`i`=int, `f`=float

    %b = add i32 %a, 42      ; int b = a + 42;

### Control Flow

- compare: `icmp` `fcmp`
    - `icmp <cond> <ty> <op1>, <op2>`
    - `<cond>` ::= `eq` `ne` `ugt` `uge` `ult` `ule` `sgt` `sge` `slt` `sle`
- branch: `br`
    - `br i1 <cond>, label <iftrue>, label <iffalse>`
    - `br label <dest>          ; Unconditional branch`
- merge: `phi`
    - `<result> = phi <ty> [ <val0>, <label0>], ...`

<!-- Disambiguous markdown -->

    entry:
      %c = icmp eq i32 %a, %b
      br i1 %c, label %equal, label %not_equal
    equal:
      %d1 = add i32 %a, %b
      br label %exit
    not_equal:
      %d2 = sub i32 %a, %b
      br label %exit
    exit:
      %d = phi i32 [%d1, %equal], [%d2, %not_equal]

- multi-branch: `switch`
    - `switch <intty> <value>, label <defaultdest> [ <intty> <val>, label <dest> ... ]`

<!-- Disambiguous markdown -->

    switch i32 %a, label %default, [
        i32 2, label %place1
        i32 3, label %place2
        i32 5, label %place3
        ]

- `select`
    - `<result> = select <selty> <cond>, <ty> <val1>, <ty> <val2>`
    - `<selty>` ::= `i1` or `{<N x i1>}`

<!-- Disambiguous markdown -->

    %cond = icmp slt i32 %a, %b
    %small = select i1 %cond, i32 %a, i32 %b
    
### Function

Define/declare a function:

    declare i32 @printf(i8*, ...)
    
    define i32 @main(i32 %argc, i8** %argv) {
      ret i32 0
    }

*Note: functions names are global constants.*
    
- Return from a function: `ret`
    - `ret <ty> <value>`
    - `ret void`

### Memory

- Stack allocation: `alloca`
    - `<result> = alloca <type>[, <ty> <NumElements>][, align <alignment>]`
    - yields: `{type*}:result`
- Register to memory: `load`
    - `<result> = load [volatile] <ty>* <pointer>[, align <alignment>][, !nontemporal !<index>][, !invariant.load !<index>]`
    - `<result> = load atomic [volatile] <ty>* <pointer> [singlethread] <ordering>, align <alignment>`
    - `!<index>` ::= `!{ i32 1 }`
- Memory to register: `store`
    - `store [volatile] <ty> <value>, <ty>* <pointer>[, align <alignment>][, !nontemporal !<index>]`
    - `store atomic [volatile] <ty> <value>, <ty>* <pointer> [singlethread] <ordering>, align <alignment>`

<!-- Disambiguous markdown -->
    
    %ptr = alloca i32       ; yields {i32*}:ptr
    store i32 3, i32* %ptr  ; yields {void}
    %val = load i32* %ptr   ; yields {i32}:val = i32 3
    

