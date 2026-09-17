define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %s1 = shufflevector <8 x i32> zeroinitializer, <8 x i32> %v, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %p1 = add <8 x i32> %v, %s1
  %s2 = shufflevector <8 x i32> zeroinitializer, <8 x i32> %p1, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %p2 = add <8 x i32> %p1, %s2
  %s4 = shufflevector <8 x i32> zeroinitializer, <8 x i32> %p2, <8 x i32> <i32 8, i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3>
  %p4 = add <8 x i32> %p2, %s4
  ret <8 x i32> %p4
}
