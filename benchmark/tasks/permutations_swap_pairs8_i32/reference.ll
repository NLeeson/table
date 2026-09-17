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
  %o0 = insertelement <8 x i32> poison, i32 %v1, i32 0
  %o1 = insertelement <8 x i32> %o0, i32 %v0, i32 1
  %o2 = insertelement <8 x i32> %o1, i32 %v3, i32 2
  %o3 = insertelement <8 x i32> %o2, i32 %v2, i32 3
  %o4 = insertelement <8 x i32> %o3, i32 %v5, i32 4
  %o5 = insertelement <8 x i32> %o4, i32 %v4, i32 5
  %o6 = insertelement <8 x i32> %o5, i32 %v7, i32 6
  %o7 = insertelement <8 x i32> %o6, i32 %v6, i32 7
  ret <8 x i32> %o7
}
