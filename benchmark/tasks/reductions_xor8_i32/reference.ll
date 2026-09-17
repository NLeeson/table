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
  %r1 = xor i32 %v0, %v1
  %r2 = xor i32 %r1, %v2
  %r3 = xor i32 %r2, %v3
  %r4 = xor i32 %r3, %v4
  %r5 = xor i32 %r4, %v5
  %r6 = xor i32 %r5, %v6
  %r7 = xor i32 %r6, %v7
  ret i32 %r7
}
