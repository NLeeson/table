define i32 @kernel(<8 x i32> %v) {
entry:
  %v0 = extractelement <8 x i32> %v, i32 0
  %v1 = extractelement <8 x i32> %v, i32 1
  %v2 = extractelement <8 x i32> %v, i32 2
  %v3 = extractelement <8 x i32> %v, i32 3
  %v4 = extractelement <8 x i32> %v, i32 4
  %v5 = extractelement <8 x i32> %v, i32 5
  %v6 = extractelement <8 x i32> %v, i32 6
  %v7 = extractelement <8 x i32> %v, i32 7
  %s01 = add i32 %v0, %v1
  %s23 = add i32 %v2, %v3
  %s45 = add i32 %v4, %v5
  %s67 = add i32 %v6, %v7
  %s0123 = add i32 %s01, %s23
  %s4567 = add i32 %s45, %s67
  %sum = add i32 %s0123, %s4567
  ret i32 %sum
}
