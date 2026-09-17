define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %v0 = extractelement <8 x i32> %v, i32 0
  %v1 = extractelement <8 x i32> %v, i32 1
  %v2 = extractelement <8 x i32> %v, i32 2
  %v3 = extractelement <8 x i32> %v, i32 3
  %v4 = extractelement <8 x i32> %v, i32 4
  %v5 = extractelement <8 x i32> %v, i32 5
  %v6 = extractelement <8 x i32> %v, i32 6
  %v7 = extractelement <8 x i32> %v, i32 7
  %p1 = xor i32 %v0, %v1
  %p2 = xor i32 %p1, %v2
  %p3 = xor i32 %p2, %v3
  %p4 = xor i32 %p3, %v4
  %p5 = xor i32 %p4, %v5
  %p6 = xor i32 %p5, %v6
  %p7 = xor i32 %p6, %v7
  %o0 = insertelement <8 x i32> poison, i32 %v0, i32 0
  %o1 = insertelement <8 x i32> %o0, i32 %p1, i32 1
  %o2 = insertelement <8 x i32> %o1, i32 %p2, i32 2
  %o3 = insertelement <8 x i32> %o2, i32 %p3, i32 3
  %o4 = insertelement <8 x i32> %o3, i32 %p4, i32 4
  %o5 = insertelement <8 x i32> %o4, i32 %p5, i32 5
  %o6 = insertelement <8 x i32> %o5, i32 %p6, i32 6
  %o7 = insertelement <8 x i32> %o6, i32 %p7, i32 7
  ret <8 x i32> %o7
}
