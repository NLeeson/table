define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %s1v = shufflevector <8 x i32> %v, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %s1 = add <8 x i32> %v, %s1v
  %s2v = shufflevector <8 x i32> %s1, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %s2 = add <8 x i32> %s1, %s2v
  %s4v = shufflevector <8 x i32> %s2, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3>
  %s4 = add <8 x i32> %s2, %s4v
  ret <8 x i32> %s4
}
