define <8 x i32> @kernel(<4 x i32> %a, <4 x i32> %b) {
entry:
  %a0 = extractelement <4 x i32> %a, i32 0
  %a1 = extractelement <4 x i32> %a, i32 1
  %a2 = extractelement <4 x i32> %a, i32 2
  %a3 = extractelement <4 x i32> %a, i32 3
  %b0 = extractelement <4 x i32> %b, i32 0
  %b1 = extractelement <4 x i32> %b, i32 1
  %b2 = extractelement <4 x i32> %b, i32 2
  %b3 = extractelement <4 x i32> %b, i32 3
  %o0 = insertelement <8 x i32> poison, i32 %a0, i32 0
  %o1 = insertelement <8 x i32> %o0, i32 %b0, i32 1
  %o2 = insertelement <8 x i32> %o1, i32 %a1, i32 2
  %o3 = insertelement <8 x i32> %o2, i32 %b1, i32 3
  %o4 = insertelement <8 x i32> %o3, i32 %a2, i32 4
  %o5 = insertelement <8 x i32> %o4, i32 %b2, i32 5
  %o6 = insertelement <8 x i32> %o5, i32 %a3, i32 6
  %o7 = insertelement <8 x i32> %o6, i32 %b3, i32 7
  ret <8 x i32> %o7
}
