define i32 @kernel(<8 x i32> %v) {
entry:
  %swap = shufflevector <8 x i32> %v, <8 x i32> %v, <8 x i32> <i32 1, i32 0, i32 3, i32 2, i32 5, i32 4, i32 7, i32 6>
  %pair = add <8 x i32> %v, %swap
  %swap2 = shufflevector <8 x i32> %pair, <8 x i32> %pair, <8 x i32> <i32 2, i32 3, i32 0, i32 1, i32 6, i32 7, i32 4, i32 5>
  %quad = add <8 x i32> %pair, %swap2
  %swap4 = shufflevector <8 x i32> %quad, <8 x i32> %quad, <8 x i32> <i32 4, i32 5, i32 6, i32 7, i32 0, i32 1, i32 2, i32 3>
  %total = add <8 x i32> %quad, %swap4
  %sum = extractelement <8 x i32> %total, i32 0
  ret i32 %sum
}
