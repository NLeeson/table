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
  %a0 = add i32 %v0, %v1
  %a1 = add i32 %v2, %v3
  %a2 = add i32 %v4, %v5
  %a3 = add i32 %v6, %v7
  %b0 = add i32 %a0, %a1
  %b1 = add i32 %a2, %a3
  %sum = add i32 %b0, %b1
  ret i32 %sum
}
