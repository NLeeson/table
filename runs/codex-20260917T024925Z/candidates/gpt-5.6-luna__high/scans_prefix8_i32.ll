define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %s1 = shufflevector <8 x i32> %v, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %a = add <8 x i32> %v, %s1
  %s2 = shufflevector <8 x i32> %a, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %b = add <8 x i32> %a, %s2
  %s3 = shufflevector <8 x i32> %b, <8 x i32> zeroinitializer, <8 x i32> <i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4>
  %r = add <8 x i32> %b, %s3
  ret <8 x i32> %r
}
