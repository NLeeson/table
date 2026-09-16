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
  %s012 = add i32 %s01, %v2
  %s0123 = add i32 %s012, %v3
  %s01234 = add i32 %s0123, %v4
  %s012345 = add i32 %s01234, %v5
  %s0123456 = add i32 %s012345, %v6
  %sum = add i32 %s0123456, %v7
  ret i32 %sum
}
