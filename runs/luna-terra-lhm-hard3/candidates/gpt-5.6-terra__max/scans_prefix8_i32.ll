define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %shift1 = shufflevector <8 x i32> %v, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %sum1 = add <8 x i32> %v, %shift1
  %shift2 = shufflevector <8 x i32> %sum1, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %sum2 = add <8 x i32> %sum1, %shift2
  %shift4 = shufflevector <8 x i32> %sum2, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3>
  %sum4 = add <8 x i32> %sum2, %shift4
  ret <8 x i32> %sum4
}
