define i32 @kernel(<8 x i32> %v) {
entry:
  %swap4 = shufflevector <8 x i32> %v, <8 x i32> poison, <8 x i32> <i32 4, i32 5, i32 6, i32 7, i32 0, i32 1, i32 2, i32 3>
  %sum4 = add <8 x i32> %v, %swap4
  %swap2 = shufflevector <8 x i32> %sum4, <8 x i32> poison, <8 x i32> <i32 2, i32 3, i32 0, i32 1, i32 6, i32 7, i32 4, i32 5>
  %sum2 = add <8 x i32> %sum4, %swap2
  %swap1 = shufflevector <8 x i32> %sum2, <8 x i32> poison, <8 x i32> <i32 1, i32 0, i32 3, i32 2, i32 5, i32 4, i32 7, i32 6>
  %sum1 = add <8 x i32> %sum2, %swap1
  %result = extractelement <8 x i32> %sum1, i32 0
  ret i32 %result
}
