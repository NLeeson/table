define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %s1 = shufflevector <8 x i32> %v, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %a1 = add <8 x i32> %v, %s1
  %s2 = shufflevector <8 x i32> %a1, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %a2 = add <8 x i32> %a1, %s2
  %s4 = shufflevector <8 x i32> %a2, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3>
  %r = add <8 x i32> %a2, %s4
  ret <8 x i32> %r
}
