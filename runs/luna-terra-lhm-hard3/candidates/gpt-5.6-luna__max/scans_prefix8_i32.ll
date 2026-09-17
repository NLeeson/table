define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %sh1 = shufflevector <8 x i32> %v, <8 x i32> poison, <8 x i32> <i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %a1 = add <8 x i32> %v, %sh1
  %s1 = select <8 x i1> <i1 true, i1 false, i1 false, i1 false, i1 false, i1 false, i1 false, i1 false>, <8 x i32> %v, <8 x i32> %a1
  %sh2 = shufflevector <8 x i32> %s1, <8 x i32> poison, <8 x i32> <i32 8, i32 8, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %a2 = add <8 x i32> %s1, %sh2
  %s2 = select <8 x i1> <i1 true, i1 true, i1 false, i1 false, i1 false, i1 false, i1 false, i1 false>, <8 x i32> %s1, <8 x i32> %a2
  %sh4 = shufflevector <8 x i32> %s2, <8 x i32> poison, <8 x i32> <i32 8, i32 8, i32 8, i32 8, i32 0, i32 1, i32 2, i32 3>
  %a4 = add <8 x i32> %s2, %sh4
  %result = select <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 false, i1 false, i1 false, i1 false>, <8 x i32> %s2, <8 x i32> %a4
  ret <8 x i32> %result
}
