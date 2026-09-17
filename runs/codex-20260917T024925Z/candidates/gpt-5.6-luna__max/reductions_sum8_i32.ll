define i32 @kernel(<8 x i32> %v) {
entry:
  %p = shufflevector <8 x i32> %v, <8 x i32> %v, <8 x i32> <i32 1, i32 0, i32 3, i32 2, i32 5, i32 4, i32 7, i32 6>
  %s = add <8 x i32> %v, %p
  %q = shufflevector <8 x i32> %s, <8 x i32> %s, <8 x i32> <i32 2, i32 3, i32 0, i32 1, i32 6, i32 7, i32 4, i32 5>
  %t = add <8 x i32> %s, %q
  %r = shufflevector <8 x i32> %t, <8 x i32> %t, <8 x i32> <i32 4, i32 5, i32 6, i32 7, i32 0, i32 1, i32 2, i32 3>
  %u = add <8 x i32> %t, %r
  %sum = extractelement <8 x i32> %u, i32 0
  ret i32 %sum
}
